from sklearn.model_selection import train_test_split
import numpy as np
import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
from datasets import Dataset, load_from_disk
from pathlib import Path
from rich import print
from core_pro.ultilities import make_dir


class TrainDistribution:
    def __init__(
        self,
        path: Path,
        data: pl.DataFrame,
        col_label: str,
        col_item: str,
        label_list: list,
        mode: str = "multi_classes",
        save: bool = False,
        **kwargs,
    ):
        self.path = path
        self.data = data
        self.col_label = col_label
        self.col_item = col_item
        self.label_list = label_list
        self.mode = mode
        self.save = save
        self.kwargs = kwargs

        self.dict_split = {}
        self.dict_ds = {}
        self.dict_ds_to_train = {}
        self.lst = ["train", "valid", "test"]

        self.label2id = None
        self.id2label = None
        self.create_label_id()

        print("[Data Loading]")

    def create_label_id(self):
        self.id2label = {idx: label for idx, label in enumerate(self.label_list)}
        self.label2id = {label: idx for idx, label in enumerate(self.label_list)}

    def split_train_valid_test(
        self, select_cols: list, test_size: float = 0.2, show_index: int = 1
    ):
        # path
        path_split = {_: self.path / f"{_}.parquet" for _ in self.lst}

        if not path_split["train"].exists():
            # split
            train, test = train_test_split(
                self.data, test_size=test_size, random_state=42
            )
            train, val = train_test_split(train, test_size=test_size, random_state=42)

            # assign to dict
            self.dict_split = {
                "train": train,
                "valid": val,
                "test": test,
            }

            # log
            message = ", ".join(
                [f"{k}: {v.shape[0]:,.0f}" for k, v in self.dict_split.items()]
            )
            print(f"-> Train/Test/Validation Split\n-> Shape {message}")

            # save
            train.write_parquet(self.path / "train.parquet")
            test.write_parquet(self.path / "test.parquet")
            val.write_parquet(self.path / "valid.parquet")

        else:
            self.dict_split = {
                _: pl.read_parquet(self.path / f"{_}.parquet") for _ in self.lst
            }

        # to dataset
        self.dict_ds = {
            k: Dataset.from_list(v[select_cols].to_dicts())
            for k, v in self.dict_split.items()
        }

        # log
        message = "\n".join([f"{k}: {v[0]}" for k, v in self.dict_ds.items()])
        print(f"-> Show data example: {show_index}\n{message}")

        return self.dict_split, self.dict_ds

    def _tokenize_data(self, examples, tokenizer):
        # tokenize
        text = examples[self.col_item]
        encoding = tokenizer(
            text,
            padding="max_length",
            truncation=True,
            max_length=self.kwargs.get("max_length", 50),
        )

        # add label
        if self.mode != "multi_classes":
            labels_batch = {
                k: examples[k] for k in examples.keys() if k in self.label_list
            }
            labels_matrix = np.zeros((len(text), len(self.label_list)))
            for idx, label in enumerate(self.label_list):
                labels_matrix[:, idx] = labels_batch[label]
            encoding["labels"] = labels_matrix.tolist()
        else:
            encoding["labels"] = [
                self.label2id.get(i) for i in examples[self.col_label]
            ]

        return encoding

    def ds_tokenize(self, tokenizer, show_index: int = 0):
        # path ds
        path_ds = self.path / "ds"
        make_dir(path_ds)
        path_dict = {_: path_ds / f"{_}" for _ in self.dict_ds}

        # tokenize
        if not path_dict["train"].exists():
            for k, v in self.dict_ds.items():
                ds = v.map(
                    self._tokenize_data,
                    batched=True,
                    remove_columns=v.column_names,
                    fn_kwargs={"tokenizer": tokenizer},
                    desc="Tokenizing data",
                )
                ds.set_format("torch")
                ds.save_to_disk(path_dict[k])
                self.dict_ds_to_train.update({k: ds})
        else:
            self.dict_ds_to_train = {i: load_from_disk(v) for i, v in path_dict.items()}

        # log
        example = self.dict_ds_to_train["train"][show_index]
        if self.mode != "multi_classes":
            label = [
                self.id2label[idx]
                for idx, label in enumerate(example["labels"])
                if label == 1.0
            ]
        else:
            label = example["labels"]

        print(
            f"-> Show token example: {show_index}\n"
            f"-> Keys: {example.keys()}\n"
            f"-> Token: {tokenizer.decode(example['input_ids'])}\n"
            f"-> Labels: {label}\n"
        )

        return self.dict_ds_to_train

    def multi_label_stats(self, data: pl.DataFrame, name: str):
        data_cal = (
            data[self.label_list]
            .sum()
            .transpose()
            .insert_column(0, pl.Series(self.label_list))
        )
        data_cal.columns = ["name", "val"]
        data_cal = data_cal.with_columns(
            (pl.col("val") / data.shape[0]).alias("pct"), pl.lit(name).alias("data")
        )
        return data_cal

    def multi_classes_stats(self, data: pl.DataFrame, name: str):
        data_cal = (
            data.group_by([self.col_label])
            .agg(pl.col(self.col_item).n_unique())
            .rename({self.col_label: "name"})
            .with_columns(
                (pl.col(self.col_item) / pl.col(self.col_item).sum()).alias("pct"),
                pl.lit(name).alias("data"),
            )
        )
        return data_cal

    def check_distribution(self):
        if self.label_list:
            lst = [
                self.multi_classes_stats(data=v, name=k)
                for k, v in self.dict_split.items()
            ]
        else:
            lst = [
                self.multi_label_stats(data=v, name=k)
                for k, v in self.dict_split.items()
            ]
        df_label_distribution = pl.concat(lst, how="vertical")
        fig, ax = plt.subplots(1, 1, figsize=(12, 6))
        sns.barplot(data=df_label_distribution, y="pct", x="name", hue="data", ax=ax)
        ax.tick_params(axis="x", rotation=90)
        fig.tight_layout()
