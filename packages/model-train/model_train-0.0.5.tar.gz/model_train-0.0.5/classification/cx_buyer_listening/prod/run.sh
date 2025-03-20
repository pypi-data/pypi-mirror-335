#!/bin/bash

eval "$(mamba shell hook --shell bash)"
mamba activate py313

python /home/kevin/PycharmProjects/model_train/classification/cx_buyer_listening/prod/get_data.py
python /home/kevin/PycharmProjects/model_train/classification/cx_buyer_listening/prod/inference.py

mamba deactivate
