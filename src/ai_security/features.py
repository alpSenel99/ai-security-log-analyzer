from datetime import timedelta

import numpy as np
import pandas as pd


FEATURE_COLUMNS = [
    "events_in_window",
    "failures_in_window",
    "failure_ratio_in_window",
    "unique_destinations_in_window",
    "bytes_transferred",
    "hour",
]


def build_features(logs: pd.DataFrame, window_minutes: int) -> pd.DataFrame:
    """Create backward-looking per-IP features without using future events."""
    result = logs.copy().sort_values("timestamp").reset_index(drop=True)
    result["is_failure"] = result["outcome"].eq("failure").astype(int)
    result["events_in_window"] = 0
    result["failures_in_window"] = 0
    result["unique_destinations_in_window"] = 0

    window = timedelta(minutes=window_minutes)
    for _, indexes in result.groupby("source_ip", sort=False).groups.items():
        active: list[int] = []
        for index in indexes:
            cutoff = result.at[index, "timestamp"] - window
            active = [i for i in active if result.at[i, "timestamp"] >= cutoff]
            active.append(index)
            result.at[index, "events_in_window"] = len(active)
            result.at[index, "failures_in_window"] = int(
                result.loc[active, "is_failure"].sum()
            )
            result.at[index, "unique_destinations_in_window"] = int(
                result.loc[active, "destination"].nunique()
            )

    result["failure_ratio_in_window"] = (
        result["failures_in_window"] / result["events_in_window"]
    )
    result["hour"] = result["timestamp"].dt.hour
    result["bytes_transferred"] = np.log1p(result["bytes_transferred"])
    return result

