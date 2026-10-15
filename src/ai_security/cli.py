from pathlib import Path

import typer

from .config import load_config
from .features import build_features
from .ingestion import load_logs
from .model import save_model, train_and_score
from .reporting import build_report, save_report
from .rules import apply_rules


app = typer.Typer(help="Analyze security logs for anomalous activity.")


@app.callback()
def main() -> None:
    """Security log anomaly detection commands."""


@app.command()
def analyze(
    input_path: Path = typer.Argument(..., help="Input CSV log file"),
    config_path: Path = typer.Option(
        Path("configs/default.yaml"), "--config", help="YAML configuration"
    ),
    report_path: Path = typer.Option(
        Path("reports/anomalies.csv"), "--report", help="CSV or JSON report"
    ),
    model_path: Path = typer.Option(
        Path("artifacts/isolation_forest.joblib"), "--model", help="Saved model"
    ),
) -> None:
    """Train on a log file, score its records, and write a report."""
    try:
        config = load_config(config_path)
        logs = load_logs(input_path)
        features = build_features(logs, config.rules.window_minutes)
        ruled = apply_rules(features, config.rules)
        scored, pipeline = train_and_score(ruled, config.model)
        report = build_report(scored)
        save_report(report, report_path)
        save_model(pipeline, model_path)
    except (FileNotFoundError, ValueError) as error:
        typer.echo(f"Error: {error}", err=True)
        raise typer.Exit(code=1) from error

    alert_count = int(report["alert"].sum())
    typer.echo(f"Analyzed {len(report)} records; {alert_count} alerts found.")
    typer.echo(f"Report: {report_path}")
    typer.echo(f"Model: {model_path}")


if __name__ == "__main__":
    app()

