import re
from tqdm.auto import tqdm
import torch
from torch.utils.data import Dataset
from pathlib import Path
import pickle


def save_pickle(file_path: Path, lst: list):
    with open(file_path, "wb") as fp:
        pickle.dump(lst, fp)

def load_pickle(file_path: Path):
    with open(file_path, "rb") as fp:  # Unpickling
        b = pickle.load(fp)
    return b


def find_keyword_position(text: str, keyword: str) -> list:
    """
    Find the start and end index of a keyword in text using regex.

    Args:
        text (str): The text to search in
        keyword (str): The keyword to find

    Returns:
        list of tuples: A list of (start, end) index positions for all matches
    """
    # Escape special regex characters in the keyword
    escaped_keyword = re.escape(keyword)

    # Find all matches of the keyword
    matches = list(re.finditer(escaped_keyword, text))

    # Return list of (start, end) tuples
    return [(match.start(), match.end()) for match in matches]


def find_keyword_pipeline(items: list, keywords: list) -> list:
    lst_position = []
    for i, k in tqdm(zip(items, keywords), total=len(items), desc='Finding position'):
        positions = find_keyword_position(i, k)
        if positions:
            lst_position.append(positions)
        else:
            lst_position.append(None)
    return lst_position


def extract_tokens_bio(text, keywords_dict):
    # Convert text to lowercase for case-insensitive matching
    lower_text = text.lower()

    # Split the text into tokens
    tokens = text.split()

    # Initialize BIO tags
    bio_tags = ['O'] * len(tokens)

    # Check for keywords
    for keyword, token_type in keywords_dict.items():
        lower_keyword = keyword.lower()

        # Find all occurrences of the keyword in the text
        start_index = lower_text.find(lower_keyword)
        while start_index != -1:
            # Split the text to find token indices
            keyword_tokens = keyword.split()

            # Find the matching tokens in the original text
            for i in range(len(tokens)):
                if lower_text[start_index:start_index + len(keyword)].strip() == lower_text[lower_text.find(
                        tokens[i].lower()):lower_text.find(tokens[i].lower()) + len(keyword)].strip():
                    # Tag the first token as B- (Beginning)
                    bio_tags[i] = f'B-{token_type}'

                    # Tag subsequent tokens as I- (Inside)
                    for j in range(1, len(keyword_tokens)):
                        if i + j < len(bio_tags):
                            bio_tags[i + j] = f'I-{token_type}'
                    break

            # Find next occurrence
            start_index = lower_text.find(lower_keyword, start_index + 1)

    # Combine tokens with their BIO tags
    result = list(zip(tokens, bio_tags))
    return result, tokens, bio_tags


def clean_label(example):
    return {
        'tokens': [i[0] for i in example['bio_label']],
        'labels': [i[1] for i in example['bio_label']],
    }


def convert_examples_to_features(
    examples,
    max_seq_len: int ,
    tokenizer,
    pad_label_id: int = -100,
    cls_token_segment_id: int = 0,
    pad_token_segment_id: int = 0,
    sequence_segment_id: int = 0,
    mask_padding_with_zero: bool = True,
    label_map: dict = None,
):
    # Get special tokens from the tokenizer
    cls_token = tokenizer.cls_token
    sep_token = tokenizer.sep_token
    unk_token = tokenizer.unk_token
    pad_token_id = tokenizer.pad_token_id

    # List to hold the converted features
    features = []

    for example in tqdm(examples):
        # Tokenize each word and align its corresponding label
        tokens = []
        label_ids = []

        for word, label in zip(example['tokens'], example['labels']):
            word_tokens = tokenizer.tokenize(word)

            # If the word cannot be tokenized, use [UNK] token
            if not word_tokens:
                word_tokens = [unk_token]

            tokens.extend(word_tokens)

            # Map string label to integer ID, apply pad_label_id for subword tokens
            label_id = label_map[label]
            label_ids.extend([label_id] + [pad_label_id] * (len(word_tokens) - 1))

        # Handle sequence truncation for [CLS] and [SEP] tokens
        special_tokens_count = 2
        if len(tokens) > max_seq_len - special_tokens_count:
            tokens = tokens[:max_seq_len - special_tokens_count]
            label_ids = label_ids[:max_seq_len - special_tokens_count]

        # Add [SEP] token at the end of the sentence
        tokens.append(sep_token)
        label_ids.append(pad_label_id)
        token_type_ids = [sequence_segment_id] * len(tokens)

        # Add [CLS] token at the start of the sentence
        tokens = [cls_token] + tokens
        label_ids = [pad_label_id] + label_ids
        token_type_ids = [cls_token_segment_id] + token_type_ids

        # Convert tokens to input IDs
        input_ids = tokenizer.convert_tokens_to_ids(tokens)

        # Create attention masks (1 for real tokens, 0 for padding tokens)
        attention_mask = [1 if mask_padding_with_zero else 0] * len(input_ids)


        # Pad sequences to the maximum sequence length
        padding_length = max_seq_len - len(input_ids)
        input_ids += [pad_token_id] * padding_length
        attention_mask += [0 if mask_padding_with_zero else 1] * padding_length
        token_type_ids += [pad_token_segment_id] * padding_length
        label_ids += [pad_label_id] * padding_length

        features.append(
            dict(
                input_ids=input_ids,
                attention_mask=attention_mask,
                token_type_ids=token_type_ids,
                slot_labels_ids=label_ids,
            )
        )

    return features


class NERDataset(Dataset):
    def __init__(self, features):
        self.features = features

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        feature = self.features[idx]
        return {
            'input_ids': torch.tensor(feature['input_ids'], dtype=torch.long),
            'attention_mask': torch.tensor(feature['attention_mask'], dtype=torch.long),
            'token_type_ids': torch.tensor(feature['token_type_ids'], dtype=torch.long),
            'labels': torch.tensor(feature['slot_labels_ids'], dtype=torch.long),
        }


def group_ner_tags(ner_tags):
    grouped_entities = []
    current_entity = None

    for tag in ner_tags:
        # Check if it's a beginning of a new entity
        if tag['entity_group'].startswith('B-'):
            # If there's a previous entity, add it to the list
            if current_entity:
                grouped_entities.append(current_entity)

            # Start a new entity
            current_entity = {
                'entity_type': tag['entity_group'][2:],
                'tokens': [tag['token']],
                'word': [tag['word']],
                'scores': [tag['score']]
            }

        # Check if it's a continuation of the previous entity
        elif tag['entity_group'].startswith('I-'):
            # Ensure the entity type matches the current entity
            if current_entity and tag['entity_group'][2:] == current_entity['entity_type']:
                current_entity['tokens'].append(tag['token'])
                current_entity['scores'].append(tag['score'])
                current_entity['word'].append(tag['word'])
            else:
                # If no matching current entity, start a new one
                if current_entity:
                    grouped_entities.append(current_entity)

                current_entity = {
                    'entity_type': tag['entity_group'][2:],
                    'tokens': [tag['token']],
                    'word': [tag['word']],
                    'scores': [tag['score']]
                }

    # Add the last entity if exists
    if current_entity:
        grouped_entities.append(current_entity)

    return grouped_entities
