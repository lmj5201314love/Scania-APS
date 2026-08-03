"""v1.0 发布契约测试。"""

from __future__ import annotations

import re
from copy import deepcopy
from pathlib import Path

import pytest
import pandas as pd
import yaml

from scania_aps.config import get_config, load_config, load_release_policy


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "config" / "config.yaml"
DAY14_METRICS_PATH = (
    PROJECT_ROOT / "outputs" / "metrics" / "day14_structural_feature_test_results.csv"
)
DAY14_METADATA_PATH = (
    PROJECT_ROOT / "outputs" / "tables" / "day14_structural_feature_test_metadata.csv"
)


def _valid_release_config() -> dict:
    return {
        "release": {
            "target_version": "1.0.0",
            "stage": "v1_0_release_candidate",
            "final_candidate": {
                "model_version": "day14_structural_all_final_candidate",
                "model_name": "xgboost_scale_pos_weight",
                "strategy": "median_all_structural_all",
                "decision_threshold": 0.18,
                "threshold_source": "day13_valid_best_summary",
                "score_semantics": "uncalibrated_risk_score",
            },
            "data_scope": {
                "fit_dataset": "train_inner",
                "fit_rows": 48000,
                "validation_dataset": "valid",
                "validation_rows": 12000,
                "evaluation_dataset": "official_test",
                "evaluation_rows": 16000,
            },
        }
    }


def _write_config(tmp_path: Path, config: dict) -> Path:
    config_dir = tmp_path / "config"
    config_dir.mkdir(exist_ok=True)
    config_path = config_dir / "config.yaml"
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    return config_path


def test_project_release_policy_freezes_v1_candidate_and_data_scope() -> None:
    """项目配置应公开唯一的 v1.0 候选方案和数据范围。"""

    policy = load_release_policy(CONFIG_PATH)
    raw_config = load_config(CONFIG_PATH)

    assert raw_config["project"]["stage"] == "v1_0_release_candidate"
    assert policy.target_version == "1.0.0"
    assert policy.stage == "v1_0_release_candidate"
    assert policy.model_version == "day14_structural_all_final_candidate"
    assert policy.model_name == "xgboost_scale_pos_weight"
    assert policy.strategy == "median_all_structural_all"
    assert policy.decision_threshold == 0.18
    assert policy.threshold_source == "day13_valid_best_summary"
    assert policy.score_semantics == "uncalibrated_risk_score"
    assert policy.fit_dataset == "train_inner"
    assert policy.fit_rows == 48000
    assert policy.validation_dataset == "valid"
    assert policy.validation_rows == 12000
    assert policy.evaluation_dataset == "official_test"
    assert policy.evaluation_rows == 16000
    assert "average_precision" in raw_config["evaluation"]["primary_metrics"]
    assert "pr_auc" not in raw_config["evaluation"]["primary_metrics"]
    assert raw_config["business_cost"] == {
        "false_positive": 10,
        "false_negative": 500,
    }
    assert raw_config["data"]["target_mapping"] == {"pos": 1, "neg": 0}


def test_release_policy_rejects_missing_final_candidate(tmp_path: Path) -> None:
    """缺少最终候选段时应给出可定位的配置错误。"""

    config = deepcopy(_valid_release_config())
    del config["release"]["final_candidate"]

    with pytest.raises(ValueError, match="release.final_candidate"):
        load_release_policy(_write_config(tmp_path, config))


def test_release_policy_rejects_missing_release_section(tmp_path: Path) -> None:
    """release 主段是 v1.0 配置的必要部分。"""

    with pytest.raises(ValueError, match="release"):
        load_release_policy(_write_config(tmp_path, {}))


@pytest.mark.parametrize(
    ("section", "field"),
    [
        ("release", "target_version"),
        ("release", "stage"),
        ("release.final_candidate", "model_version"),
        ("release.final_candidate", "model_name"),
        ("release.final_candidate", "strategy"),
        ("release.final_candidate", "decision_threshold"),
        ("release.final_candidate", "threshold_source"),
        ("release.final_candidate", "score_semantics"),
        ("release.data_scope", "fit_dataset"),
        ("release.data_scope", "fit_rows"),
        ("release.data_scope", "validation_dataset"),
        ("release.data_scope", "validation_rows"),
        ("release.data_scope", "evaluation_dataset"),
        ("release.data_scope", "evaluation_rows"),
    ],
)
def test_release_policy_reports_missing_required_fields_as_value_error(
    tmp_path: Path,
    section: str,
    field: str,
) -> None:
    """缺少任一必填字段时应返回包含完整路径的配置错误。"""

    config = deepcopy(_valid_release_config())
    section_values = config["release"]
    if section != "release":
        section_values = section_values[section.removeprefix("release.")]
    del section_values[field]

    with pytest.raises(ValueError, match=re.escape(f"{section}.{field}")):
        load_release_policy(_write_config(tmp_path, config))


@pytest.mark.parametrize(
    ("section", "field"),
    [
        ("release", "target_version"),
        ("release", "stage"),
        ("release.final_candidate", "model_version"),
        ("release.final_candidate", "model_name"),
        ("release.final_candidate", "strategy"),
        ("release.final_candidate", "decision_threshold"),
        ("release.final_candidate", "threshold_source"),
        ("release.final_candidate", "score_semantics"),
        ("release.data_scope", "fit_dataset"),
        ("release.data_scope", "fit_rows"),
        ("release.data_scope", "validation_dataset"),
        ("release.data_scope", "validation_rows"),
        ("release.data_scope", "evaluation_dataset"),
        ("release.data_scope", "evaluation_rows"),
    ],
)
def test_release_policy_rejects_null_required_fields(
    tmp_path: Path,
    section: str,
    field: str,
) -> None:
    """发布契约中的必填字段不得接受 YAML null。"""

    config = deepcopy(_valid_release_config())
    section_values = config["release"]
    if section != "release":
        section_values = section_values[section.removeprefix("release.")]
    section_values[field] = None

    with pytest.raises(ValueError, match=re.escape(f"{section}.{field}")):
        load_release_policy(_write_config(tmp_path, config))


def test_release_policy_rejects_threshold_outside_probability_range(
    tmp_path: Path,
) -> None:
    """最终决策阈值必须严格位于 0 到 1 之间。"""

    config = deepcopy(_valid_release_config())
    config["release"]["final_candidate"]["decision_threshold"] = 1.1

    with pytest.raises(ValueError, match="decision_threshold"):
        load_release_policy(_write_config(tmp_path, config))


def test_release_policy_rejects_empty_strategy(tmp_path: Path) -> None:
    """最终候选策略必须是非空文本。"""

    config = deepcopy(_valid_release_config())
    config["release"]["final_candidate"]["strategy"] = "  "

    with pytest.raises(ValueError, match="strategy"):
        load_release_policy(_write_config(tmp_path, config))


def test_release_policy_rejects_empty_model_version(tmp_path: Path) -> None:
    """最终候选模型版本必须是非空文本。"""

    config = deepcopy(_valid_release_config())
    config["release"]["final_candidate"]["model_version"] = ""

    with pytest.raises(ValueError, match="model_version"):
        load_release_policy(_write_config(tmp_path, config))


def test_release_policy_rejects_calibrated_probability_semantics(
    tmp_path: Path,
) -> None:
    """发布契约不得把当前模型分数声明为校准概率。"""

    config = deepcopy(_valid_release_config())
    config["release"]["final_candidate"]["score_semantics"] = (
        "calibrated_probability"
    )

    with pytest.raises(ValueError, match="score_semantics"):
        load_release_policy(_write_config(tmp_path, config))


def test_release_policy_rejects_missing_data_scope(tmp_path: Path) -> None:
    """缺少数据范围段时应给出可定位的配置错误。"""

    config = deepcopy(_valid_release_config())
    del config["release"]["data_scope"]

    with pytest.raises(ValueError, match="release.data_scope"):
        load_release_policy(_write_config(tmp_path, config))


@pytest.mark.parametrize("row_field", ["fit_rows", "validation_rows", "evaluation_rows"])
def test_release_policy_requires_positive_integer_row_counts(
    tmp_path: Path,
    row_field: str,
) -> None:
    """训练、验证和评估行数都必须是正整数。"""

    config = deepcopy(_valid_release_config())
    config["release"]["data_scope"][row_field] = 0

    with pytest.raises(ValueError, match=row_field):
        load_release_policy(_write_config(tmp_path, config))


def test_release_policy_requires_full_official_train_partition(tmp_path: Path) -> None:
    """train_inner 与 valid 必须完整覆盖 60,000 行 official train。"""

    config = deepcopy(_valid_release_config())
    config["release"]["data_scope"]["fit_rows"] = 47000

    with pytest.raises(ValueError, match="fit_rows.*validation_rows"):
        load_release_policy(_write_config(tmp_path, config))


def test_release_policy_requires_16000_evaluation_rows(tmp_path: Path) -> None:
    """official test 的冻结评估范围必须是 16,000 行。"""

    config = deepcopy(_valid_release_config())
    config["release"]["data_scope"]["evaluation_rows"] = 15999

    with pytest.raises(ValueError, match="evaluation_rows"):
        load_release_policy(_write_config(tmp_path, config))


@pytest.mark.parametrize(
    ("dataset_field", "invalid_value"),
    [
        ("fit_dataset", "official_train"),
        ("validation_dataset", "validation"),
        ("evaluation_dataset", "test"),
    ],
)
def test_release_policy_rejects_non_frozen_dataset_names(
    tmp_path: Path,
    dataset_field: str,
    invalid_value: str,
) -> None:
    """发布契约必须保留冻结的训练、验证和公开评估数据集名称。"""

    config = deepcopy(_valid_release_config())
    config["release"]["data_scope"][dataset_field] = invalid_value

    with pytest.raises(ValueError, match=dataset_field):
        load_release_policy(_write_config(tmp_path, config))


def test_release_policy_matches_committed_day14_metrics() -> None:
    """冻结策略、阈值、指标和成本应与 Day14 最终结果一致。"""

    policy = load_release_policy(CONFIG_PATH)
    raw_config = load_config(CONFIG_PATH)
    metrics = pd.read_csv(DAY14_METRICS_PATH)
    final_rows = metrics.loc[metrics["strategy"].eq(policy.strategy)]

    assert len(final_rows) == 1
    assert "average_precision" in metrics.columns
    assert "pr_auc" not in metrics.columns

    result = final_rows.iloc[0]
    assert result["threshold"] == pytest.approx(policy.decision_threshold)
    assert result["model_name"] == policy.model_name
    assert result["precision"] == pytest.approx(0.47700394218134035)
    assert result["recall"] == pytest.approx(0.968)
    assert result["f2"] == pytest.approx(0.8027421494913755)
    assert result["average_precision"] == pytest.approx(0.9054549964028027)
    assert result["fp"] == 398
    assert result["fn"] == 12
    assert result["tp"] == 363
    assert result["tn"] == 15227
    assert result["total_cost"] == 9980
    assert result["total_cost"] == (
        result["fp"] * raw_config["business_cost"]["false_positive"]
        + result["fn"] * raw_config["business_cost"]["false_negative"]
    )


def _parse_artifact_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"true", "1"}:
        return True
    if normalized in {"false", "0"}:
        return False
    raise ValueError(f"无法解析布尔值：{value!r}")


def test_release_policy_matches_committed_day14_metadata() -> None:
    """训练范围、阈值来源和特征规模应与 Day14 metadata 一致。"""

    policy = load_release_policy(CONFIG_PATH)
    metadata = pd.read_csv(DAY14_METADATA_PATH)
    final_rows = metadata.loc[metadata["candidate_group"].eq(policy.strategy)]

    assert len(final_rows) == 1
    result = final_rows.iloc[0]
    assert result["model_name"] == policy.model_name
    assert result["fit_dataset"] == policy.fit_dataset
    assert result["train_inner_rows"] == policy.fit_rows
    assert result["valid_rows"] == policy.validation_rows
    assert result["evaluation_dataset"] == policy.evaluation_dataset
    assert result["official_test_rows"] == policy.evaluation_rows
    assert result["threshold_source"] == policy.threshold_source
    assert _parse_artifact_bool(result["uses_official_test_for_selection"]) is False
    assert result["n_original_features"] == 170
    assert result["n_structural_features"] == 60
    assert result["n_total_features"] == 230


def test_full_project_config_exposes_validated_release_policy(tmp_path: Path) -> None:
    """常规配置调用方应能从同一对象读取已校验的发布政策。"""

    config = deepcopy(load_config(CONFIG_PATH))
    config.pop("_project_root")
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True)
    (raw_dir / "aps_failure_training_set.csv").touch()
    (raw_dir / "aps_failure_test_set.csv").touch()

    config_path = _write_config(tmp_path, config)
    cfg = get_config(config_path)

    assert cfg.release == load_release_policy(config_path)
