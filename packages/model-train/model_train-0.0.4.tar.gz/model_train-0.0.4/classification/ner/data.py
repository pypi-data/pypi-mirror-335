from core_pro import DataPipeLine
import pandas as pd
from core_pro.ultilities import make_sync_folder


query = f"""
select
    item_id
    ,i.name item_name
    ,level1_global_be_category
    ,level2_global_be_category
    ,level3_global_be_category
    ,level4_global_be_category
    ,level5_global_be_category
    ,global_brand_details.local_name brand_name
    ,t1.name attribute_name
    ,t2.value attribute_value
from
    mp_item.dim_item__vn_s0_live i
    cross join unnest (i.global_attribute_details.seller_input) as t1
    cross join unnest (t1.value_multi_lang_values) as t2
where
    grass_date = current_date - interval '1' day
    and global_attribute_details is not null
    and is_cb_shop = 0
    and status = 1
    and t2.lang = 'vn'
    and lower(t2.value) not in ('có', 'không', 'khác', '', ' ', 'đúng')
    and regexp_like(i.name, t2.value)
limit 2000000
"""
df = DataPipeLine(query).run_presto_to_df()

if not isinstance(df, pd.DataFrame):
    df = df.to_pandas()

path = make_sync_folder('nlp/ner')
df.to_parquet(path / 'tag_ner.parquet', index=False, compression='zstd')
