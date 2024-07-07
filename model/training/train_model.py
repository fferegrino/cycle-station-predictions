import os
import sys
import tempfile
import time
from datetime import timedelta

import mlflow
import plotly.graph_objects as go
import polars as pl
from mlflow.tracking import MlflowClient
from plotly.subplots import make_subplots
from prophet import Prophet
from sampling import resample

MLFLOW_RUN_ID = os.environ["MLFLOW_RUN_ID"]
PLACE_ID = sys.argv[1]

with mlflow.start_run(run_id=MLFLOW_RUN_ID):
    client = MlflowClient()
    t0 = time.time()
    temp_dir = tempfile.mkdtemp()
    data_parquet = client.download_artifacts(run_id=MLFLOW_RUN_ID, path="data.parquet", dst_path=temp_dir)

    df = pl.read_parquet(data_parquet)

    filtered = df.filter(pl.col("place_id") == sys.argv[1])
    mlflow.log_param(f"{PLACE_ID}/training_dataset_shape", filtered.shape)

    resampled = resample(filtered)

    mlflow.log_param(f"{PLACE_ID}/resampled_dataset_shape", resampled.shape)

    cutoff = resampled["rounded_time"].max() - timedelta(hours=24 * 7)

    mlflow.log_param(f"{PLACE_ID}/cutoff_time", cutoff.strftime("%Y-%m-%d %H:%M:%S"))

    training_data = resampled.filter(pl.col("rounded_time") < cutoff)
    holdout_data = resampled.filter(pl.col("rounded_time") >= cutoff)

    prepared_frame = (
        training_data.with_columns(
            pl.col("rounded_time").dt.strftime("%Y-%m-%d %H:%M:%S").alias("ds"), pl.col("occupancy_ratio").alias("y")
        )
        .select(["ds", "y"])
        .to_pandas()
    )

    prophet = Prophet()
    prophet.fit(prepared_frame)

    mlflow.prophet.log_model(prophet, f"{PLACE_ID}/prophet_model")

    future = (
        holdout_data.with_columns(pl.col("rounded_time").dt.strftime("%Y-%m-%d %H:%M:%S").alias("ds"))
        .select(["ds", "occupancy_ratio"])
        .to_pandas()
    )

    forecast = prophet.predict(future[["ds"]])

    from sklearn.metrics import mean_absolute_error

    mae = mean_absolute_error(holdout_data["occupancy_ratio"], forecast["yhat"])

    mlflow.log_metric(f"{PLACE_ID}/mae", mae)

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=future["ds"], y=future["occupancy_ratio"], name="actual targets"),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=future["ds"], y=forecast["yhat"], name="predicted targets"),
        secondary_y=True,
    )
    fig.update_layout(title_text="Actual vs Predicted Targets")
    fig.update_xaxes(title_text="Timeline")
    fig.update_yaxes(title_text="actual targets", secondary_y=False)
    fig.update_yaxes(title_text="predicted targets", secondary_y=True)

    fig.write_html(f"{temp_dir}/forecast.html")
    mlflow.log_artifact(f"{temp_dir}/forecast.html", f"{PLACE_ID}")

    t1 = time.time()
    mlflow.log_metric(f"{PLACE_ID}/training_time", t1 - t0)
