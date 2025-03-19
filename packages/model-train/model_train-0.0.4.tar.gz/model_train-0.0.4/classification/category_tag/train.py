from pathlib import Path
import duckdb
from datetime import datetime
from transformers import AutoTokenizer
from core_pro.ultilities import make_sync_folder, update_df
import sys

sys.path.extend([str(Path.home() / "PycharmProjects/model_train")])

from src.model_train.data_loading import TrainDistribution
from src.model_train.pipeline_train import Pipeline
from src.model_train.func import training_report


def train(pretrain_name: str):
    # data
    path = make_sync_folder("dataset/category_tag")

    query = f"""
    select * from read_parquet('{path / "clean.parquet"}')
    """
    label = "level1_global_be_category"
    # label = "label"
    df = duckdb.sql(query).pl()
    print(f"Data shape: {df.shape}")

    # split train/test/val
    select_cols = ["item_id", "item_name", label]
    label_list = df[label].unique().to_list()
    dist_check = TrainDistribution(
        path, df, col_label=label, col_item="item_name", label_list=label_list
    )
    dict_split, dict_ds = dist_check.split_train_valid_test(
        select_cols=select_cols, test_size=0.2
    )

    # tokenizer
    tokenizer = AutoTokenizer.from_pretrained(pretrain_name)
    dict_train = dist_check.ds_tokenize(tokenizer, show_index=1)

    # train
    pipe = Pipeline(
        pretrain_name=pretrain_name,
        id2label=dist_check.id2label,
        label2id=dist_check.label2id,
        bf16=True,
        flash_attention_2=False,
        # per_device_train_batch_size=16,
        # per_device_eval_batch_size=4,
        hub_model_id="kevinkhang2909/l1_category",
    )
    time_now = datetime.now().strftime("%Y%m%d%H%M%S")
    folder = str(
        path / f"model_multi_classes/{label}_{pretrain_name.split('/')[-1]}/{time_now}"
    )
    config = dict(
        log_step=5000,
        num_train_epochs=5,
        learning_rate=1e-4,
    )
    trainer = pipe.train(
        folder=folder, train=dict_train["train"], val=dict_train["valid"], **config
    )

    # report
    valid_result = trainer.predict(dict_train["test"])
    y_pred = valid_result.predictions.argmax(-1)
    y_true = valid_result.label_ids
    df_report = training_report(
        y_true=y_true, y_pred=y_pred, id2label=dist_check.id2label
    )

    sh = "1L-4z-SrAWXee-ScQ9dZCEVcPrUGaJUv5U4hw_jiDeOI"
    update_df(df_report, f"{label}_{pretrain_name.split("/")[1]}", sh)


train("bkai-foundation-models/vietnamese-bi-encoder")
# train("dangvantuan/vietnamese-embedding")
# train("answerdotai/ModernBERT-base")
