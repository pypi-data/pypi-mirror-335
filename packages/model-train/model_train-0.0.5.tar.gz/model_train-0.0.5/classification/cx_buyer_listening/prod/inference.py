from pathlib import Path
import polars as pl
from rich import print
from core_pro.ultilities import make_dir, make_sync_folder, upload_to_datahub, filter_unprocessed_files
from core_eda import TextEDA
from datasets import Dataset
from tqdm.auto import tqdm
import re
from collections import defaultdict
import sys

sys.path.extend([str(Path.home() / "PycharmProjects/model_train")])
from src.model_train.pipeline_infer import InferenceTextClassification
from config import dict_source


# path
path = make_sync_folder("cx/buyer_listening/inference/2025")
files = sorted([*path.glob("*/*.xlsx")])

# file_inference = sorted([*path.glob(f"*/result/*")])
# file_inference_name = [f.name for f in file_inference]
# new_infer_file = filter_unprocessed_files(files, file_inference_name)

# model
path_model = "kevinkhang2909/buyer_listening"
infer = InferenceTextClassification(
    pretrain_name=path_model,
    torch_compile=False,
    fp16=True,
    task_type="multi_classes",
)

def clean_file_name(file_path: Path):
    file_name = file_path.stem
    file_name = '_'.join(re.sub(r"\.", "", file_name.lower()).split(' '))
    return file_name


def run(file_path: Path):
    # init source:
    folder = file_path.parts[-2]
    print(f"=== START {file_path.name} ===")

    # create path
    path_export = path / folder / "result"
    make_dir(path_export)
    file_name = clean_file_name(file_path)
    file_export = path_export / f"{file_name}.parquet"
    if file_export.exists():
        print(f"Batch Done: {file_export.stem}")
        return None, None, file_export

    # data
    if folder == "nps":
        df = pl.read_parquet(file_path)
    else:
        df = pl.read_excel(file_path, engine="openpyxl")
    string_cols = [i for i in dict_source[folder]["string_cols"] if i in df.columns]
    select_cols = [i for i in dict_source[folder]["select_cols"] if i in df.columns]

    # clean data
    lst = {
        col: [TextEDA.clean_text_multi_method(_) for _ in df[col]]
        for col in tqdm(string_cols, desc="[TextEDA] Clean Text")
    }
    if not select_cols:
        df_clean = pl.DataFrame(lst)
    else:
        df_clean = pl.concat([df[select_cols], pl.DataFrame(lst)], how="horizontal")
    df_clean = (
        df_clean
        .with_columns(
            pl.concat_str([pl.col(i) for i in string_cols], separator=". ").alias("text")
        )
    )

    # infer
    # print(infer.process_batch(df_clean["text"][0]))
    ds_pred = infer.run_pipeline(Dataset.from_polars(df_clean), text_column="text")

    # post process
    ds_pred_post = (
        ds_pred.to_polars()
        .with_columns(
            pl.col("labels").str.split(" >> ").list[i].alias(v)
            for i, v in enumerate(["l1_pred", "l2_pred"])
        )
        .drop(["labels"])
        .with_columns(pl.lit(f"{f.stem}").alias("file_source"))
    )

    if folder == "kompa":
        ds_pred_post = ds_pred_post.with_columns(
            pl.col("PublishedDate").alias("grass_date"),
            pl.col('AuthorId').cast(pl.String),
            pl.col("score").cast(pl.Float32),
        )
    elif folder == "app_review":
        ds_pred_post = (
            ds_pred_post
            .with_columns(pl.col("score").cast(pl.Float32))
            .select(["Date", "text", "score", "l1_pred", "l2_pred", "file_source"])
        )
        ds_pred_post = ds_pred_post.with_columns(pl.col("Date").alias("grass_date"))

    elif folder == "nps":
        ds_pred_post = (
            ds_pred_post.with_columns(
                pl.col("date_submitted").str.to_date("%Y-%m-%d", strict=False),
                pl.col("date_submitted").str.to_date("%Y-%m-%d", strict=False).alias("grass_date"),
                pl.col("score").cast(pl.Float32),
            )
            .filter(pl.col("text") != "")
        )

    # export
    ds_pred_post.columns = [i.lower() for i in ds_pred_post.columns]
    ds_pred_post.write_parquet(file_export)
    return df, ds_pred_post, file_export


def export(df_csv, folder: str, dict_source: dict):
    path_export = path / folder / 'export'
    make_dir(path_export)
    file_csv = path_export / f"{folder}.csv"
    df_csv.write_csv(file_csv)

    api_endpoint = dict_source[folder]["api_endpoint"]
    ingestion_token = dict_source[folder]["ingestion_token"]
    upload_to_datahub(file_path=file_csv, api_endpoint=api_endpoint, ingestion_token=ingestion_token)


# tag
lst = defaultdict(list)
for f in files:
    df, df_tag, file_export = run(f)
    folder = file_export.parts[-3]
    lst[folder].append(file_export)
    # break

# export
for folder in lst:
    df_csv = pl.concat([pl.read_parquet(f) for f in lst[folder]])
    export(df_csv, folder, dict_source)

file = path / "nps/free_text.parquet"
df = pl.read_parquet(file)
df, df_csv, file_export = run(file)
folder = "nps"
df_csv = pl.read_parquet(file_export)
export(df_csv, folder, dict_source)
