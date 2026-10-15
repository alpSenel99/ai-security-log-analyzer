from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .config import ModelConfig
from .features import FEATURE_COLUMNS


def train_and_score(
    features: pd.DataFrame, config: ModelConfig
) -> tuple[pd.DataFrame, Pipeline]:
    if len(features) < 10:
        raise ValueError("At least 10 log records are required for anomaly modeling")

    pipeline = Pipeline(
        [
            ("scale", StandardScaler()),
            (
                "model",
                IsolationForest(
                    contamination=config.contamination,
                    random_state=config.random_state,
                ),
            ),
        ]
    )
    matrix = features[FEATURE_COLUMNS]
    predictions = pipeline.fit_predict(matrix)
    scored = features.copy()
    scored["anomaly_score"] = -pipeline.decision_function(matrix)
    scored["model_alert"] = predictions == -1
    return scored, pipeline


def save_model(pipeline: Pipeline, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": pipeline, "features": FEATURE_COLUMNS}, path)

