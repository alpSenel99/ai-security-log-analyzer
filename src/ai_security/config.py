from pathlib import Path

import yaml
from pydantic import BaseModel, Field, model_validator


class RuleConfig(BaseModel):
    window_minutes: int = Field(default=5, gt=0)
    failed_login_threshold: int = Field(default=5, gt=0)
    request_burst_threshold: int = Field(default=10, gt=0)
    unusual_hour_start: int = Field(default=0, ge=0, le=23)
    unusual_hour_end: int = Field(default=5, ge=0, le=23)

    @model_validator(mode="after")
    def validate_hour_range(self) -> "RuleConfig":
        if self.unusual_hour_start > self.unusual_hour_end:
            raise ValueError("unusual_hour_start must be <= unusual_hour_end")
        return self


class ModelConfig(BaseModel):
    contamination: float = Field(default=0.10, gt=0, le=0.5)
    random_state: int = 42


class AppConfig(BaseModel):
    rules: RuleConfig = RuleConfig()
    model: ModelConfig = ModelConfig()


def load_config(path: Path) -> AppConfig:
    with path.open("r", encoding="utf-8") as stream:
        raw = yaml.safe_load(stream) or {}
    return AppConfig.model_validate(raw)

