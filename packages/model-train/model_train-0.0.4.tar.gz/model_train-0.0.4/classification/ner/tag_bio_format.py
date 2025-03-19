import polars as pl
from core_pro.ultilities import make_sync_folder
from rich import print
import re
from tqdm.auto import tqdm
from func import find_keyword_pipeline, extract_tokens_bio
from pattern import pattern, label2id


# config
path = make_sync_folder('nlp/ner')

# data clean
file_name = path / 'raw/tag_ner_clean.parquet'
rerun = False
if rerun:
    # load data
    df = (
        pl.read_parquet(path / 'raw/tag_ner.parquet')
        .with_columns(pl.col('brand_name').fill_null('No brand'))
    )
    print(f'Data shape: {df.shape}, Total items: {df['item_id'].n_unique():,.0f}')

    # check position
    item = df['item_name'].str.to_lowercase()
    keyword = df['attribute_value'].fill_null('None').str.to_lowercase()
    lst_position = find_keyword_pipeline(item, keyword)

    item = df['item_name'].str.to_lowercase()
    keyword = df['brand_name'].str.to_lowercase()
    lst_brand= find_keyword_pipeline(item, keyword)

    df = df.with_columns(
        pl.Series('position_value', lst_position),
        pl.Series('position_brand', lst_brand),
    )

    # check ner
    df_not_found = df.filter(pl.col('position_value').is_null())
    print(f'Not Found NER: {df_not_found.shape[0]}')
    df = df.filter(~pl.col('position_value').is_null())

    # group ner into patterns
    lst = ['SKU' if re.findall(r'\d+', text) else None for text in df['attribute_value']]
    lst = ['SKU' if l else n for l, n in zip(lst, df['attribute_name'])]
    for p in tqdm(pattern, desc='Group attributes into patterns'):
        k, v = list(p.items())[0]
        for token in k.split():
            set_token = {token}
            lst = [v if set_token.intersection(text.split()) else text for text in lst]
    df = df.with_columns(pl.Series('attribute_name_patterns', lst))

    # export
    df.write_parquet(file_name)
else:
    df = pl.read_parquet(file_name)

# load data
print(f'Data shape: {df.shape}, Total items: {df['item_id'].n_unique():,.0f}')

# filter ner
patterns_list = set([list(i.values())[0] for i in pattern])
df = df.filter(pl.col('attribute_name_patterns').is_in(patterns_list))
value_count = (
    df['attribute_name_patterns'].value_counts()
    .with_columns((pl.col('count') / df.shape[0]).round(3).alias('count_pct'))
    .sort('count', descending=True)
)
print(value_count)

# bio format
df_ner_group = df.group_by(['item_id', 'item_name']).agg(
    pl.struct('attribute_value', 'attribute_name_patterns').alias('attribute'),
)

col = ['item_id', 'item_name', 'attribute']
ner_bio_lst, token_lst, bio_tag_list, id_bio = [], [], [], []
for idx, name, att in tqdm(df_ner_group[col].to_numpy().tolist(), desc='Post process'):
    keywords_dict = {a[0].lower(): a[1] for a in att}
    ner_bio, tokens, bio_tag = extract_tokens_bio(name, keywords_dict)
    ner_bio_lst.append(ner_bio)
    token_lst.append(tokens)
    bio_tag_list.append(bio_tag)
    id_bio.append([label2id.get(i) for i in bio_tag])
    # break

df_ner_group = df_ner_group.with_columns(
    pl.Series('tokens', token_lst),
    pl.Series('ner_tag', bio_tag_list),
    pl.Series('ner_id', id_bio),
)
df_ner_group.write_parquet(path / 'raw/tag_ner_bio.parquet')
