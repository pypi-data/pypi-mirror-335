from core_pro import Sheet
from core_pro.ultilities import make_sync_folder
import polars as pl


col_all = ['text', 'l1', 'l2', 'sentiment']

sh = '1sa09xeq-FTC5Qi37qstXc722tB8R3oXlB1tK7u_LseA'
col = ['Content', 'predicted_L1', 'predicted_L2', 'segment']
df_nps = (
    Sheet(sh).google_sheet_into_df('predict pain point', 'A:Q')
    .select(col)
)
df_nps.columns = col_all

sh = '1Q5Bk5PHa0pMa378aQM9WD9k1Q2InZD69k3R7Byp_Us0'
col = ['Content', 'predicted_L1_top1', 'predicted_L2_top1', 'Sentiment']
df_social = (
    Sheet(sh).google_sheet_into_df('Raw', 'A:T')
    .select(col)
)
df_social.columns = col_all

sh = '11SIxbPge86_hCorWJGSJAWUJfaVtba6cJp9CEw2qb6A'
col = ['Content', 'predicted_L1', 'predicted_L2', 'Sentiment']
df_app_review = (
    Sheet(sh).google_sheet_into_df('App review_2024', 'A:T')
    .select(col)
)
df_app_review.columns = col_all

df = pl.concat([df_nps, df_social, df_app_review])
print(df.shape, df['text'].n_unique())

path = make_sync_folder('cx/buyer_listening')
df.write_parquet(path / 'raw.parquet')
