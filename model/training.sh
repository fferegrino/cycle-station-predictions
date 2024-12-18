#!/bin/bash

export MLFLOW_TRACKING_URI=http://localhost:5555

MLFLOW_RUN_ID=$(python model/training/create_run.py)

export MLFLOW_RUN_ID=$MLFLOW_RUN_ID

python model/training/download_dataset.py

python model/training/preprocessing.py

python model/training/train_model.py
