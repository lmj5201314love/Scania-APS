"""二分类 baseline 评估指标。"""

from __future__ import annotations

from typing import Any

from sklearn.metrics import (
    average_precision_score,
    f1_score,
    fbeta_score,
    precision_score,
    recall_score,
)

from scania_aps.evaluation.cost_utils import calculate_aps_cost


def evaluate_binary_classifier(
    y_true: Any,
    y_pred: Any,
    y_proba: Any = None,
    cfg: Any = None,
    model_name: str | None = None,
    strategy: str | None = None,
    threshold: float | None = None,
) -> dict[str, Any]:
    """评估二分类模型，重点输出召回、F2、PR-AUC 和业务总成本。"""

    if cfg is None:
        raise ValueError("cfg 不能为空，成本敏感评估需要从配置读取 FP/FN 成本。")

    cost_result = calculate_aps_cost(y_true=y_true, y_pred=y_pred, cfg=cfg)

    result: dict[str, Any] = {
        "model_name": model_name,
        "strategy": strategy,
        "threshold": threshold,
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "f2": fbeta_score(y_true, y_pred, beta=2, zero_division=0),
        "average_precision": None,
    }

    if y_proba is not None:
        result["average_precision"] = average_precision_score(y_true, y_proba)

    result.update(cost_result)
    return result
