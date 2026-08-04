"""输出文件 schema 轻量检查。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from scania_aps.models.train_advanced import build_prediction_frame


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
    """Day 5 预测生成接口应包含 validation 对比所需基础字段。"""

    predictions = build_prediction_frame(
        dataset="test",
        y_true=pd.Series([1, 0]),
        y_proba=pd.Series([0.9, 0.1]),
        y_pred=pd.Series([1, 0]),
        model_name="schema_test_model",
        strategy="schema_test_strategy",
        threshold=0.18,
    )

    assert predictions.columns.tolist() == [
        "dataset",
        "sample_id",
        "y_true",
        "y_proba",
        "y_pred",
        "model_name",
        "strategy",
        "threshold",
    ]
    assert predictions["sample_id"].tolist() == [1, 2]


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
