import logging
from datetime import datetime
from typing import Any

import pendulum
import polars as pl

logger = logging.getLogger("root")


def adaptive_downsample(df: pl.DataFrame, column: str, window_size: int, threshold: float) -> pl.DataFrame:
    """Adaptive downsampling of data points based on rate of change."""
    downsampled_df_size_valid = False
    while not downsampled_df_size_valid:
        downsampled_data = []
        time_stamps = []

        for i in range(0, df.height, window_size):
            window = df.slice(i, window_size)
            rate_of_change = window[column].diff().abs().mean()

            if rate_of_change > threshold:
                downsampled_data.extend(window[column].to_list())
                time_stamps.extend(window["Time Stamp"].to_list())
            else:
                downsampled_data.append(window[column].mean())
                time_stamps.append(window["Time Stamp"][0])

        downsampled_df = pl.DataFrame({"Time Stamp": time_stamps, "Value": downsampled_data})
        rows = downsampled_df.height
        if rows > 7800000:
            threshold = threshold * 1.1
        else:
            downsampled_df_size_valid = True

    return downsampled_df


def normalize_timestamp(ts: Any) -> pl.Series:
    if isinstance(ts, str):
        return pl.from_epoch([int(pendulum.parse(ts).timestamp())]).cast(pl.Datetime("us", "UTC"))
    elif isinstance(ts, (int, float)):
        if ts < 10000000000:  # seconds
            return pl.from_epoch([ts], time_unit="s").cast(pl.Datetime("us", "UTC"))
        return pl.from_epoch([ts], time_unit="ms").cast(pl.Datetime("us", "UTC"))
    elif isinstance(ts, (datetime, pendulum.DateTime)):
        return pl.from_epoch([int(ts.timestamp())]).cast(pl.Datetime("us", "UTC"))
    raise ValueError(f"Unsupported timestamp format: {type(ts)}")


def process_metric_data(df: pl.DataFrame, start_date, end_date) -> pl.DataFrame:
    """Process metric data, handling empty dataframes and type conversions."""
    schema = {"Time Stamp": pl.Datetime("us", "UTC"), "Value": pl.Float64}
    if df.is_empty():
        logger.warning("Empty DataFrame received")
        return pl.DataFrame({"Time Stamp": pl.concat([normalize_timestamp(start_date), normalize_timestamp(end_date)]), "Value": pl.Series([0.0, 0.0])}).with_columns([
            pl.col("Time Stamp").cast(schema["Time Stamp"]),
            pl.col("Value").cast(schema["Value"]),
        ])
    df = df.sort("Time Stamp")
    first_timestamp = df["Time Stamp"][0]
    if isinstance(first_timestamp, (int, float)):
        time_unit = "s" if first_timestamp < 10000000000 else "ms"
        df = df.with_columns(pl.from_epoch("Time Stamp", time_unit=time_unit).cast(schema["Time Stamp"]))
    else:
        df = df.with_columns(pl.col("Time Stamp").cast(schema["Time Stamp"]))
    return df.with_columns(pl.col("Value").cast(schema["Value"]))


def calculate_scheduler_resources(scheduler_resources: dict[str, float]) -> str:
    """Calculate resources for software."""
    if scheduler_resources["memory"] % 384 == 0 and scheduler_resources["cpu"] % 100 == 0:
        if scheduler_resources["cpu"] / 100 == scheduler_resources["memory"] / 384:
            return str(scheduler_resources["cpu"] / 100)
    res = {
        "Memory": str(scheduler_resources["memory"] / 1024) + " GiB",
        "CPU": str(scheduler_resources["cpu"] / 1000) + " vCPU",
    }
    res_str = "{}, {}".format(res["CPU"], res["Memory"])
    return res_str


def calculate_worker_concurrency(env_vars: list[dict]) -> int:
    """Calculate worker concurrency for software."""
    concurrency = 16
    for env_var in env_vars:
        if env_var["key"] == "AIRFLOW__CELERY__WORKER_CONCURRENCY":
            return int(env_var["value"])
    return concurrency


def calculate_worker_type(worker_resources: dict) -> dict:
    """Calculate worker type for software."""
    worker_type = {
        "machinetype": "",  # Software doesn't have machine type
        "Memory": str(worker_resources["memory"] / 1024) + " GiB",
        "CPU": str(worker_resources["cpu"] / 1000) + " vCPU",
    }
    return worker_type
