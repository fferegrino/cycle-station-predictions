import polars as pl


def resample(df, min_date=None, max_date=None, interval="15m"):
    if min_date is None:
        min_date = df["rounded_time"].min()
    if max_date is None:
        max_date = df["rounded_time"].max()

    # Create a complete time series covering the whole dataset timespan
    complete_time_series = pl.datetime_range(start=min_date, end=max_date, interval=interval, eager=True)

    # Get unique place_ids
    unique_place_ids = df["place_id"].unique()

    # Create a cartesian product of times and place_ids
    times = complete_time_series.to_frame()
    places = unique_place_ids.to_frame()
    interpolated = times.join(places, how="cross").rename({"literal": "rounded_time"})

    # Merge the original data with the complete time series
    interpolated = interpolated.join(df, on=["rounded_time", "place_id"], how="left").sort("rounded_time")

    # Remove duplicate rounded_time columns
    interpolated = interpolated.unique(subset=["rounded_time"])

    return interpolated.interpolate()
