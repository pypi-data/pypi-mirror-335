import duckdb
import polars as pl
from rich import print
from core_pro.ultilities import make_sync_folder
from pyvi import ViTokenizer
from tqdm.auto import tqdm


path = make_sync_folder('dataset/category_tag')

query = f"""
select *
, concat_ws(' >> ', level1_global_be_category, level2_global_be_category) as label
from read_parquet('{path / 'l12/*.parquet'}')
"""
df = duckdb.sql(query).pl()

label = 'label'
item_multil_label = df.group_by(['item_name']).agg(pl.col(label).n_unique()).filter(pl.col(label) > 1)
dup_item = len(item_multil_label)

df = df.unique(subset=['item_name'])
total_item = df['item_name'].n_unique()
print(
    f'Data shape: {df.shape}, Total item: {total_item}\n'
    f'Item multil label: {dup_item:,.0f} - {dup_item / total_item:,.5f}%'
)

lst = [ViTokenizer.tokenize(i) for i in tqdm(df['item_name'])]
df = df.with_columns(pl.Series('word', lst))
df.write_parquet(path / 'clean.parquet')
