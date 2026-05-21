"""Day 14 结构特征候选方案 official test 最终观察。

本模块只对 Day 13 在 valid 上选出的少数候选方案做 official test 观察。
阈值和候选组必须来自 valid 结果；official test 不参与特征选择、阈值选择
或任何规则拟合。
"""

from __future__ import annotations

from typing import Any, Iterable

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer

from scania_aps.config import ScaniaConfig
from scania_aps.data.clean_data import split_features_target
from scania_aps.evaluation.metrics import evaluate_binary_classifier
from scania_aps.features.structural_features import (
    StructuralFeatureBuilder,
    fit_structural_feature_builder,
    transform_structural_features,
)
from scania_aps.models.train_advanced import (
    build_xgboost_model,
    calculate_scale_pos_weight,
)


DEFAULT_DAY14_CANDIDATE_GROUPS = [
    "baseline_median_all",
    "median_all_selected_missing_indicators_top30",
    "median_all_prefix_zero_rate",
    "median_all_structural_all",
]


def _positive_class_proba(model: Any, X: pd.DataFrame) -> np.ndarray:
    """提取正类预测概率。"""

    if not hasattr(model, "predict_proba"):
        raise ValueError("Day 14 official test 观察要求模型支持 predict_proba。")

    proba = model.predict_proba(X)
    classes = list(getattr(model, "classes_", []))
    positive_index = classes.index(1) if 1 in classes else proba.shape[1] - 1
    return proba[:, positive_index]


def _threshold_for_group(
    valid_best_summary: pd.DataFrame,
    candidate_group: str,
) -> float:
    """从 Day 13 valid best summary 读取候选组阈值。"""

    if "strategy" not in valid_best_summary.columns:
        raise ValueError("valid_best_summary 缺少 strategy 列。")
    if "best_threshold" not in valid_best_summary.columns:
        raise ValueError("valid_best_summary 缺少 best_threshold 列。")

    matched = valid_best_summary[valid_best_summary["strategy"].eq(candidate_group)]
    if matched.empty:
        raise ValueError(f"valid_best_summary 中找不到候选组：{candidate_group}")
    return float(matched.iloc[0]["best_threshold"])


def _prepare_median_all_train_test_with_structural_features(
    train_inner_df: pd.DataFrame,
    test_df: pd.DataFrame,
    cfg: ScaniaConfig,
    structural_config: dict[str, Any],
    candidate_group: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, StructuralFeatureBuilder, dict[str, Any]]:
    """在 train_inner 上 fit 原始特征 median imputer 和结构特征规则，再 transform test。"""

    X_train, y_train = split_features_target(train_inner_df, cfg.label_column)
    X_test, y_test = split_features_target(test_df, cfg.label_column)

    imputer = SimpleImputer(strategy="median")
    X_train_original = pd.DataFrame(
        imputer.fit_transform(X_train),
        columns=X_train.columns.tolist(),
        index=X_train.index,
    )
    X_test_original = pd.DataFrame(
        imputer.transform(X_test),
        columns=X_train.columns.tolist(),
        index=X_test.index,
    )

    builder = fit_structural_feature_builder(
        train_inner_df=train_inner_df,
        cfg=cfg,
        structural_config=structural_config,
        feature_group=candidate_group,
    )
    X_train_structural = transform_structural_features(train_inner_df, builder)
    X_test_structural = transform_structural_features(test_df, builder)

    X_train_processed = pd.concat([X_train_original, X_train_structural], axis=1)
    X_test_processed = pd.concat([X_test_original, X_test_structural], axis=1)

    metadata = {
        "candidate_group": candidate_group,
        "model_name": "xgboost_scale_pos_weight",
        "base_strategy": "median_all",
        "fit_dataset": "train_inner",
        "evaluation_dataset": "official_test",
        "threshold_source": "day13_valid_best_summary",
        "uses_official_test_for_selection": False,
        "n_original_features": X_train_original.shape[1],
        "n_structural_features": X_train_structural.shape[1],
        "n_total_features": X_train_processed.shape[1],
        "structural_feature_names": "|".join(X_train_structural.columns.tolist()),
        "selected_missing_indicator_columns": "|".join(
            builder.selected_missing_indicator_columns
        ),
        "prefix_zero_groups": "|".join(builder.prefix_zero_members.keys()),
        "prefix_missing_groups": "|".join(builder.prefix_missing_members.keys()),
    }
    if builder.metadata:
        metadata.update(builder.metadata)

    return (
        X_train_processed,
        X_test_processed,
        y_train.copy(),
        y_test.copy(),
        builder,
        metadata,
    )


def _prediction_frame(
    *,
    test_df: pd.DataFrame,
    y_true: pd.Series,
    y_proba: np.ndarray,
    threshold: float,
    candidate_group: str,
) -> pd.DataFrame:
    """整理 official test 预测明细。"""

    y_pred = (y_proba >= threshold).astype(int)
    return pd.DataFrame(
        {
            "dataset": "official_test",
            "sample_id": test_df.index.to_numpy() + 1,
            "y_true": y_true.to_numpy(),
            "y_proba": y_proba,
            "y_pred": y_pred,
            "model_name": "xgboost_scale_pos_weight",
            "strategy": candidate_group,
            "candidate_group": candidate_group,
            "threshold": threshold,
            "threshold_source": "day13_valid_best_summary",
        }
    )


def _compare_valid_test(
    valid_best_summary: pd.DataFrame,
    test_results: pd.DataFrame,
    candidate_groups: list[str],
) -> pd.DataFrame:
    """对比 Day 13 valid best 结果和 Day 14 official test 结果。"""

    valid_cols = [
        "strategy",
        "best_threshold",
        "precision",
        "recall",
        "f1",
        "f2",
        "average_precision",
        "fp",
        "fn",
        "total_cost",
    ]
    valid = valid_best_summary[valid_best_summary["strategy"].isin(candidate_groups)][
        valid_cols
    ].copy()
    valid = valid.rename(
        columns={
            "strategy": "candidate_group",
            "best_threshold": "threshold",
            "precision": "valid_precision",
            "recall": "valid_recall",
            "f1": "valid_f1",
            "f2": "valid_f2",
            "average_precision": "valid_average_precision",
            "fp": "valid_fp",
            "fn": "valid_fn",
            "total_cost": "valid_total_cost",
        }
    )

    test = test_results[
        [
            "candidate_group",
            "threshold",
            "precision",
            "recall",
            "f1",
            "f2",
            "average_precision",
            "fp",
            "fn",
            "total_cost",
        ]
    ].copy()
    test = test.rename(
        columns={
            "precision": "test_precision",
            "recall": "test_recall",
            "f1": "test_f1",
            "f2": "test_f2",
            "average_precision": "test_average_precision",
            "fp": "test_fp",
            "fn": "test_fn",
            "total_cost": "test_total_cost",
        }
    )

    comparison = valid.merge(
        test,
        on=["candidate_group", "threshold"],
        how="left",
    )
    comparison["delta_total_cost_test_minus_valid"] = (
        comparison["test_total_cost"] - comparison["valid_total_cost"]
    )
    comparison["delta_fn_test_minus_valid"] = comparison["test_fn"] - comparison["valid_fn"]
    comparison["delta_fp_test_minus_valid"] = comparison["test_fp"] - comparison["valid_fp"]
    comparison["delta_recall_test_minus_valid"] = (
        comparison["test_recall"] - comparison["valid_recall"]
    )
    comparison["delta_f2_test_minus_valid"] = comparison["test_f2"] - comparison["valid_f2"]
    comparison["note"] = (
        "test 仅用于最终观察；不允许根据该表反向修改候选组或阈值"
    )
    return comparison.sort_values(
        ["test_total_cost", "test_recall", "test_f2"],
        ascending=[True, False, False],
    ).reset_index(drop=True)


def evaluate_structural_feature_candidates_on_test(
    train_inner_df: pd.DataFrame,
    valid_df: pd.DataFrame,
    test_df: pd.DataFrame,
    cfg: ScaniaConfig,
    structural_config: dict[str, Any],
    candidate_groups: Iterable[str],
    valid_best_summary: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """使用 Day 13 valid 阈值，在 official test 上观察固定候选方案。"""

    groups = list(candidate_groups)
    test_metric_rows: list[dict[str, Any]] = []
    prediction_frames: list[pd.DataFrame] = []
    metadata_rows: list[dict[str, Any]] = []

    for candidate_group in groups:
        threshold = _threshold_for_group(valid_best_summary, candidate_group)
        (
            X_train_processed,
            X_test_processed,
            y_train,
            y_test,
            _builder,
            metadata,
        ) = _prepare_median_all_train_test_with_structural_features(
            train_inner_df=train_inner_df,
            test_df=test_df,
            cfg=cfg,
            structural_config=structural_config,
            candidate_group=candidate_group,
        )

        scale_pos_weight = calculate_scale_pos_weight(y_train)
        model = build_xgboost_model(cfg, scale_pos_weight=scale_pos_weight)
        model.fit(X_train_processed, y_train)
        y_test_proba = _positive_class_proba(model, X_test_processed)
        y_test_pred = (y_test_proba >= threshold).astype(int)

        metric = evaluate_binary_classifier(
            y_true=y_test,
            y_pred=y_test_pred,
            y_proba=y_test_proba,
            cfg=cfg,
            model_name="xgboost_scale_pos_weight",
            strategy=candidate_group,
            threshold=threshold,
        )
        metric.update(
            {
                "dataset": "official_test",
                "candidate_group": candidate_group,
                "threshold_source": "day13_valid_best_summary",
                "n_original_features": metadata["n_original_features"],
                "n_structural_features": metadata["n_structural_features"],
                "n_total_features": metadata["n_total_features"],
            }
        )
        test_metric_rows.append(metric)

        prediction_frames.append(
            _prediction_frame(
                test_df=test_df,
                y_true=y_test,
                y_proba=y_test_proba,
                threshold=threshold,
                candidate_group=candidate_group,
            )
        )
        metadata["threshold"] = threshold
        metadata["train_inner_rows"] = len(train_inner_df)
        metadata["valid_rows"] = len(valid_df)
        metadata["official_test_rows"] = len(test_df)
        metadata_rows.append(metadata)

    test_results = pd.DataFrame(test_metric_rows).sort_values(
        ["total_cost", "recall", "f2"],
        ascending=[True, False, False],
    ).reset_index(drop=True)
    test_predictions = pd.concat(prediction_frames, ignore_index=True)
    metadata = pd.DataFrame(metadata_rows)
    test_compare_with_valid = _compare_valid_test(
        valid_best_summary=valid_best_summary,
        test_results=test_results,
        candidate_groups=groups,
    )

    return {
        "test_results": test_results,
        "test_predictions": test_predictions,
        "test_compare_with_valid": test_compare_with_valid,
        "metadata": metadata,
    }
