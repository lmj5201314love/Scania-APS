"""项目配置读取工具。

统一从 config/config.yaml 读取路径、标签、缺失值 token、业务成本、评估指标和模型参数。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


def find_project_root(start: Path | None = None) -> Path:
    """向上查找包含 config/config.yaml 的项目根目录。"""

    current = (start or Path.cwd()).resolve()

    for path in [current, *current.parents]:
        if (path / "config" / "config.yaml").exists():
            return path

    raise FileNotFoundError("未找到 config/config.yaml，请确认当前路径在项目目录内。")


def load_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """读取 YAML 配置文件，返回原始 dict。"""

    if config_path is None:
        project_root = find_project_root()
        config_path = project_root / "config" / "config.yaml"
    else:
        config_path = Path(config_path).resolve()
        project_root = config_path.parents[1]

    with Path(config_path).open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    config["_project_root"] = project_root
    return config


@dataclass(frozen=True)
class ScaniaConfig:
    """项目常用配置对象。"""

    project_root: Path
    train_raw: Path
    test_raw: Path
    interim_dir: Path
    processed_dir: Path
    figures_dir: Path
    metrics_dir: Path
    predictions_dir: Path
    tables_dir: Path
    reports_dir: Path
    label_column: str
    missing_value_token: str
    positive_label: str
    negative_label: str
    target_mapping: dict[str, int]
    false_positive_cost: int
    false_negative_cost: int
    primary_metrics: list[str]
    random_state: int
    default_threshold: float
    high_missing_threshold: float
    validation_valid_size: float
    validation_stratify: bool
    feature_ablation: dict[str, Any]
    advanced_models: dict[str, Any]
    xgb_tuning: dict[str, Any]
    oof_threshold: dict[str, Any]


def _require_sections(config: dict[str, Any], sections: list[str]) -> None:
    """校验必要配置段存在。"""

    missing = [section for section in sections if section not in config]
    if missing:
        raise ValueError(f"config.yaml 缺少必要配置段：{missing}")


def _resolve_project_path(project_root: Path, value: str | Path) -> Path:
    """将项目相对路径转换为绝对路径。"""

    path = Path(value)
    return path if path.is_absolute() else project_root / path


def _validate_probability(value: Any, name: str) -> None:
    """校验 0 到 1 之间的比例参数。"""

    if not isinstance(value, (int, float)) or not 0 < float(value) < 1:
        raise ValueError(f"{name} 必须是 0 到 1 之间的数值。")


def _validate_config(raw_config: dict[str, Any], project_root: Path) -> None:
    """执行轻量配置校验。"""

    if not raw_config:
        raise ValueError("config.yaml 为空或无法解析。")

    _require_sections(
        raw_config,
        [
            "paths",
            "data",
            "business_cost",
            "evaluation",
            "model",
            "validation",
            "feature_ablation",
            "advanced_models",
            "xgb_tuning",
            "oof_threshold",
        ],
    )

    train_raw = _resolve_project_path(project_root, raw_config["paths"]["train_raw"])
    test_raw = _resolve_project_path(project_root, raw_config["paths"]["test_raw"])
    if not train_raw.exists():
        raise FileNotFoundError(f"训练集路径不存在：{train_raw}")
    if not test_raw.exists():
        raise FileNotFoundError(f"测试集路径不存在：{test_raw}")

    false_positive_cost = raw_config["business_cost"]["false_positive"]
    false_negative_cost = raw_config["business_cost"]["false_negative"]
    if not isinstance(false_positive_cost, (int, float)):
        raise TypeError("false_positive_cost 必须是数值。")
    if not isinstance(false_negative_cost, (int, float)):
        raise TypeError("false_negative_cost 必须是数值。")

    target_mapping = raw_config["data"]["target_mapping"]
    positive_label = raw_config["data"]["positive_label"]
    negative_label = raw_config["data"]["negative_label"]
    if positive_label not in target_mapping or negative_label not in target_mapping:
        raise ValueError("target_mapping 必须包含 positive_label 和 negative_label。")

    _validate_probability(raw_config["validation"]["valid_size"], "validation.valid_size")

    feature_ablation = raw_config["feature_ablation"]
    if "missing_thresholds" not in feature_ablation:
        raise ValueError("feature_ablation 必须包含 missing_thresholds 配置。")
    for name, threshold in feature_ablation["missing_thresholds"].items():
        _validate_probability(threshold, f"feature_ablation.missing_thresholds.{name}")

    correlation_threshold = feature_ablation.get("correlation_threshold")
    _validate_probability(correlation_threshold, "feature_ablation.correlation_threshold")

    advanced_models = raw_config["advanced_models"]
    if "random_forest" not in advanced_models or "xgboost" not in advanced_models:
        raise ValueError("advanced_models 必须包含 random_forest 和 xgboost 配置。")

    xgb_tuning = raw_config["xgb_tuning"]
    if xgb_tuning.get("tuning_mode") != "two_stage_random_search":
        raise ValueError("xgb_tuning.tuning_mode 必须是 two_stage_random_search。")
    if not xgb_tuning.get("candidate_strategies"):
        raise ValueError("xgb_tuning 必须配置 candidate_strategies。")
    for key in ["broad_trials_per_strategy", "refine_trials_per_strategy"]:
        if int(xgb_tuning[key]) <= 0:
            raise ValueError(f"xgb_tuning.{key} 必须大于 0。")
    threshold_grid = xgb_tuning["threshold_grid"]
    for key in ["start", "stop", "step"]:
        if float(threshold_grid[key]) <= 0:
            raise ValueError(f"xgb_tuning.threshold_grid.{key} 必须大于 0。")
    if float(threshold_grid["start"]) >= float(threshold_grid["stop"]):
        raise ValueError("xgb_tuning.threshold_grid.start 必须小于 stop。")
    oof_threshold = raw_config["oof_threshold"]
    cv_config = oof_threshold["cv"]
    if int(cv_config["n_splits"]) < 2:
        raise ValueError("oof_threshold.cv.n_splits must be >= 2.")
    if int(cv_config["n_repeats"]) < 1:
        raise ValueError("oof_threshold.cv.n_repeats must be >= 1.")
    oof_grid = oof_threshold["threshold_grid"]
    for key in ["start", "stop", "step"]:
        if float(oof_grid[key]) <= 0:
            raise ValueError(f"oof_threshold.threshold_grid.{key} must be > 0.")
    if float(oof_grid["start"]) >= float(oof_grid["stop"]):
        raise ValueError("oof_threshold.threshold_grid.start must be smaller than stop.")


def get_config(config_path: str | Path | None = None) -> ScaniaConfig:
    """读取并整理项目配置。"""

    raw_config = load_config(config_path)
    project_root = raw_config["_project_root"]
    _validate_config(raw_config, project_root)

    return ScaniaConfig(
        project_root=project_root,
        train_raw=_resolve_project_path(project_root, raw_config["paths"]["train_raw"]),
        test_raw=_resolve_project_path(project_root, raw_config["paths"]["test_raw"]),
        interim_dir=_resolve_project_path(project_root, raw_config["paths"]["interim_dir"]),
        processed_dir=_resolve_project_path(project_root, raw_config["paths"]["processed_dir"]),
        figures_dir=_resolve_project_path(project_root, raw_config["paths"]["figures_dir"]),
        metrics_dir=_resolve_project_path(project_root, raw_config["paths"]["metrics_dir"]),
        predictions_dir=_resolve_project_path(
            project_root,
            raw_config["paths"]["predictions_dir"],
        ),
        tables_dir=_resolve_project_path(project_root, raw_config["paths"]["tables_dir"]),
        reports_dir=_resolve_project_path(project_root, raw_config["paths"]["reports_dir"]),
        label_column=raw_config["data"]["label_column"],
        missing_value_token=raw_config["data"]["missing_value_token"],
        positive_label=raw_config["data"]["positive_label"],
        negative_label=raw_config["data"]["negative_label"],
        target_mapping=raw_config["data"]["target_mapping"],
        false_positive_cost=raw_config["business_cost"]["false_positive"],
        false_negative_cost=raw_config["business_cost"]["false_negative"],
        primary_metrics=raw_config["evaluation"]["primary_metrics"],
        random_state=raw_config["model"]["random_state"],
        default_threshold=raw_config["model"]["default_threshold"],
        high_missing_threshold=raw_config["model"]["high_missing_threshold"],
        validation_valid_size=float(raw_config["validation"]["valid_size"]),
        validation_stratify=bool(raw_config["validation"]["stratify"]),
        feature_ablation=raw_config["feature_ablation"],
        advanced_models=raw_config["advanced_models"],
        xgb_tuning=raw_config["xgb_tuning"],
        oof_threshold=raw_config["oof_threshold"],
    )
