"""Day 5 提升模型训练与评估。"""

from __future__ import annotations

from typing import Sequence

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

from scania_aps.config import ScaniaConfig
from scania_aps.data.clean_data import prepare_baseline_data
from scania_aps.evaluation.metrics import evaluate_binary_classifier


def build_random_forest_model(cfg: ScaniaConfig) -> RandomForestClassifier:
    """基于 cfg 构建 Random Forest 提升模型。"""

    params = cfg.advanced_models["random_forest"]
    return RandomForestClassifier(
        n_estimators=params["n_estimators"],
        max_depth=params["max_depth"],
        min_samples_leaf=params["min_samples_leaf"],
        class_weight=params["class_weight"],
        n_jobs=params["n_jobs"],
        random_state=cfg.random_state,
    )


def calculate_scale_pos_weight(y_train: pd.Series) -> float:
    """计算 XGBoost 类别不平衡权重。"""

    pos_count = int((y_train == 1).sum())
    neg_count = int((y_train == 0).sum())
    if pos_count == 0:
        raise ValueError("训练集中没有正类样本，无法计算 scale_pos_weight。")

    return neg_count / pos_count


def build_xgboost_model(
    cfg: ScaniaConfig,
    scale_pos_weight: float | None = None,
) -> XGBClassifier:
    """基于 cfg 构建 XGBoost 提升模型。"""

    params = cfg.advanced_models["xgboost"]
    return XGBClassifier(
        n_estimators=params["n_estimators"],
        max_depth=params["max_depth"],
        learning_rate=params["learning_rate"],
        subsample=params["subsample"],
        colsample_bytree=params["colsample_bytree"],
        eval_metric=params["eval_metric"],
        n_jobs=params["n_jobs"],
        random_state=cfg.random_state,
        scale_pos_weight=scale_pos_weight,
    )


def _positive_class_proba(model, X: pd.DataFrame) -> np.ndarray | None:
    """提取正类预测概率。"""

    if not hasattr(model, "predict_proba"):
        return None

    proba = model.predict_proba(X)
    classes = list(getattr(model, "classes_", []))
    if 1 in classes:
        positive_index = classes.index(1)
    else:
        positive_index = proba.shape[1] - 1

    return proba[:, positive_index]


def _predict_with_threshold(
    model,
    X: pd.DataFrame,
    threshold: float,
) -> tuple[np.ndarray, np.ndarray | None]:
    """使用 cfg 默认阈值生成预测结果。"""

    y_proba = _positive_class_proba(model, X)
    if y_proba is None:
        y_pred = model.predict(X)
    else:
        y_pred = (y_proba >= threshold).astype(int)

    return y_pred, y_proba


def build_prediction_frame(
    *,
    dataset: str,
    y_true: Sequence[int] | np.ndarray | pd.Series,
    y_proba: Sequence[float] | np.ndarray | pd.Series | None,
    y_pred: Sequence[int] | np.ndarray | pd.Series,
    model_name: str,
    strategy: str,
    threshold: float,
) -> pd.DataFrame:
    """构造 Day 5 模型对比使用的样本级预测表。"""

    y_true_values = np.asarray(y_true)
    probability_values = (
        np.asarray(y_proba)
        if y_proba is not None
        else np.full(len(y_true_values), np.nan)
    )
    return pd.DataFrame(
        {
            "dataset": dataset,
            "sample_id": np.arange(1, len(y_true_values) + 1),
            "y_true": y_true_values,
            "y_proba": probability_values,
            "y_pred": np.asarray(y_pred),
            "model_name": model_name,
            "strategy": strategy,
            "threshold": threshold,
        }
    )


def _append_model_result(
    metrics_rows: list[dict],
    predictions: list[pd.DataFrame],
    *,
    model,
    model_name: str,
    strategy: str,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    cfg: ScaniaConfig,
    n_features: int,
    n_dropped_features: int,
) -> None:
    """评估模型并收集指标和预测结果。"""

    threshold = cfg.default_threshold
    y_pred, y_proba = _predict_with_threshold(
        model=model,
        X=X_test,
        threshold=threshold,
    )

    metric = evaluate_binary_classifier(
        y_true=y_test,
        y_pred=y_pred,
        y_proba=y_proba,
        cfg=cfg,
        model_name=model_name,
        strategy=strategy,
        threshold=threshold,
    )
    metric["dataset"] = "test"
    metric["n_features"] = n_features
    metric["n_dropped_features"] = n_dropped_features
    metrics_rows.append(metric)

    predictions.append(
        build_prediction_frame(
            dataset="test",
            y_true=y_test,
            y_proba=y_proba,
            y_pred=y_pred,
            model_name=model_name,
            strategy=strategy,
            threshold=threshold,
        )
    )


def train_and_evaluate_advanced_models(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    cfg: ScaniaConfig,
    strategies: Sequence[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """训练并评估 Day 5 Random Forest / XGBoost 模型。"""

    metrics_rows: list[dict] = []
    predictions: list[pd.DataFrame] = []

    for strategy in strategies:
        prepared = prepare_baseline_data(
            train_df=train_df,
            test_df=test_df,
            cfg=cfg,
            strategy=strategy,
        )

        if strategy in ["median_all", "drop_high_missing_median", "median_with_indicator"]:
            random_forest = build_random_forest_model(cfg)
            random_forest.fit(prepared.X_train_processed, prepared.y_train)
            _append_model_result(
                metrics_rows,
                predictions,
                model=random_forest,
                model_name="random_forest_balanced",
                strategy=strategy,
                X_test=prepared.X_test_processed,
                y_test=prepared.y_test,
                cfg=cfg,
                n_features=len(prepared.feature_names),
                n_dropped_features=len(prepared.dropped_features),
            )

        if strategy in ["median_all", "drop_high_missing_median"]:
            scale_pos_weight = calculate_scale_pos_weight(prepared.y_train)
            xgboost = build_xgboost_model(cfg, scale_pos_weight=scale_pos_weight)
            xgboost.fit(prepared.X_train_processed, prepared.y_train)
            _append_model_result(
                metrics_rows,
                predictions,
                model=xgboost,
                model_name="xgboost_scale_pos_weight",
                strategy=strategy,
                X_test=prepared.X_test_processed,
                y_test=prepared.y_test,
                cfg=cfg,
                n_features=len(prepared.feature_names),
                n_dropped_features=len(prepared.dropped_features),
            )

    metrics_df = pd.DataFrame(metrics_rows)
    predictions_df = pd.concat(predictions, ignore_index=True)
    return metrics_df, predictions_df
