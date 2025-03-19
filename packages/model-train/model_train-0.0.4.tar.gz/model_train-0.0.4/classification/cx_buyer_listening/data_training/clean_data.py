from core_pro.ultilities import make_sync_folder, update_df
import polars as pl
from core_eda import TextEDA


path = make_sync_folder('cx/buyer_listening')
file = path / 'raw.parquet'
df = pl.read_parquet(file)
print(f'Data Shape: {df.shape}, Total Text: {df['text'].n_unique()}')


def clean_pipeline(data):
    return (
        data
        .with_columns(
            pl.col('text').str.replace('\n', ' '),
        )
        .pipe(TextEDA.clean_text, col='text')
        .pipe(TextEDA.len_text, col='text_clean')
        .with_columns(
            pl.col(i).str.strip_chars() for i in ['l1', 'l2', 'sentiment']
        )
        .filter(
            pl.col('text') != '',
            pl.col('text_clean_word_count') != 1,
            pl.col('l1') != '',
        )
        .unique(['text'])
        .with_row_index()
    )


df = df.pipe(clean_pipeline)
print(f'Data Shape: {df.shape}, Total Text: {df['text'].n_unique()}')
df.write_parquet(path / f'{file.stem}_cleaned.parquet')

col = ['l1', 'l2']
df_cat = (
    df.group_by(col).agg(pl.col('index').count())
    .sort(col)
)

col = ['sentiment']
df_sentiment = (
    df.group_by(col).agg(pl.col('index').count())
    .sort(col)
)

sh = '1TsAxRmQDPIuL_enHMyHZSsb1aZZs9VCSzOYyXo83uZA'
update_df(df_cat, 'train', sh, start='A2')
update_df(df_sentiment, 'train', sh, start='e2')
