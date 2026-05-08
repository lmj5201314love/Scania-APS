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
    "Critical": "立即检修",
    "High": "优先检修",
    "Medium": "观察复查",
    "Low": "暂不处理",
}

RISK_LEVEL_ORDER = ["Critical", "High", "Medium", "Low"]


def assign_risk_level(y_proba: Any, best_threshold: float) -> pd.Series:
    """根据预测概率和低成本阈值划分风险等级。"""

    proba = pd.Series(y_proba, dtype="float64")
    if not 0 <= best_threshold <= 1:
        raise ValueError("best_threshold 必须位于 0 到 1 之间。")

    levels = np.select(
        [
            proba >= 0.80,
            (proba >= best_threshold) & (proba < 0.80),
            (proba >= 0.05) & (proba < best_threshold),
            proba < 0.05,
        ],
        ["Critical", "High", "Medium", "Low"],
        default="Unknown",
    )
    return pd.Series(levels, index=proba.index)


def assign_suggested_action(risk_level: Any) -> pd.Series | str:
    """根据风险等级给出维修动作建议。"""

    if isinstance(risk_level, str):
        return ACTION_MAPPING.get(risk_level, "人工复核")

    levels = pd.Series(risk_level)
    return levels.map(ACTION_MAPPING).fillna("人工复核")


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
