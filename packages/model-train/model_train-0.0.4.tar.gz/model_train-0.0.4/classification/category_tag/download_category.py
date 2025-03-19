from core_pro import DataPipeLine
from core_pro.ultilities import make_sync_folder


query = f"""
select
    i.level1_global_be_category
    ,i.level2_global_be_category
    ,i.level3_global_be_category
    ,count(distinct item_id) total_item
    ,count(distinct shop_id) total_shop
from
    mp_order.dwd_order_item_all_ent_df__vn_s0_live i
where
    date(i.create_datetime) >= current_date - interval '365' day
    and is_cb_shop = 0
    and is_net_order = 1
group by 1, 2, 3
order by 1, 2
"""

# file
path = make_sync_folder('dataset/category_tag')
file_name = path / f'cat.parquet'
df = DataPipeLine(query).run_presto_to_df(save_path=file_name, overwrite=True)
