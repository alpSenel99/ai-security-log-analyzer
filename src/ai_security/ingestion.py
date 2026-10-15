from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "timestamp",
    "source_ip",
    "user",
    "event_type",
    "outcome",
    "bytes_transferred",
    "destination",
}


def load_logs(path: Path) -> pd.DataFrame:
    """Load a CSV log file and validate its basic schema."""
    if not path.exists():
        raise FileNotFoundError(f"Log file not found: {path}")

    frame = pd.read_csv(path)
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    if frame.empty:
        raise ValueError("Log file contains no records")

    frame = frame.copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True, errors="coerce")
    frame["bytes_transferred"] = pd.to_numeric(
        frame["bytes_transferred"], errors="coerce"
    )

    invalid = frame["timestamp"].isna() | frame["bytes_transferred"].isna()
    if invalid.any():
        rows = ", ".join(str(index + 2) for index in frame.index[invalid])
        raise ValueError(f"Invalid timestamp or bytes_transferred at CSV rows: {rows}")
    if (frame["bytes_transferred"] < 0).any():
        raise ValueError("bytes_transferred cannot be negative")

    text_columns = ["source_ip", "user", "event_type", "outcome", "destination"]
    if frame[text_columns].isna().any().any():
        raise ValueError("Text fields cannot be empty")
    for column in text_columns:
        frame[column] = frame[column].astype(str).str.strip().str.lower()
        if frame[column].eq("").any():
            raise ValueError(f"{column} cannot be empty")

    valid_outcomes = {"success", "failure"}
    unknown = set(frame["outcome"]).difference(valid_outcomes)
    if unknown:
        raise ValueError(f"Unknown outcomes: {', '.join(sorted(unknown))}")

    return frame.sort_values("timestamp").reset_index(drop=True)

