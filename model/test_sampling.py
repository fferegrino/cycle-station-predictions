import polars as pl
from polars.testing import assert_frame_equal

from sampling import resample


def test_resample():
    df = pl.DataFrame(
        {
            "rounded_time": ["2021-01-01 00:00:00", "2021-01-01 00:15:00", "2021-01-01 00:45:00"],
            "place_id": ["1", "1", "1"],
            "value": [1, None, 3],
        }
    ).with_columns(
        pl.col('rounded_time').str.strptime(pl.Datetime, '%Y-%m-%d %H:%M:%S')
    )

    resampled = resample(df)

    expected = pl.DataFrame(
        {
            "rounded_time": [
                "2021-01-01 00:00:00",
                "2021-01-01 00:15:00",
                "2021-01-01 00:30:00",
                "2021-01-01 00:45:00",
            ],
            "place_id": ["1", "1", "1", "1"],
            "value": [1.0, 1.6666666666666665, 2.333333333333333, 3.0],
        }
    ).with_columns(
        pl.col('rounded_time').str.strptime(pl.Datetime, '%Y-%m-%d %H:%M:%S')
    )

    assert_frame_equal(resampled, expected)


def test_resample_drops_duplicate_dates():
    df = pl.DataFrame(
        {
            "rounded_time": ["2021-01-01 00:00:00", "2021-01-01 00:00:00", "2021-01-01 00:15:00"],
            "place_id": ["1", "1", "1"],
            "value": [1, None, 3],
        }
    ).with_columns(
        pl.col('rounded_time').str.strptime(pl.Datetime, '%Y-%m-%d %H:%M:%S')
    )

    resampled = resample(df)

    expected = pl.DataFrame(
        {
            "rounded_time": [
                "2021-01-01 00:00:00",
                "2021-01-01 00:15:00",
            ],
            "place_id": ["1", "1"],
            "value": [1.0, 3.0],
        }
    ).with_columns(
        pl.col('rounded_time').str.strptime(pl.Datetime, '%Y-%m-%d %H:%M:%S')
    )

    assert_frame_equal(resampled, expected)