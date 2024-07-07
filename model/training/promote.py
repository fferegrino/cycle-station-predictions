import os
import sys
import time

import mlflow
from mlflow.tracking import MlflowClient

MLFLOW_RUN_ID = os.environ["MLFLOW_RUN_ID"]
PLACE_ID = sys.argv[1]

with mlflow.start_run(run_id=MLFLOW_RUN_ID):
    client = MlflowClient()
    t0 = time.time()

    model_name = f"{PLACE_ID}__prophet_model"
    challenger_alias = "challenger"

    model_info = client.get_model_version_by_alias(model_name, challenger_alias)

    model_uri = f"models:/{model_name}@{challenger_alias}"
    challenger_prophet = mlflow.prophet.load_model(model_uri)

    # TODO: implement the model promotion logic

    client.delete_registered_model_alias(model_name, challenger_alias)
    client.set_registered_model_alias(model_name, "champion", model_info.version)

    t1 = time.time()
    mlflow.log_metric("model_promotion_time", t1 - t0)
