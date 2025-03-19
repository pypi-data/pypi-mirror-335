from torch import nn, Tensor
from transformers import EvalPrediction
from sklearn.metrics import (
    f1_score,
    roc_auc_score,
    accuracy_score,
    classification_report,
)
import numpy as np
from textwrap import dedent
from pathlib import Path
import pandas as pd
from huggingface_hub import login, HfApi
from .config import Config


def upload_model_to_hub(folder: Path | str, repo: str):
    login(token=Config.hub_token)

    api = HfApi()
    api.upload_folder(
        folder_path=folder,
        repo_id=repo,
        commit_message='model updated',
        ignore_patterns=['checkpoint*']
    )


class MultiLabels:
    def __init__(self):
        self.sigmoid = nn.Sigmoid()

    def post_process(self, predictions, threshold: float = 0.5):
        probs = self.sigmoid(Tensor(predictions))
        y_pred = np.zeros(probs.shape)
        y_pred[np.where(probs >= threshold)] = 1
        return y_pred

    def report(self, predictions, labels, threshold=0.5):
        y_pred = self.post_process(predictions, threshold)

        f1_micro_average = f1_score(y_true=labels, y_pred=y_pred, average="micro")
        roc_auc = roc_auc_score(labels, y_pred, average="micro")
        accuracy = accuracy_score(labels, y_pred)
        metrics = {"f1": f1_micro_average, "roc_auc": roc_auc, "accuracy": accuracy}
        return metrics

    def classification_report_html(
        self, result, labels, target_names: list = None, show: bool = True
    ):
        y_pred = MultiLabels().post_process(result)
        report = classification_report(labels, y_pred, target_names=target_names)
        if show:
            print(report)
        return report


def export_to_md(file_name: Path, config, valid_report, test_report):
    with open(file_name, "w", encoding="utf-8") as md:
        text = dedent(f"""
        Config:
        {config}

        Valid Classification Report:
        {valid_report}

        Test Classification Report:
        {test_report}
        """)
        md.write(text)


def compute_metrics_multi_labels(p: EvalPrediction):
    preds = p.predictions[0] if isinstance(p.predictions, tuple) else p.predictions
    result = MultiLabels().report(predictions=preds, labels=p.label_ids)
    return result


def compute_metrics_multi_class(p: EvalPrediction):
    logits, labels = p
    y_pred = logits.argmax(-1)

    f1_micro_average = f1_score(y_true=labels, y_pred=y_pred, average="micro")
    accuracy = accuracy_score(labels, y_pred)
    return {"f1": f1_micro_average, "accuracy": accuracy}


def training_report(y_true, y_pred, id2label: dict = None, verbose: bool = True):
    actual_classes = sorted(set(y_true) | set(y_pred))
    actual_class_names = [id2label.get(i) for i in actual_classes]

    if verbose:
        print(
            classification_report(
                y_true,
                y_pred,
                labels=actual_classes,
                target_names=actual_class_names,
                zero_division=True,
            )
        )

    report_dict = classification_report(
        y_true,
        y_pred,
        labels=actual_classes,
        target_names=actual_class_names,
        zero_division=True,
        output_dict=True,
    )
    return pd.DataFrame(report_dict).T.sort_index().reset_index()
