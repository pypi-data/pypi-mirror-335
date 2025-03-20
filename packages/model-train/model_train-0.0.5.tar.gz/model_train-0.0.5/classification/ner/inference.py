from pathlib import Path
from func import load_pickle, group_ner_tags
from core_pro.ultilities import make_sync_folder
from transformers import pipeline
import polars as pl
from pattern import label_map, id2label
from transformers import RobertaTokenizerFast
from rich import print


path = make_sync_folder('nlp/ner')
file = path / 'raw/tag_ner_bio.parquet'
df = pl.read_parquet(file).sample(1000)

# init
tokenizer = RobertaTokenizerFast.from_pretrained('roberta-base', add_prefix_space=True)
folder = Path('/media/kevin/data_4t/nlp/ner/model/roberta-base')
classify = pipeline(
    task="ner",
    model=str(folder),
    batch_size=100,
    tokenizer=tokenizer,
    aggregation_strategy="max"
)

sample = df['item_name'][:5].to_list()
result = classify(sample)

lst_final = []
for r, s in zip(result, sample):
    lst = []
    for pred in r:
        entity = int(pred['entity_group'].split('_')[1])
        score = round(pred['score'].item(), 3)
        if id2label.get(entity) != 'O':
            dict_ = {
                'entity_group': id2label.get(entity),
                'score': score,
                'token': s[pred['start']:pred['end']],
                'word': pred['word'],
            }
            lst.append(dict_)
    group_lst = group_ner_tags(lst)
    final_result = {'text': s, 'ner': group_lst}
    lst_final.append(final_result)
print(lst_final)
