"""输出文件 schema 轻量检查。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def _assert_columns_exist(path: Path, required_columns: set[str]) -> None:
    """检查 CSV 可读取且包含必要列。"""

    df = pd.read_csv(path, nrows=5)
    missing = required_columns - set(df.columns)
    assert not missing, f"{path} 缺少必要列：{missing}"


def test_day6_best_threshold_summary_schema() -> None:
    """Day 6 最优阈值摘要应包含后续对比所需字段。"""

    path = Path("outputs/metrics/day6_best_threshold_summary.csv")
    _assert_columns_exist(
        path,
        {
            "model_name",
            "strategy",
            "best_threshold",
            "precision",
            "recall",
            "f2",
            "fp",
            "fn",
            "total_cost",
        },
    )


def test_day5_prediction_schema() -> None:
    """Day 5 预测文件应包含 validation 对比所需基础字段。"""

    path = Path("outputs/predictions/day5_model_compare_predictions.csv")
    _assert_columns_exist(
        path,
        {
            "dataset",
            "sample_id",
            "y_true",
            "y_proba",
            "y_pred",
            "model_name",
            "strategy",
            "threshold",
        },
    )


def test_validation_outputs_schema_if_generated() -> None:
    """如果 validation 输出已生成，则检查其关键字段。"""

    path = Path("outputs/metrics/final_test_evaluation_from_valid_selection.csv")
    if not path.exists():
        return

    _assert_columns_exist(
        path,
        {
            "model_name",
            "strategy",
            "threshold",
            "precision",
            "recall",
            "f2",
            "fp",
            "fn",
            "total_cost",
        },
    )
