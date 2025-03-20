from core_pro import DataPipeLine
from core_pro.ultilities import make_sync_folder
import polars as pl


query = f"""
with comment_tab as (
    select
        date(r.create_datetime) create_date
        ,count(distinct comment_id) total_comments
    from
        mp_item.dwd_item_review_df__vn_s0_live r
        left join mp_item.dim_item__vn_s0_live i on r.item_id = i.item_id
        and i.grass_date = current_date - interval '1' day
    where
        r.status in (1, 2)
        and cardinality(split(r.comment, ' ')) > 1
        and date(r.create_datetime) >= date '2024-10-01'
    group by 1
)
,tag as (
    select
        create_date
        ,count(*) total_comments
    from dev_vnbi_ops.ds_cx__item_marketplace_listening__s3
    group by 1
)
select
    c.*
    ,t.total_comments total_tag
    ,c.total_comments - t.total_comments dif
from
    comment_tab c
    left join tag t on c.create_date = t.create_date
"""
path = make_sync_folder("cx/product_review/deploy")
df = DataPipeLine(query).run_presto_to_df(overwrite=True)
missing = df.filter(pl.col('dif') > 0)
missing.write_parquet(path / "missing.parquet")
#
# df = pl.read_parquet(path / "missing.parquet")
