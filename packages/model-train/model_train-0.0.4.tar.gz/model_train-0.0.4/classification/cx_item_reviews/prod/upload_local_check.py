import duckdb
import polars as pl
from core_pro.ultilities import make_sync_folder


# path
path = make_sync_folder("cx/product_review/deploy")

query = f"""
with base as (
    select * exclude(comment_stats)
    , unnest(comment_stats, recursive := true)
    from (
        select * exclude(comment_stats)
        , cast(unnest(comment_stats, recursive := true)::json as STRUCT(comment_id bigint, comment VARCHAR, rating_star int, create_date date)) comment_stats
        from read_parquet('{path / 'raw/*.parquet'}')
    )
)

, infer as (
    select create_date
    , count(distinct comment_id) total_comments
    from read_parquet('{path / 'inference/*.parquet'}')
    group by 1
)

, raw as (
    select create_date
    , count(distinct comment_id) total_comments
    from base
    group by 1
)

select r.* 
, i.total_comments total_comments_tag
, r.total_comments - i.total_comments dif
from raw r
left join infer i on r.create_date = i.create_date
"""
df = (
    duckdb.query(query).pl()
    .filter(pl.col("dif") != 0)
)
