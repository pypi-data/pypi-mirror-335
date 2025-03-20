from core_pro.ultilities import make_sync_folder
from datasets import Dataset
import polars as pl
from sklearn.model_selection import train_test_split
from rich import print
from pattern import label_map, label_list
from transformers import Trainer
from seqeval.metrics import classification_report, f1_score, precision_score, recall_score
from transformers import EvalPrediction
from func import clean_label, convert_examples_to_features, NERDataset, save_pickle, load_pickle
from transformers import RobertaTokenizerFast, RobertaForTokenClassification, TrainingArguments
import torch
import gc


# config
path = make_sync_folder('nlp/ner')
pretrain = 'roberta-base'

# data
file = path / 'raw/tag_ner_bio.parquet'
df = pl.read_parquet(file)
print(f'Data shape: {df.shape}, Total items: {df['item_id'].n_unique():,.0f}')

# split
col = ['item_id', 'item_name', 'bio_label']
train, test = train_test_split(df.select(col), test_size=.2, random_state=42)
train, valid = train_test_split(train, test_size=.2, random_state=42)
del df

# dataset

file_name_train = path / 'ds/ds_train.pkl'
file_name_val = path / 'ds/ds_valid.pkl'
file_name_test = path / 'ds/ds_test.pkl'
tokenizer = RobertaTokenizerFast.from_pretrained('roberta-base', add_prefix_space=True)
if not file_name_train.exists():
    print(f'Create dataset to train: Loading')
    # to dataset
    ds_train = Dataset.from_polars(train)
    ds_train = ds_train.map(clean_label, remove_columns=['bio_label'])
    ds_valid = Dataset.from_polars(valid)
    ds_valid = ds_valid.map(clean_label, remove_columns=['bio_label'])
    ds_test = Dataset.from_polars(test)
    ds_test = ds_test.map(clean_label, remove_columns=['bio_label'])

    max_seq_len = 60
    train_features = convert_examples_to_features(
        examples=ds_train,
        max_seq_len=max_seq_len,
        tokenizer=tokenizer,
        label_map=label_map,
    )
    valid_features = convert_examples_to_features(
        examples=ds_valid,
        max_seq_len=max_seq_len,
        tokenizer=tokenizer,
        label_map=label_map,
    )
    test_features = convert_examples_to_features(
        examples=ds_test,
        max_seq_len=max_seq_len,
        tokenizer=tokenizer,
        label_map=label_map,
    )
    ds_test.save_to_disk(path / 'ds/test')
    save_pickle(file_name_train, train_features)
    save_pickle(file_name_val, valid_features)
    save_pickle(file_name_test, test_features)
else:
    print(f'Create dataset to train: Dataset is already loaded')
    train_features = load_pickle(file_name_train)
    valid_features = load_pickle(file_name_val)
    test_features = load_pickle(file_name_test)

train_dataset = NERDataset(train_features)
valid_dataset = NERDataset(valid_features)
test_dataset = NERDataset(test_features)

# model
num_labels = len(label_list)
model = RobertaForTokenClassification.from_pretrained(pretrain, num_labels=num_labels)

log_step = 5000
folder = str(path / f'model/{pretrain}')
# Define training arguments
training_args = TrainingArguments(
    output_dir=folder,
    warmup_ratio=0.1,
    lr_scheduler_type='cosine',
    weight_decay=0.001,
    learning_rate=1e-4,
    per_device_train_batch_size=128,
    per_device_eval_batch_size=16,
    fp16=True,
    logging_strategy='steps',
    save_strategy='steps',
    eval_strategy='steps',
    save_steps=log_step,
    eval_steps=log_step,
    logging_steps=log_step,
    save_total_limit=2,
    load_best_model_at_end=True,
    metric_for_best_model='f1',
    report_to="none",
    num_train_epochs=3,
    optim='adafactor',
)

def compute_metrics(p: EvalPrediction):
    predictions = p.predictions.argmax(axis=2)  # Get predicted label indices
    labels = p.label_ids  # True label IDs

    pred_labels = []
    true_labels = []

    for i, (pred_seq, true_seq) in enumerate(zip(predictions, labels)):
        pred_label_seq = []
        true_label_seq = []

        for pred_idx, true_idx in zip(pred_seq, true_seq):
            if true_idx == -100:
                # Debugging: Log any padding tokens encountered
                # print(f"Padding token encountered at position {i}")
                continue

            # Check if the indices are within the valid range
            if pred_idx < len(label_list) and true_idx < len(label_list):
                pred_label_seq.append(label_list[pred_idx])
                true_label_seq.append(label_list[true_idx])
            else:
                # Debugging: Log when out-of-bound indices are encountered
                print(f"Index out of range: pred_idx={pred_idx}, true_idx={true_idx} at position {i}")

        pred_labels.append(pred_label_seq)
        true_labels.append(true_label_seq)

    # Compute token-level F1, Precision, and Recall
    precision = precision_score(true_labels, pred_labels)
    recall = recall_score(true_labels, pred_labels)
    f1 = f1_score(true_labels, pred_labels)

    print("Classification Report:")
    print(classification_report(true_labels, pred_labels))

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


# Initialize the Trainer with the modified compute_metrics function
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=valid_dataset,
    processing_class=tokenizer,
    compute_metrics=compute_metrics  # Updated function
)

# Train the model
train_results = trainer.train()
trainer.save_model()
trainer.log_metrics("train", train_results.metrics)
trainer.save_metrics("train", train_results.metrics)
trainer.save_state()

torch.cuda.empty_cache()
gc.collect()
