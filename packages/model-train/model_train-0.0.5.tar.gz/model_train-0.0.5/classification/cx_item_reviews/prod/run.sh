#!/bin/bash

eval "$(mamba shell hook --shell bash)"
mamba activate py313

python /home/kevin/PycharmProjects/model_train/classification/cx_item_reviews/prod/download_data.py
python /home/kevin/PycharmProjects/model_train/classification/cx_item_reviews/prod/inference.py

mamba deactivate
