from core_pro import DataPipeLine
from core_pro.ultilities import make_sync_folder
from datetime import date, timedelta, datetime
import polars as pl
from concurrent.futures import ThreadPoolExecutor


# config
path = make_sync_folder('cx/product_review/deploy/raw')

start = date(2024, 10, 1)
end = date.today() - timedelta(days=1)
run = [i.date() for i in pl.datetime_range(start, end, "1d", eager=True)]
files = [datetime.strptime(i.stem.split("_")[1], "%Y-%m-%d").date() for i in [*path.glob("*.parquet")]]
new_day = list(set(run) - set(files))

def spawn(d):
    query = f"""
    with comment_tab as (
        select distinct
            r.comment_id
            ,r.shop_id
            ,case when r.shop_id = 851157471 then 'Choice' else 'Marketplace' end shop_type
            ,r.item_id
            ,i.name item_name
            ,date(date_trunc('month', r.create_datetime)) grass_month
            ,cast(
                map_from_entries(
                    array[
                        ('comment_id', cast(r.comment_id as varchar))
                        ,('comment', r.comment)
                        ,('rating_star', cast(r.rating_star as varchar))
                        ,('create_date', cast(date(r.create_datetime) as varchar))
                    ]
                ) as json
            ) comment_stats
            ,cardinality(split(r.comment, ' ')) comment_length
            ,case
                when cardinality(split(r.comment, ' ')) between 2 and 50 then 1
                else 0
            end valid_comment
        from
            mp_item.dwd_item_review_df__vn_s0_live r
            left join mp_item.dim_item__vn_s0_live i on r.item_id = i.item_id
            and i.grass_date = current_date - interval '1' day
        where
            r.status in (1, 2)
            and cardinality(split(r.comment, ' ')) > 1
            and date(r.create_datetime) = date '{d}'
    )
    select
        c.shop_id
        ,c.shop_type
        ,c.item_id
        ,c.item_name
        ,c.grass_month
        ,array_agg(c.comment_stats) comment_stats
        ,count(distinct comment_id) total_comments
        ,sum(valid_comment) valid_comment
    from comment_tab c
    group by 1, 2, 3, 4, 5
    """
    df = DataPipeLine(query).run_presto_to_df(save_path=path / f'raw_{d}.parquet', verbose=False)

# spawn(run[0])
with ThreadPoolExecutor(max_workers=4) as executor:
    list(executor.map(spawn, new_day))
