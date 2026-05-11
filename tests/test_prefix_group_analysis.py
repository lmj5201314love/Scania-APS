"""前缀组结构信号分析测试。"""

from __future__ import annotations

import pandas as pd
import pandas.testing as pdt
import pytest

from scania_aps.analysis.prefix_group_analysis import (
    add_prefix_column,
    build_prefix_group_signal_ranking,
    build_prefix_group_summary,
    extract_feature_prefix,
)


def _mock_day10_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """构造小型 Day 10 输出表。"""

    distribution = pd.DataFrame(
        {
            "dataset": ["train_inner", "train_inner", "train_inner"],
            "feature_name": ["ag_000", "ag_001", "br_000"],
            "skew": [2.0, 4.0, 10.0],
            "p99_to_median_ratio": [3.0, 5.0, 8.0],
            "max_to_p99_ratio": [1.2, 1.5, 2.0],
        }
    )
    missing_zero = pd.DataFrame(
        {
            "dataset": ["train_inner", "train_inner", "train_inner"],
            "feature_name": ["ag_000", "ag_001", "br_000"],
            "missing_rate": [0.1, 0.2, 0.8],
            "zero_rate": [0.5, 0.7, 0.1],
            "near_zero_rate": [0.5, 0.7, 0.1],
            "non_missing_count": [9, 8, 2],
        }
    )
    pos_neg_diff = pd.DataFrame(
        {
            "feature_name": ["ag_000", "ag_001", "br_000"],
            "missing_rate_diff_abs": [0.1, 0.2, 0.7],
            "zero_rate_diff_abs": [0.3, 0.4, 0.1],
        }
    )
    drift = pd.DataFrame(
        {
            "feature_name": ["ag_000", "ag_001", "br_000"],
            "train_test_missing_diff_abs": [0.01, 0.02, 0.03],
            "train_test_p99_diff_abs": [100.0, 200.0, 300.0],
        }
    )
    return distribution, missing_zero, pos_neg_diff, drift


def test_extract_feature_prefix() -> None:
    """字段前缀提取应按下划线前部分返回。"""

    assert extract_feature_prefix("ag_000") == "ag"
    assert extract_feature_prefix("br_000") == "br"
    assert extract_feature_prefix("ec_00") == "ec"
    assert extract_feature_prefix("abc") == "ab"
    assert extract_feature_prefix("x") == "x"


def test_add_prefix_column_does_not_modify_original() -> None:
    """新增 prefix 列不应修改原始 DataFrame。"""

    df = pd.DataFrame({"feature_name": ["ag_000", "br_000"]})
    original = df.copy(deep=True)

    result = add_prefix_column(df)

    assert result["prefix"].tolist() == ["ag", "br"]
    assert "prefix" not in df.columns
    pdt.assert_frame_equal(df, original)


def test_build_prefix_group_summary_aggregates_by_prefix() -> None:
    """prefix summary 应能按前缀聚合字段数量和均值指标。"""

    distribution, missing_zero, pos_neg_diff, drift = _mock_day10_tables()

    summary = build_prefix_group_summary(distribution, missing_zero, pos_neg_diff, drift)
    ag_row = summary[summary["prefix"].eq("ag")].iloc[0]

    assert ag_row["feature_count"] == 2
    assert ag_row["feature_names"] == "ag_000,ag_001"
    assert ag_row["avg_missing_rate"] == pytest.approx(0.15)
    assert ag_row["avg_zero_rate"] == pytest.approx(0.6)
    assert {"avg_abs_skew", "avg_train_test_p99_diff"}.issubset(summary.columns)


def test_build_prefix_group_signal_ranking_outputs_recommendation() -> None:
    """signal ranking 应每个 prefix 一行，并输出推荐说明。"""

    distribution, missing_zero, pos_neg_diff, drift = _mock_day10_tables()
    summary = build_prefix_group_summary(distribution, missing_zero, pos_neg_diff, drift)

    ranking = build_prefix_group_signal_ranking(summary)

    assert set(ranking["prefix"]) == {"ag", "br"}
    assert "signal_score" in ranking.columns
    assert "recommendation" in ranking.columns
    assert ranking["recommendation"].notna().all()
