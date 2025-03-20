from core_pro import DataPipeLine
from core_pro.ultilities import make_sync_folder

query = f"""
select
    item_id
    ,i.item_name
    ,i.shop_id
    ,array_agg(distinct i.model_name) model_name
from
    mp_item.dim_model__vn_s0_live i
where
    grass_date = current_date - interval '1' day
    and is_cb_shop = 0
    and item_status = 1
--     and shop_id = 851157471
group by 1, 2, 3
limit
    200000
"""
path = make_sync_folder('nlp/ner')
df = DataPipeLine(query).run_presto_to_df(save_path=path / 'ner_quantity.parquet')
