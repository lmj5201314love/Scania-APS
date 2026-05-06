"""Scania APS 成本敏感评估工具。"""

from __future__ import annotations

from typing import Any

from sklearn.metrics import confusion_matrix


def calculate_aps_cost(y_true: Any, y_pred: Any, cfg: Any) -> dict[str, int | float]:
    """根据 APS 业务成本计算混淆矩阵和总成本。

    FP/FN 成本必须来自配置对象，避免在评估逻辑中写死业务参数。
    """

    matrix = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = matrix.ravel()

    false_positive_cost = cfg.false_positive_cost
    false_negative_cost = cfg.false_negative_cost
    total_cost = fp * false_positive_cost + fn * false_negative_cost

    return {
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "false_positive_cost": false_positive_cost,
        "false_negative_cost": false_negative_cost,
        "total_cost": total_cost,
    }
