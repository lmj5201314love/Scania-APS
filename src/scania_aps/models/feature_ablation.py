"""缺失值与特征工程消融实验。"""

from __future__ import annotations

from typing import Any, Iterable

import numpy as np
import pandas as pd

from scania_aps.config import ScaniaConfig
from scania_aps.evaluation.metrics import evaluate_binary_classifier
from scania_aps.evaluation.threshold_utils import (
    build_threshold_summary,
    evaluate_threshold_grid,
)
from scania_aps.features.build_features import FeatureData, prepare_feature_ablation_data
from scania_aps.models.train_advanced import (
    build_xgboost_model,
    calculate_scale_pos_weight,
)
from scania_aps.models.train_baseline import build_logistic_regression_model


DEFAULT_MODELS = ["logistic_regression_balanced", "xgboost_scale_pos_weight"]


def _positive_class_proba(model: Any, X: pd.DataFrame) -> np.ndarray:
    """提取正类预测概率。"""

    if not hasattr(model, "predict_proba"):
        raise ValueError("消融实验候选模型必须支持 predict_proba。")

    proba = model.predict_proba(X)
    classes = list(getattr(model, "classes_", []))
    positive_index = classes.index(1) if 1 in classes else proba.shape[1] - 1
    return proba[:, positive_index]


def _build_model(model_name: str, cfg: ScaniaConfig, y_train: pd.Series) -> Any:
    """按模型名构建模型。"""

    if model_name == "logistic_regression_balanced":
        return build_logistic_regression_model(cfg)

    if model_name == "xgboost_scale_pos_weight":
        scale_pos_weight = calculate_scale_pos_weight(y_train)
        return build_xgboost_model(cfg, scale_pos_weight=scale_pos_weight)

    raise ValueError(f"不支持的模型：{model_name}")


def _is_supported_combination(strategy: str, model_name: str) -> bool:
    """判断策略和模型组合是否支持。"""

    if strategy == "xgb_native_missing" and model_name != "xgboost_scale_pos_weight":
        return False
    if strategy == "l1_feature_selection" and model_name != "logistic_regression_balanced":
        return False
    return True


def _metadata_row(model_name: str, feature_data: FeatureData) -> dict[str, Any]:
    """整理策略元数据。"""

    row = {
        "model_name": model_name,
        "strategy": feature_data.strategy,
        "n_features": len(feature_data.feature_names),
        "n_dropped_features": len(feature_data.dropped_features),
        "dropped_features": "|".join(feature_data.dropped_features),
    }
    row.update(feature_data.strategy_metadata)
    return row


def _evaluate_on_test(
    *,
    model: Any,
    feature_data: FeatureData,
    cfg: ScaniaConfig,
    model_name: str,
    best_threshold: float,
) -> dict[str, Any]:
    """使用 valid 选出的阈值，在 official test 上评估。"""

    y_proba = _positive_class_proba(model, feature_data.X_test_processed)
    y_pred = (y_proba >= best_threshold).astype(int)
    metric = evaluate_binary_classifier(
        y_true=feature_data.y_test,
        y_pred=y_pred,
        y_proba=y_proba,
        cfg=cfg,
        model_name=model_name,
        strategy=feature_data.strategy,
        threshold=best_threshold,
    )
    metric["dataset"] = "official_test"
    metric["threshold_source"] = "validation"
    metric["n_features"] = len(feature_data.feature_names)
    metric["n_dropped_features"] = len(feature_data.dropped_features)
    return metric


def _build_missing_indicator_signal_summary(
    valid_best_summary: pd.DataFrame,
    final_test_results: pd.DataFrame,
    valid_df: pd.DataFrame,
    test_df: pd.DataFrame,
) -> pd.DataFrame:
    """汇总 missing_indicator_only 是否携带预测信号。"""

    rows: list[dict[str, Any]] = []
    valid_pos_rate = valid_df["target"].mean()
    test_pos_rate = test_df["target"].mean()
    valid_missing = valid_best_summary[
        valid_best_summary["strategy"].eq("missing_indicator_only")
    ]
    test_missing = final_test_results[
        final_test_results["strategy"].eq("missing_indicator_only")
    ]

    for _, valid_row in valid_missing.iterrows():
        model_name = valid_row["model_name"]
        matched_test = test_missing[test_missing["model_name"].eq(model_name)]
        if matched_test.empty:
            continue
        test_row = matched_test.iloc[0]
        rows.append(
            {
                "model_name": model_name,
                "strategy": "missing_indicator_only",
                "valid_best_threshold": valid_row["best_threshold"],
                "valid_average_precision": valid_row["average_precision"],
                "valid_pos_rate": valid_pos_rate,
                "valid_total_cost": valid_row["total_cost"],
                "test_average_precision": test_row["average_precision"],
                "test_pos_rate": test_pos_rate,
                "test_recall": test_row["recall"],
                "test_f2": test_row["f2"],
                "test_fp": int(test_row["fp"]),
                "test_fn": int(test_row["fn"]),
                "test_total_cost": test_row["total_cost"],
                "signal_note": "AP 高于正类基准率，说明缺失模式本身存在一定信号",
            }
        )

    return pd.DataFrame(rows)


def run_feature_ablation_experiments(
    train_inner_df: pd.DataFrame,
    valid_df: pd.DataFrame,
    test_df: pd.DataFrame,
    cfg: ScaniaConfig,
    strategies: Iterable[str],
    model_names: Iterable[str] | None = None,
) -> dict[str, pd.DataFrame]:
    """运行缺失值与特征工程消融实验。"""

    model_names = list(model_names or DEFAULT_MODELS)
    valid_threshold_frames: list[pd.DataFrame] = []
    metadata_rows: list[dict[str, Any]] = []
    trained_models: dict[tuple[str, str], tuple[Any, FeatureData]] = {}

    for strategy in strategies:
        feature_data = prepare_feature_ablation_data(
            train_inner_df=train_inner_df,
            valid_df=valid_df,
            test_df=test_df,
            cfg=cfg,
            strategy=strategy,
        )

        for model_name in model_names:
            if not _is_supported_combination(strategy, model_name):
                continue

            model = _build_model(model_name, cfg, feature_data.y_train_inner)
            model.fit(feature_data.X_train_inner_processed, feature_data.y_train_inner)
            y_valid_proba = _positive_class_proba(model, feature_data.X_valid_processed)

            threshold_metrics = evaluate_threshold_grid(
                y_true=feature_data.y_valid,
                y_proba=y_valid_proba,
                cfg=cfg,
                model_name=model_name,
                strategy=strategy,
            )
            threshold_metrics["dataset"] = "valid"
            threshold_metrics["n_features"] = len(feature_data.feature_names)
            threshold_metrics["n_dropped_features"] = len(feature_data.dropped_features)
            valid_threshold_frames.append(threshold_metrics)

            metadata_rows.append(_metadata_row(model_name, feature_data))
            trained_models[(model_name, strategy)] = (model, feature_data)

    valid_threshold_metrics = pd.concat(valid_threshold_frames, ignore_index=True)
    valid_best_summary = build_threshold_summary(valid_threshold_metrics).reset_index(drop=True)
    valid_best_summary.insert(0, "selection_rank", range(1, len(valid_best_summary) + 1))

    metadata_df = pd.DataFrame(metadata_rows).drop_duplicates(["model_name", "strategy"])
    valid_best_summary = valid_best_summary.merge(
        metadata_df.drop(columns=["dropped_features"], errors="ignore"),
        on=["model_name", "strategy"],
        how="left",
    )

    final_rows: list[dict[str, Any]] = []
    for _, best_row in valid_best_summary.iterrows():
        key = (best_row["model_name"], best_row["strategy"])
        model, feature_data = trained_models[key]
        final_rows.append(
            _evaluate_on_test(
                model=model,
                feature_data=feature_data,
                cfg=cfg,
                model_name=best_row["model_name"],
                best_threshold=float(best_row["best_threshold"]),
            )
        )

    final_test_results = pd.DataFrame(final_rows).sort_values(
        ["total_cost", "recall", "f2"],
        ascending=[True, False, False],
    )
    missing_signal_summary = _build_missing_indicator_signal_summary(
        valid_best_summary=valid_best_summary,
        final_test_results=final_test_results,
        valid_df=valid_df,
        test_df=test_df,
    )

    return {
        "valid_threshold_metrics": valid_threshold_metrics,
        "valid_best_summary": valid_best_summary,
        "final_test_results": final_test_results,
        "strategy_metadata": metadata_df,
        "missing_indicator_signal_summary": missing_signal_summary,
    }
