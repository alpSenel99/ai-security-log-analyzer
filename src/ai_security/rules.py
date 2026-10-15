import pandas as pd

from .config import RuleConfig


def apply_rules(features: pd.DataFrame, config: RuleConfig) -> pd.DataFrame:
    result = features.copy()

    def triggered(row: pd.Series) -> list[str]:
        rules: list[str] = []
        if row["failures_in_window"] >= config.failed_login_threshold:
            rules.append("repeated_failed_login")
        if row["events_in_window"] >= config.request_burst_threshold:
            rules.append("request_burst")
        if config.unusual_hour_start <= row["hour"] <= config.unusual_hour_end:
            rules.append("unusual_hour")
        return rules

    result["triggered_rules"] = result.apply(
        lambda row: ",".join(triggered(row)), axis=1
    )
    result["rule_alert"] = result["triggered_rules"].ne("")
    return result

