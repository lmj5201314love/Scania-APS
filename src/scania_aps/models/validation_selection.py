"""基于 validation set 的模型、缺失策略和阈值选择。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from scania_aps.config import ScaniaConfig
from scania_aps.data.clean_data import BaselineData, prepare_baseline_data
from scania_aps.evaluation.metrics import evaluate_binary_classifier
from scania_aps.evaluation.threshold_utils import (
    build_threshold_summary,
    evaluate_threshold_grid,
)
from scania_aps.models.train_advanced import (
    build_xgboost_model,
    calculate_scale_pos_weight,
)
from scania_aps.models.train_baseline import build_logistic_regression_model


DEFAULT_MODEL_NAMES = ["logistic_regression_balanced", "xgboost_scale_pos_weight"]
DEFAULT_STRATEGIES = ["median_all", "drop_high_missing_median"]


def _positive_class_proba(model: Any, X: pd.DataFrame) -> np.ndarray:
    """提取正类预测概率。"""

    if not hasattr(model, "predict_proba"):
        raise ValueError("候选模型必须支持 predict_proba，才能做阈值分析。")

    proba = model.predict_proba(X)
    classes = list(getattr(model, "classes_", []))
    positive_index = classes.index(1) if 1 in classes else proba.shape[1] - 1
    return proba[:, positive_index]


def _build_model(model_name: str, cfg: ScaniaConfig, y_train: pd.Series) -> Any:
    """根据模型名称构建候选模型。"""

    if model_name == "logistic_regression_balanced":
        return build_logistic_regression_model(cfg)

    if model_name == "xgboost_scale_pos_weight":
        scale_pos_weight = calculate_scale_pos_weight(y_train)
        return build_xgboost_model(cfg, scale_pos_weight=scale_pos_weight)

    raise ValueError(f"不支持的候选模型：{model_name}")


def _prediction_frame(
    *,
    dataset: str,
    source_index: pd.Index,
    y_true: pd.Series,
    y_proba: np.ndarray,
    threshold: float,
    model_name: str,
    strategy: str,
) -> pd.DataFrame:
    """整理预测概率输出表。"""

    y_pred = (y_proba >= threshold).astype(int)
    return pd.DataFrame(
        {
            "dataset": dataset,
            "sample_id": source_index.to_numpy() + 1,
            "y_true": y_true.to_numpy(),
            "y_proba": y_proba,
            "y_pred": y_pred,
            "model_name": model_name,
            "strategy": strategy,
            "threshold": threshold,
        }
    )


def train_candidates_on_validation(
    train_inner_df: pd.DataFrame,
    valid_df: pd.DataFrame,
    cfg: ScaniaConfig,
    strategies: Iterable[str] | None = None,
    model_names: Iterable[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """在 train_inner 训练候选模型，并在 valid 上输出阈值网格和预测概率。"""

    strategies = list(strategies or DEFAULT_STRATEGIES)
    model_names = list(model_names or DEFAULT_MODEL_NAMES)
    threshold_results: list[pd.DataFrame] = []
    prediction_results: list[pd.DataFrame] = []

    for strategy in strategies:
        prepared = prepare_baseline_data(
            train_df=train_inner_df,
            test_df=valid_df,
            cfg=cfg,
            strategy=strategy,
        )

        for model_name in model_names:
            if model_name == "xgboost_scale_pos_weight" and strategy == "median_with_indicator":
                continue

            model = _build_model(model_name, cfg, prepared.y_train)
            model.fit(prepared.X_train_processed, prepared.y_train)
            y_proba = _positive_class_proba(model, prepared.X_test_processed)

            threshold_df = evaluate_threshold_grid(
                y_true=prepared.y_test,
                y_proba=y_proba,
                cfg=cfg,
                model_name=model_name,
                strategy=strategy,
            )
            threshold_df["dataset"] = "valid"
            threshold_df["n_features"] = len(prepared.feature_names)
            threshold_df["n_dropped_features"] = len(prepared.dropped_features)
            threshold_results.append(threshold_df)

            prediction_results.append(
                _prediction_frame(
                    dataset="valid",
                    source_index=valid_df.index,
                    y_true=prepared.y_test,
                    y_proba=y_proba,
                    threshold=cfg.default_threshold,
                    model_name=model_name,
                    strategy=strategy,
                )
            )

    return (
        pd.concat(threshold_results, ignore_index=True),
        pd.concat(prediction_results, ignore_index=True),
    )


def build_validation_best_summary(validation_threshold_metrics: pd.DataFrame) -> pd.DataFrame:
    """基于 valid total_cost 汇总每个模型和策略的最佳阈值。"""

    summary = build_threshold_summary(validation_threshold_metrics)
    summary.insert(0, "selection_rank", range(1, len(summary) + 1))
    summary["selection_dataset"] = "valid"
    return summary


def evaluate_selected_model_on_official_test(
    train_inner_df: pd.DataFrame,
    test_df: pd.DataFrame,
    cfg: ScaniaConfig,
    best_row: pd.Series,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """使用 valid 选出的模型/策略/阈值，在官方 test 上评估一次。"""

    model_name = str(best_row["model_name"])
    strategy = str(best_row["strategy"])
    threshold = float(best_row["best_threshold"])

    prepared = prepare_baseline_data(
        train_df=train_inner_df,
        test_df=test_df,
        cfg=cfg,
        strategy=strategy,
    )
    model = _build_model(model_name, cfg, prepared.y_train)
    model.fit(prepared.X_train_processed, prepared.y_train)
    y_proba = _positive_class_proba(model, prepared.X_test_processed)
    y_pred = (y_proba >= threshold).astype(int)

    metric = evaluate_binary_classifier(
        y_true=prepared.y_test,
        y_pred=y_pred,
        y_proba=y_proba,
        cfg=cfg,
        model_name=model_name,
        strategy=strategy,
        threshold=threshold,
    )
    metric["dataset"] = "official_test"
    metric["threshold_source"] = "validation"
    metric["n_features"] = len(prepared.feature_names)
    metric["n_dropped_features"] = len(prepared.dropped_features)

    predictions = _prediction_frame(
        dataset="official_test",
        source_index=test_df.index,
        y_true=prepared.y_test,
        y_proba=y_proba,
        threshold=threshold,
        model_name=model_name,
        strategy=strategy,
    )

    return pd.DataFrame([metric]), predictions


def compare_with_day6_backtest(
    final_test_evaluation: pd.DataFrame,
    day6_best_summary_path: str | Path,
) -> pd.DataFrame:
    """对比 valid 选阈值后的 test 结果和 Day 6 test 回溯最优结果。"""

    day6_summary = pd.read_csv(day6_best_summary_path)
    day6_best = day6_summary.sort_values(
        ["total_cost", "recall", "f2"],
        ascending=[True, False, False],
    ).iloc[0]
    valid_selected = final_test_evaluation.iloc[0]

    return pd.DataFrame(
        [
            {
                "comparison_item": "validation_selected_on_test",
                "model_name": valid_selected["model_name"],
                "strategy": valid_selected["strategy"],
                "threshold": valid_selected["threshold"],
                "precision": valid_selected["precision"],
                "recall": valid_selected["recall"],
                "f2": valid_selected["f2"],
                "fp": int(valid_selected["fp"]),
                "fn": int(valid_selected["fn"]),
                "total_cost": valid_selected["total_cost"],
            },
            {
                "comparison_item": "day6_test_backtest_best",
                "model_name": day6_best["model_name"],
                "strategy": day6_best["strategy"],
                "threshold": day6_best["best_threshold"],
                "precision": day6_best["precision"],
                "recall": day6_best["recall"],
                "f2": day6_best["f2"],
                "fp": int(day6_best["fp"]),
                "fn": int(day6_best["fn"]),
                "total_cost": day6_best["total_cost"],
            },
            {
                "comparison_item": "delta_valid_minus_day6",
                "model_name": None,
                "strategy": None,
                "threshold": None,
                "precision": valid_selected["precision"] - day6_best["precision"],
                "recall": valid_selected["recall"] - day6_best["recall"],
                "f2": valid_selected["f2"] - day6_best["f2"],
                "fp": int(valid_selected["fp"]) - int(day6_best["fp"]),
                "fn": int(valid_selected["fn"]) - int(day6_best["fn"]),
                "total_cost": valid_selected["total_cost"] - day6_best["total_cost"],
            },
        ]
    )


def run_validation_model_selection(
    train_inner_df: pd.DataFrame,
    valid_df: pd.DataFrame,
    test_df: pd.DataFrame,
    cfg: ScaniaConfig,
    day6_best_summary_path: str | Path,
    strategies: Iterable[str] | None = None,
    model_names: Iterable[str] | None = None,
) -> dict[str, pd.DataFrame]:
    """运行 validation-based model selection 完整流程。"""

    validation_threshold_metrics, validation_predictions = train_candidates_on_validation(
        train_inner_df=train_inner_df,
        valid_df=valid_df,
        cfg=cfg,
        strategies=strategies,
        model_names=model_names,
    )
    validation_best_summary = build_validation_best_summary(validation_threshold_metrics)
    best_row = validation_best_summary.iloc[0]

    final_test_evaluation, final_test_predictions = evaluate_selected_model_on_official_test(
        train_inner_df=train_inner_df,
        test_df=test_df,
        cfg=cfg,
        best_row=best_row,
    )
    comparison = compare_with_day6_backtest(
        final_test_evaluation=final_test_evaluation,
        day6_best_summary_path=day6_best_summary_path,
    )

    return {
        "validation_threshold_metrics": validation_threshold_metrics,
        "validation_best_summary": validation_best_summary,
        "final_test_evaluation": final_test_evaluation,
        "comparison_with_day6_backtest": comparison,
        "validation_predictions": validation_predictions,
        "final_test_predictions": final_test_predictions,
    }
