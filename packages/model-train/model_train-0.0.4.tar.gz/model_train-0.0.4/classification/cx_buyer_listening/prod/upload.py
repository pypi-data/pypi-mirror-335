from pathlib import Path
import polars as pl
from core_pro.ultilities import upload_to_datahub, make_sync_folder, make_dir
import sys

sys.path.extend([str(Path.home() / "PycharmProjects/model_train")])
from src.model_train.pipeline_infer import InferenceTextClassification
from config import dict_source


path = make_sync_folder("cx/buyer_listening/inference/2025")
file_nps = next(path.glob("nps/result/*.csv"))
df_nps = pl.read_csv(file_nps)
# upload_to_datahub()

# kompa
file_kompa = sorted([*path.glob("kompa/result/*.csv")])
file_kompa_export = path / f"kompa/export"
make_dir(file_kompa_export)
file_export = file_kompa_export / "full.csv"

df_kompa = pl.DataFrame()
for f in file_kompa:
    tmp = (
        pl.read_csv(f, ignore_errors=True)
        .with_columns(
            pl.col("PublishedDate").str.strptime(pl.Date, format="%Y-%m-%dT%H:%M:%S%.f"),
            pl.col('AuthorId').cast(pl.String)
        )
    )
    df_kompa = pl.concat([df_kompa, tmp])
df_kompa.write_csv(file_export)

# app_review
file_app_review = sorted([*path.glob("app_review/result/*.csv")])
df_app = pl.DataFrame()
for f in file_app_review:
    tmp = pl.read_csv(f)
    if len(tmp.columns) == 8:
        df_app = pl.concat([df_app, tmp])
