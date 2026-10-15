from pathlib import Path

import pandas as pd
import pytest

from ai_security.config import ModelConfig, RuleConfig
from ai_security.features import build_features
from ai_security.ingestion import load_logs
from ai_security.model import train_and_score
from ai_security.reporting import build_report
from ai_security.rules import apply_rules


def test_failed_login_sequence_triggers_rule() -> None:
    logs = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                [f"2026-10-15T08:0{i}:00Z" for i in range(6)], utc=True
            ),
            "source_ip": ["203.0.113.50"] * 6,
            "user": ["admin"] * 6,
            "event_type": ["login"] * 6,
            "outcome": ["failure"] * 6,
            "bytes_transferred": [100] * 6,
            "destination": ["vpn-gateway"] * 6,
        }
    )
    features = build_features(logs, window_minutes=5)
    result = apply_rules(features, RuleConfig(failed_login_threshold=5))

    assert result.iloc[4]["rule_alert"]
    assert "repeated_failed_login" in result.iloc[4]["triggered_rules"]


def test_pipeline_scores_and_reports_records() -> None:
    count = 20
    logs = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-10-15T08:00:00Z", periods=count, freq="min"),
            "source_ip": [f"10.0.0.{i % 4 + 1}" for i in range(count)],
            "user": ["analyst"] * count,
            "event_type": ["api_request"] * count,
            "outcome": ["success"] * count,
            "bytes_transferred": [1000] * 19 + [5_000_000],
            "destination": ["web-api"] * count,
        }
    )
    features = build_features(logs, window_minutes=5)
    ruled = apply_rules(features, RuleConfig())
    scored, _ = train_and_score(ruled, ModelConfig(contamination=0.1))
    report = build_report(scored)

    assert len(report) == count
    assert report["model_alert"].any()
    assert report["alert"].equals(report["model_alert"] | report["rule_alert"])


def test_ingestion_rejects_missing_columns(tmp_path: Path) -> None:
    path = tmp_path / "invalid.csv"
    pd.DataFrame({"timestamp": ["2026-10-15T08:00:00Z"]}).to_csv(
        path, index=False
    )

    with pytest.raises(ValueError, match="Missing required columns"):
        load_logs(path)

