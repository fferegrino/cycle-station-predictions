import json
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

with mlflow.start_run(run_id=MLFLOW_RUN_ID):
    client = MlflowClient()
    t0 = time.time()
    temp_dir = tempfile.mkdtemp()
    data_parquet = client.download_artifacts(run_id=MLFLOW_RUN_ID, path="data.parquet", dst_path=temp_dir)
    regions_folder = client.download_artifacts(run_id=MLFLOW_RUN_ID, path="regions.json", dst_path=temp_dir)

    with open(regions_folder) as f:
        regions = json.load(f)

    df = pl.read_parquet(data_parquet)

    for region, region_data in regions.items():
        place_id = region_data["mean_station"]
        mlflow.log_param(f"{region}/place_id", place_id)
        # with mlflow.start_run(run_name=place_id, nested=True):
        filtered = df.filter(pl.col("place_id") == place_id)

        mlflow.log_param(f"{region}/training_dataset_shape", filtered.shape)

        resampled = resample(filtered)

        mlflow.log_param(f"{region}/resampled_dataset_shape", resampled.shape)

        cutoff = resampled["rounded_time"].max() - timedelta(hours=24 * 7)

        mlflow.log_param(f"{region}/cutoff_time", cutoff.strftime("%Y-%m-%d %H:%M:%S"))

        training_data = resampled.filter(pl.col("rounded_time") < cutoff)
        holdout_data = resampled.filter(pl.col("rounded_time") >= cutoff)

        prepared_frame = (
            training_data.with_columns(
                pl.col("rounded_time").dt.strftime("%Y-%m-%d %H:%M:%S").alias("ds"),
                pl.col("occupancy_ratio").alias("y"),
            )
            .select(["ds", "y"])
            .to_pandas()
        )

        prophet = Prophet()
        prophet.fit(prepared_frame)

        mlflow.prophet.log_model(prophet, f"{region}/prophet_model")

        version = mlflow.register_model(f"runs:/{MLFLOW_RUN_ID}/{region}/prophet_model", f"{region}__prophet_model")
        client.set_registered_model_alias(
            version.name,
            "champion",  # Make this the champion model for now
            version.version,
        )

        client.set_registered_model_tag(
            version.name,
            "cycle_prediction",
            "true",
        )

        client.set_registered_model_tag(
            version.name,
            "place_id",
            place_id,
        )

        future = (
            holdout_data.with_columns(pl.col("rounded_time").dt.strftime("%Y-%m-%d %H:%M:%S").alias("ds"))
            .select(["ds", "occupancy_ratio"])
            .to_pandas()
        )

        forecast = prophet.predict(future[["ds"]])

        from sklearn.metrics import mean_absolute_error

        mae = mean_absolute_error(holdout_data["occupancy_ratio"], forecast["yhat"])

        mlflow.log_metric(f"{region}/mae", mae)

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

        fig.write_html(f"{temp_dir}/{region}_forecast.html")
        mlflow.log_artifact(f"{temp_dir}/{region}_forecast.html", f"{region}")

        t1 = time.time()
        mlflow.log_metric(f"{region}/training_time", t1 - t0)
