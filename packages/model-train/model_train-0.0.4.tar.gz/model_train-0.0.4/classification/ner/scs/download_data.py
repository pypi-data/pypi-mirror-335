from core_pro import DataPipeLine
from core_pro.ultilities import make_sync_folder


path = make_sync_folder('scs/brand')
query = f"""
select
    d.*
    ,i.item_name
    ,i.model_name
    ,i.shop_id
    ,i.shop_name
    ,i.level1_global_be_category
    ,i.level2_global_be_category
    ,i.level3_global_be_category
from
    dev_vnbi_bd.scs_cspu_wishlist_pool_tentative_jan25 d
    left join mp_item.dim_model__vn_s0_live i on d.typical_model_id = i.model_id
    and i.grass_date = current_date - interval '2' day
"""
df = DataPipeLine(query=query).run_presto_to_df(save_path=path / 'lst.parquet')
