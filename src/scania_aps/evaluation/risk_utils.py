"""风险分层和维修优先级工具。"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


REQUIRED_PREDICTION_COLUMNS = {
    "sample_id",
    "y_true",
    "y_proba",
    "model_name",
    "strategy",
}

ACTION_MAPPING = {
    "Critical": "immediate_aps_inspection",
    "High": "priority_aps_inspection",
    "Medium": "aps_recheck_or_additional_diagnosis",
    "Low": "continue_non_aps_diagnosis",
}

RISK_LEVEL_ORDER = ["Critical", "High", "Medium", "Low"]
CRITICAL_RISK_LOWER_BOUND = 0.80
MEDIUM_RISK_LOWER_BOUND = 0.05


def _validate_decision_threshold(value: Any) -> float:
    """校验决策阈值能形成互不重叠的四档风险区间。"""

    if isinstance(value, bool) or not isinstance(value, (int, float, np.number)):
        raise ValueError("decision_threshold 必须是数值。")
    threshold = float(value)
    if not np.isfinite(threshold) or not (
        MEDIUM_RISK_LOWER_BOUND < threshold < CRITICAL_RISK_LOWER_BOUND
    ):
        raise ValueError(
            "decision_threshold 必须大于 0.05 且小于 0.80。"
        )
    return threshold


def assign_risk_level(y_proba: Any, best_threshold: float) -> pd.Series:
    """根据风险分数和调用方传入的决策阈值划分风险等级。"""

    proba = pd.Series(y_proba, dtype="float64")
    decision_threshold = _validate_decision_threshold(best_threshold)

    levels = np.select(
        [
            proba >= CRITICAL_RISK_LOWER_BOUND,
            (proba >= decision_threshold) & (proba < CRITICAL_RISK_LOWER_BOUND),
            (proba >= MEDIUM_RISK_LOWER_BOUND) & (proba < decision_threshold),
            proba < MEDIUM_RISK_LOWER_BOUND,
        ],
        ["Critical", "High", "Medium", "Low"],
        default="Unknown",
    )
    return pd.Series(levels, index=proba.index)


def assign_suggested_action(risk_level: Any) -> pd.Series | str:
    """根据风险等级给出维修动作建议。"""

    if isinstance(risk_level, str):
        return ACTION_MAPPING.get(risk_level, "manual_review")

    levels = pd.Series(risk_level)
    return levels.map(ACTION_MAPPING).fillna("manual_review")


def classify_prediction_type(y_true: Any, y_pred: Any) -> pd.Series:
    """将真实标签和预测标签映射为 TP / FP / TN / FN。"""

    true = pd.Series(y_true).astype(int)
    pred = pd.Series(y_pred).astype(int)
    if len(true) != len(pred):
        raise ValueError("y_true 和 y_pred 长度必须一致。")

    prediction_type = np.select(
        [
            (true == 1) & (pred == 1),
            (true == 0) & (pred == 1),
            (true == 0) & (pred == 0),
            (true == 1) & (pred == 0),
        ],
        ["TP", "FP", "TN", "FN"],
        default="Unknown",
    )
    return pd.Series(prediction_type, index=true.index)


def build_maintenance_priority_table(
    predictions_df: pd.DataFrame,
    best_threshold: float,
    model_name: str,
    strategy: str,
) -> pd.DataFrame:
    """生成维修优先级明细表。"""

    missing_cols = REQUIRED_PREDICTION_COLUMNS - set(predictions_df.columns)
    if missing_cols:
        raise ValueError(f"predictions_df 缺少必要字段：{sorted(missing_cols)}")

    result = predictions_df.copy().reset_index(drop=True)
    result["model_name"] = model_name
    result["strategy"] = strategy
    result["threshold"] = float(best_threshold)
    result["y_pred"] = (result["y_proba"] >= best_threshold).astype(int)
    result["prediction_type"] = classify_prediction_type(result["y_true"], result["y_pred"])
    result["risk_level"] = assign_risk_level(result["y_proba"], best_threshold)
    result["suggested_action"] = assign_suggested_action(result["risk_level"])

    output_columns = [
        "sample_id",
        "model_name",
        "strategy",
        "y_true",
        "y_proba",
        "threshold",
        "y_pred",
        "prediction_type",
        "risk_level",
        "suggested_action",
    ]
    return result[output_columns].sort_values(
        ["risk_level", "y_proba"],
        ascending=[True, False],
        key=lambda col: col.map({level: i for i, level in enumerate(RISK_LEVEL_ORDER)})
        if col.name == "risk_level"
        else col,
    )
