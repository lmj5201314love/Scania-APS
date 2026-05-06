"""Day 4 baseline 模型训练与评估。"""

from __future__ import annotations

from typing import Sequence

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from scania_aps.config import ScaniaConfig
from scania_aps.data.clean_data import prepare_baseline_data
from scania_aps.evaluation.metrics import evaluate_binary_classifier


def build_dummy_model() -> DummyClassifier:
    """构建只学习标签先验分布的 Dummy baseline。"""

    return DummyClassifier(strategy="prior")


def build_logistic_regression_model(cfg: ScaniaConfig) -> Pipeline:
    """构建带标准化的 Logistic Regression baseline。"""

    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "model",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=cfg.random_state,
                ),
            ),
        ]
    )


def _positive_class_proba(model, X: pd.DataFrame) -> np.ndarray | None:
    """提取正类概率。"""

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
    """使用默认阈值生成预测结果。"""

    y_proba = _positive_class_proba(model, X)
    if y_proba is None:
        y_pred = model.predict(X)
    else:
        y_pred = (y_proba >= threshold).astype(int)

    return y_pred, y_proba


def train_and_evaluate_baselines(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    cfg: ScaniaConfig,
    strategies: Sequence[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """训练并评估 Day 4 baseline 模型。"""

    metrics_rows: list[dict] = []
    predictions: list[pd.DataFrame] = []
    threshold = cfg.default_threshold

    for strategy in strategies:
        prepared = prepare_baseline_data(
            train_df=train_df,
            test_df=test_df,
            cfg=cfg,
            strategy=strategy,
        )

        model_builders = [
            ("dummy_prior", build_dummy_model),
            ("logistic_regression_balanced", lambda: build_logistic_regression_model(cfg)),
        ]

        for model_name, build_model in model_builders:
            model = build_model()
            model.fit(prepared.X_train_processed, prepared.y_train)

            y_pred, y_proba = _predict_with_threshold(
                model=model,
                X=prepared.X_test_processed,
                threshold=threshold,
            )

            metric = evaluate_binary_classifier(
                y_true=prepared.y_test,
                y_pred=y_pred,
                y_proba=y_proba,
                cfg=cfg,
                model_name=model_name,
                strategy=strategy,
                threshold=threshold,
            )
            metric["dataset"] = "test"
            metric["n_features"] = len(prepared.feature_names)
            metric["n_dropped_features"] = len(prepared.dropped_features)
            metrics_rows.append(metric)

            prediction_df = pd.DataFrame(
                {
                    "dataset": "test",
                    "sample_id": np.arange(1, len(prepared.y_test) + 1),
                    "y_true": prepared.y_test.to_numpy(),
                    "y_proba": y_proba if y_proba is not None else np.nan,
                    "y_pred": y_pred,
                    "model_name": model_name,
                    "strategy": strategy,
                    "threshold": threshold,
                }
            )
            predictions.append(prediction_df)

    metrics_df = pd.DataFrame(metrics_rows)
    predictions_df = pd.concat(predictions, ignore_index=True)
    return metrics_df, predictions_df
