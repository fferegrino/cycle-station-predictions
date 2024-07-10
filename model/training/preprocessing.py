import json
import os
import time

import mlflow
import numpy as np
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


def calculate_regions(df):
    stations = df.unique(subset=["place_id", "lat", "lon"])
    stat = stations.filter(pl.col("lat") > 41.5)
    min_lon, max_lon = stat["lon"].min(), stat["lon"].max()
    min_lat, max_lat = stat["lat"].min(), stat["lat"].max()

    lon_buffer = (max_lon - min_lon) * 0.02
    lat_buffer = (max_lat - min_lat) * 0.02

    n_lon, n_lat = 4, 4
    lon_bins = np.linspace(min_lon - lon_buffer, max_lon + lon_buffer, n_lon)
    lat_bins = np.linspace(min_lat - lat_buffer, max_lat + lat_buffer, n_lat)

    lon_intervals = list(zip(lon_bins[:-1], lon_bins[1:]))
    lat_intervals = list(zip(lat_bins[:-1], lat_bins[1:]))

    regions = {}

    for lat_interval, name in zip(lat_intervals, ["south", "", "north"]):
        for lon_interval, name2 in zip(lon_intervals, ["west", "", "east"]):
            region = f"{name}{name2}" or "centre"

            filtered = (
                stat.filter(pl.col("lon") > lon_interval[0])
                .filter(pl.col("lon") <= lon_interval[1])
                .filter(pl.col("lat") > lat_interval[0])
                .filter(pl.col("lat") <= lat_interval[1])
            )
            if len(filtered) > 0:

                mean_lon = filtered["lon"].mean()
                mean_lat = filtered["lat"].mean()

                distances = filtered.with_columns(
                    ((pl.col("lon") - mean_lon) ** 2 + (pl.col("lat") - mean_lat) ** 2).alias("distance")
                )

                closest, closest_lon, closest_lat = (
                    distances.sort("distance").select(pl.first("place_id", "lon", "lat")).row(0)
                )

                regions[region] = {
                    "mean_station": closest,
                    "lat_min": lat_interval[0],
                    "lat_max": lat_interval[1],
                    "lon_min": lon_interval[0],
                    "lon_max": lon_interval[1],
                }
            else:
                print(f"{name}{name2}: No stations")
    return regions


if __name__ == "__main__":
    with mlflow.start_run(run_id=MLFLOW_RUN_ID):
        t0 = time.time()
        df = read_file("temp_data/weekly-london-cycles-db/data/*.csv")
        regions = calculate_regions(df)

        with open("temp_data/weekly-london-cycles-db/regions.json", "w") as f:
            json.dump(regions, f)

        mlflow.log_artifact("temp_data/weekly-london-cycles-db/regions.json")

        mlflow.log_param("dataset_shape", df.shape)
        mlflow.log_param("dataset_columns", df.columns)
        mlflow.log_param("dataset_schema", df.schema)
        df.write_parquet("temp_data/weekly-london-cycles-db/data.parquet")
        mlflow.log_artifact("temp_data/weekly-london-cycles-db/data.parquet")
        t1 = time.time()
        mlflow.log_metric("dataset_preprocessing_time", t1 - t0)
