"""字段级分布诊断工具测试。"""

from __future__ import annotations

import pandas as pd
import pandas.testing as pdt

from scania_aps.analysis.distribution_diagnostics import (
    build_feature_distribution_summary,
    build_missing_zero_summary,
    build_pos_neg_distribution_diff,
    build_train_valid_test_drift_summary,
    get_numeric_feature_columns,
)


def _sample_df() -> pd.DataFrame:
    """构造小型模拟数据。"""

    return pd.DataFrame(
        {
            "class": ["neg", "neg", "pos", "pos"],
            "target": [0, 0, 1, 1],
            "f1": [0.0, 1.0, 10.0, None],
            "f2": [5.0, 5.0, 5.0, 5.0],
            "text_col": ["a", "b", "c", "d"],
        }
    )


def test_get_numeric_feature_columns_excludes_label_and_target() -> None:
    """数值字段列表不应包含 class 和 target。"""

    df = _sample_df()

    feature_cols = get_numeric_feature_columns(df, label_col="class")

    assert feature_cols == ["f1", "f2"]


def test_build_feature_distribution_summary_outputs_required_columns() -> None:
    """字段分布统计应输出必要字段且不修改输入。"""

    df = _sample_df()
    original = df.copy(deep=True)

    summary = build_feature_distribution_summary(df, ["f1", "f2"], "train_inner")

    required_cols = {
        "dataset",
        "feature_name",
        "non_missing_count",
        "missing_count",
        "missing_rate",
        "zero_rate",
        "median",
        "p99",
        "skew",
        "unique_count",
    }
    assert required_cols.issubset(summary.columns)
    assert summary.shape[0] == 2
    pdt.assert_frame_equal(df, original)


def test_build_missing_zero_summary_rates() -> None:
    """缺失率和零值率应按总行数计算。"""

    df = _sample_df()

    summary = build_missing_zero_summary(df, ["f1"], "train_inner")
    row = summary.iloc[0]

    assert row["missing_rate"] == 0.25
    assert row["zero_rate"] == 0.25
    assert row["near_zero_rate"] == 0.25
    assert row["non_missing_count"] == 3


def test_build_pos_neg_distribution_diff_outputs_differences() -> None:
    """pos/neg 差异统计应包含缺失率、零值率和分位数差异。"""

    df = _sample_df()

    diff = build_pos_neg_distribution_diff(df, ["f1"], label_col="class")
    row = diff.iloc[0]

    assert row["feature_name"] == "f1"
    assert row["missing_rate_diff_abs"] == 0.5
    assert row["zero_rate_diff_abs"] == 0.5
    assert row["median_diff_abs"] > 0


def test_build_train_valid_test_drift_summary_outputs_drift() -> None:
    """train/valid/test 漂移统计应输出 train/test 差异。"""

    train = pd.DataFrame({"f1": [0.0, 1.0, None]})
    valid = pd.DataFrame({"f1": [0.0, 2.0, 2.0]})
    test = pd.DataFrame({"f1": [10.0, None, 20.0]})
    original_train = train.copy(deep=True)

    drift = build_train_valid_test_drift_summary(train, valid, test, ["f1"])
    row = drift.iloc[0]

    assert row["feature_name"] == "f1"
    assert row["train_test_missing_diff_abs"] == 0.0
    assert row["train_test_median_diff_abs"] == 14.5
    pdt.assert_frame_equal(train, original_train)
