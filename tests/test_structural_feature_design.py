"""结构特征方案设计测试。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from scania_aps.features.structural_feature_design import (
    DESIGN_COLUMNS,
    build_structural_feature_design_table,
    load_structural_feature_config,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_structural_features_yaml_is_readable() -> None:
    """structural_features.yaml 应能被 yaml.safe_load 正常读取。"""

    config_path = PROJECT_ROOT / "config" / "structural_features.yaml"
    with config_path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    assert "structural_features" in config
    assert "candidate_prefix_groups" in config["structural_features"]


def test_generated_design_table_contains_required_columns() -> None:
    """生成后的 Day 12 设计表应包含必要列。"""

    output_path = PROJECT_ROOT / "outputs" / "tables" / "day12_structural_feature_design_table.csv"
    design_table = pd.read_csv(output_path)

    assert set(DESIGN_COLUMNS).issubset(design_table.columns)
    assert "sample_missing_count" in set(design_table["feature_name"])
    assert "sample_zero_count" in set(design_table["feature_name"])
    assert {
        "prefix_ag_zero_rate",
        "prefix_ay_zero_rate",
    }.intersection(set(design_table["feature_name"]))
    assert (design_table["feature_family"] == "selected_missing_indicators").any()


def test_build_structural_feature_design_table_with_mock_data() -> None:
    """设计表生成逻辑不依赖真实模型训练。"""

    structural_config = load_structural_feature_config(
        PROJECT_ROOT / "config" / "structural_features.yaml"
    )
    missing_zero_summary = pd.DataFrame(
        {
            "dataset": ["train_inner", "train_inner"],
            "feature_name": ["br_000", "ag_000"],
            "missing_rate": [0.8, 0.02],
            "zero_rate": [0.1, 0.5],
        }
    )
    pos_neg_diff = pd.DataFrame(
        {
            "feature_name": ["br_000", "ag_000"],
            "missing_rate_diff_abs": [0.7, 0.01],
        }
    )
    prefix_group_summary = pd.DataFrame(
        {
            "prefix": ["ag", "ay", "cn", "az", "cs", "ba", "ee"],
            "feature_names": [
                "ag_000,ag_001",
                "ay_000,ay_001",
                "cn_000,cn_001",
                "az_000,az_001",
                "cs_000,cs_001",
                "ba_000,ba_001",
                "ee_000,ee_001",
            ],
        }
    )

    design_table = build_structural_feature_design_table(
        missing_zero_summary=missing_zero_summary,
        pos_neg_diff=pos_neg_diff,
        prefix_group_summary=prefix_group_summary,
        structural_config=structural_config,
    )

    assert set(DESIGN_COLUMNS).issubset(design_table.columns)
    assert "missing_br_000" in set(design_table["feature_name"])
    assert "prefix_ag_missing_count" in set(design_table["feature_name"])
    assert "prefix_ay_zero_rate" in set(design_table["feature_name"])
