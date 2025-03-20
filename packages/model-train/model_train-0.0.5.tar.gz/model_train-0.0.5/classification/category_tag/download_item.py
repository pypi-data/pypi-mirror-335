from core_pro import DataPipeLine
from core_pro.ultilities import make_sync_folder
import duckdb
from concurrent.futures import ThreadPoolExecutor
from rich import print
from re import sub


# category
path = make_sync_folder('dataset/category_tag')
query = f"""
select level1_global_be_category
, level2_global_be_category
, sum(total_item) total_item
from read_parquet('{path / 'cat.parquet'}')
group by 1, 2
"""
df_cat = duckdb.sql(query).pl().to_dicts()
print(f'Total items: {len(df_cat)}')

# download
def download(arr):
    l1, l2, limit = arr['level1_global_be_category'], arr['level2_global_be_category'], arr['total_item']
    limit = min(limit, 30_000)
    query = f"""
    select
        item_id
        ,item_name
        ,level1_global_be_category
        ,level2_global_be_category
        ,count(distinct item_id) total_item
        ,count(distinct shop_id) total_shop
    from
        mp_order.dwd_order_item_all_ent_df__vn_s0_live
    where
        date(create_datetime) >= current_date - interval '365' day
        and is_cb_shop = 0
        and is_net_order = 1
        and level1_global_be_category = '{l1}'
        and level2_global_be_category = '{l2}'
    group by 1, 2, 3, 4
    limit {limit}
    """
    l2 = sub('/| / ', '_', l2)
    save_path = path / f'l12/{l1}_{l2}.parquet'
    DataPipeLine(query).run_presto_to_df(save_path=save_path, verbose=False)


with ThreadPoolExecutor(4) as executor:
    executor.map(download, df_cat)

# arr = df_cat[0]
# l1, l2, limit = arr['level1_global_be_category'], arr['level2_global_be_category'], arr['total_item']
# limit = max(limit, 30_000)
# query = f"""
# select
#     item_id
#     ,item_name
#     ,level1_global_be_category
#     ,level2_global_be_category
#     ,count(distinct item_id) total_item
#     ,count(distinct shop_id) total_shop
# from
#     mp_order.dwd_order_item_all_ent_df__vn_s0_live
# where
#     date(create_datetime) >= current_date - interval '365' day
#     and is_cb_shop = 0
#     and is_net_order = 1
#     and level1_global_be_category = '{l1}'
#     and level2_global_be_category = '{l2}'
# group by 1, 2, 3, 4
# limit {limit}
# """
# df = DataPipeLine(query).run_presto_to_df()
