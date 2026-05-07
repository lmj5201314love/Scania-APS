"""阈值成本敏感分析工具。"""

from __future__ import annotations

from typing import Any, Iterable

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    fbeta_score,
    precision_score,
    recall_score,
)

from scania_aps.evaluation.cost_utils import calculate_aps_cost


THRESHOLD_COLUMNS = [
    "model_name",
    "strategy",
    "threshold",
    "precision",
    "recall",
    "f1",
    "f2",
    "average_precision",
    "tn",
    "fp",
    "fn",
    "tp",
    "false_positive_cost",
    "false_negative_cost",
    "total_cost",
]


def _default_thresholds() -> np.ndarray:
    """生成默认阈值网格。"""

    return np.round(np.arange(0.01, 1.00, 0.01), 2)


def evaluate_threshold_grid(
    y_true: Any,
    y_proba: Any,
    cfg: Any,
    model_name: str,
    strategy: str,
    thresholds: Iterable[float] | None = None,
) -> pd.DataFrame:
    """遍历阈值并计算分类指标和业务成本。"""

    if y_proba is None:
        return pd.DataFrame(columns=THRESHOLD_COLUMNS)

    y_true_series = pd.Series(y_true).reset_index(drop=True)
    y_proba_series = pd.Series(y_proba).reset_index(drop=True)
    valid_mask = y_true_series.notna() & y_proba_series.notna()

    if not valid_mask.any():
        return pd.DataFrame(columns=THRESHOLD_COLUMNS)

    y_true_array = y_true_series.loc[valid_mask].astype(int).to_numpy()
    y_proba_array = y_proba_series.loc[valid_mask].astype(float).to_numpy()
    threshold_values = list(thresholds) if thresholds is not None else _default_thresholds()
    average_precision = average_precision_score(y_true_array, y_proba_array)

    rows: list[dict[str, Any]] = []
    for threshold in threshold_values:
        threshold = float(threshold)
        y_pred = (y_proba_array >= threshold).astype(int)
        cost_result = calculate_aps_cost(y_true_array, y_pred, cfg)
        rows.append(
            {
                "model_name": model_name,
                "strategy": strategy,
                "threshold": threshold,
                "precision": precision_score(y_true_array, y_pred, zero_division=0),
                "recall": recall_score(y_true_array, y_pred, zero_division=0),
                "f1": f1_score(y_true_array, y_pred, zero_division=0),
                "f2": fbeta_score(y_true_array, y_pred, beta=2, zero_division=0),
                "average_precision": average_precision,
                **cost_result,
            }
        )

    return pd.DataFrame(rows, columns=THRESHOLD_COLUMNS)


def find_best_threshold(
    threshold_df: pd.DataFrame,
    sort_by: str = "total_cost",
) -> pd.Series:
    """选择低成本阈值；成本相同则优先 recall 和 F2 更高。"""

    if threshold_df.empty:
        return pd.Series(dtype="object")
    if sort_by not in threshold_df.columns:
        raise ValueError(f"threshold_df 缺少排序字段：{sort_by}")

    sorted_df = threshold_df.sort_values(
        by=[sort_by, "recall", "f2"],
        ascending=[True, False, False],
    )
    return sorted_df.iloc[0]


def build_threshold_summary(all_threshold_results: pd.DataFrame) -> pd.DataFrame:
    """汇总每个模型和策略的低成本阈值。"""

    if all_threshold_results.empty:
        return pd.DataFrame(
            columns=[
                "model_name",
                "strategy",
                "best_threshold",
                "precision",
                "recall",
                "f1",
                "f2",
                "fp",
                "fn",
                "total_cost",
                "average_precision",
            ]
        )

    rows = []
    for (model_name, strategy), group in all_threshold_results.groupby(
        ["model_name", "strategy"],
        dropna=False,
    ):
        best = find_best_threshold(group)
        rows.append(
            {
                "model_name": model_name,
                "strategy": strategy,
                "best_threshold": best["threshold"],
                "precision": best["precision"],
                "recall": best["recall"],
                "f1": best["f1"],
                "f2": best["f2"],
                "fp": int(best["fp"]),
                "fn": int(best["fn"]),
                "total_cost": best["total_cost"],
                "average_precision": best["average_precision"],
            }
        )

    return pd.DataFrame(rows).sort_values(
        ["total_cost", "recall", "f2"],
        ascending=[True, False, False],
    )
