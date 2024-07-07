import os
import time

import mlflow
import polars as pl

MLFLOW_RUN_ID = os.environ["MLFLOW_RUN_ID"]


def read_file(file_path: str) -> pl.DataFrame:
    df = (
        pl.read_csv(file_path)
        .with_columns(pl.col("query_time").str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%S%.f"))
        .with_columns(
            pl.col("query_time").dt.round("15m").alias("rounded_time"),
        )
        .with_columns(
            pl.col("lat").cast(pl.Float32),
            pl.col("lon").cast(pl.Float32),
            pl.col("bikes").cast(pl.Int32),
            pl.col("docks").cast(pl.Int32),
            pl.col("empty_docks").cast(pl.Int32),
            ((pl.col("docks") - pl.col("empty_docks")) / pl.col("docks")).alias("occupancy_ratio"),
        )
    )

    return df


if __name__ == "__main__":
    with mlflow.start_run(run_id=MLFLOW_RUN_ID):
        t0 = time.time()
        df = read_file("temp_data/weekly-london-cycles-db/data/*.csv")
        mlflow.log_param("dataset_shape", df.shape)
        mlflow.log_param("dataset_columns", df.columns)
        mlflow.log_param("dataset_schema", df.schema)
        df.write_parquet("temp_data/weekly-london-cycles-db/data.parquet")
        mlflow.log_artifact("temp_data/weekly-london-cycles-db/data.parquet")
        t1 = time.time()
        mlflow.log_metric("dataset_preprocessing_time", t1 - t0)
