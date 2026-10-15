from pathlib import Path

import pandas as pd


REPORT_COLUMNS = [
    "timestamp",
    "source_ip",
    "user",
    "event_type",
    "outcome",
    "destination",
    "events_in_window",
    "failures_in_window",
    "failure_ratio_in_window",
    "unique_destinations_in_window",
    "anomaly_score",
    "model_alert",
    "rule_alert",
    "triggered_rules",
    "alert",
]


def build_report(scored: pd.DataFrame) -> pd.DataFrame:
    report = scored.copy()
    report["alert"] = report["model_alert"] | report["rule_alert"]
    return report[REPORT_COLUMNS].sort_values(
        ["alert", "anomaly_score"], ascending=[False, False]
    )


def save_report(report: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".json":
        report.to_json(path, orient="records", date_format="iso", indent=2)
    elif path.suffix.lower() == ".csv":
        report.to_csv(path, index=False)
    else:
        raise ValueError("Report extension must be .csv or .json")

