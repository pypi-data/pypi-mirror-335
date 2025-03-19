from core_pro import DataPipeLine, Sheet
from core_pro.ultilities import make_sync_folder


sh = '1KjoWbnUAV45lTtRModwnq_QDPLLGKwZbfrb_SBzL8aE'
df = Sheet(sh).google_sheet_into_df('List Item', 'A:A')
items = df['supplier_item_id'].unique().to_list()
items = ', '.join(items)

query = f"""
with comment_tab as (
    select distinct
        r.comment_id
        ,r.shop_id
        ,r.item_id
        ,i.name item_name
        ,date(r.create_datetime) create_datetime
        ,cast(
            map_from_entries(
                array[
                    ('comment_id', cast(r.comment_id as varchar))
                    ,('comment', r.comment)
                    ,('rating_star', cast(r.rating_star as varchar))
                ]
            ) as json
        ) comment_star
        ,case when CARDINALITY(split(r.comment, ' ')) between 2 and 50 then 1 else 0 end valid_comment
    from
        mp_item.dwd_item_review_df__vn_s0_live r
        left join mp_item.dim_item__vn_s0_live i on r.item_id = i.item_id
        and i.grass_date = current_date - interval '1' day
    where
        r.status in (1, 2)
        and CARDINALITY(split(r.comment, ' ')) > 1
        and date(r.create_datetime) >= date '2024-11-01'
        and r.item_id in ({items})
)

    select
        c.shop_id
        ,c.item_id
        ,c.item_name
        ,c.create_datetime
        ,array_agg(c.comment_star) comment_star
        ,count(distinct comment_id) total_comments
        ,count(distinct case when valid_comment = 1 then comment_id else null end) total_valid_comments
    from comment_tab c
    group by 1, 2, 3, 4
"""

path = make_sync_folder('cx_product_review')
df = DataPipeLine(query).run_presto_to_df(save_path=path / 'raw/adhoc.parquet')
