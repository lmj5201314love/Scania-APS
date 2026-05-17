"""Day 13 结构特征 valid-only 实验。

本模块只在 train_inner / valid 上运行结构特征第一轮实验。official test
不参与策略选择，也不在这里评估。
"""

from __future__ import annotations

from typing import Any, Iterable

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer

from scania_aps.config import ScaniaConfig
from scania_aps.data.clean_data import split_features_target
from scania_aps.evaluation.threshold_utils import (
    build_threshold_summary,
    evaluate_threshold_grid,
)
from scania_aps.features.structural_features import (
    MAIN_EXPERIMENT_GROUPS,
    StructuralFeatureBuilder,
    fit_structural_feature_builder,
    transform_structural_features,
)
from scania_aps.models.train_advanced import (
    build_xgboost_model,
    calculate_scale_pos_weight,
)


def _positive_class_proba(model: Any, X: pd.DataFrame) -> np.ndarray:
    """提取正类预测概率。"""

    if not hasattr(model, "predict_proba"):
        raise ValueError("Day 13 结构特征实验要求模型支持 predict_proba。")

    proba = model.predict_proba(X)
    classes = list(getattr(model, "classes_", []))
    positive_index = classes.index(1) if 1 in classes else proba.shape[1] - 1
    return proba[:, positive_index]


def _prepare_median_all_with_structural_features(
    train_inner_df: pd.DataFrame,
    valid_df: pd.DataFrame,
    cfg: ScaniaConfig,
    structural_config: dict[str, Any],
    experiment_group: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, StructuralFeatureBuilder, dict[str, Any]]:
    """median_all 原始特征 + 指定结构特征组。

    median imputer 只在 train_inner 上 fit；结构特征 builder 也只在 train_inner
    上 fit，然后应用到 valid。
    """

    X_train, y_train = split_features_target(train_inner_df, cfg.label_column)
    X_valid, y_valid = split_features_target(valid_df, cfg.label_column)

    imputer = SimpleImputer(strategy="median")
    X_train_original = pd.DataFrame(
        imputer.fit_transform(X_train),
        columns=X_train.columns.tolist(),
        index=X_train.index,
    )
    X_valid_original = pd.DataFrame(
        imputer.transform(X_valid),
        columns=X_train.columns.tolist(),
        index=X_valid.index,
    )

    builder = fit_structural_feature_builder(
        train_inner_df=train_inner_df,
        cfg=cfg,
        structural_config=structural_config,
        feature_group=experiment_group,
    )
    X_train_structural = transform_structural_features(train_inner_df, builder)
    X_valid_structural = transform_structural_features(valid_df, builder)

    X_train_processed = pd.concat([X_train_original, X_train_structural], axis=1)
    X_valid_processed = pd.concat([X_valid_original, X_valid_structural], axis=1)

    metadata = {
        "experiment_group": experiment_group,
        "model_name": "xgboost_scale_pos_weight",
        "base_strategy": "median_all",
        "n_original_features": X_train_original.shape[1],
        "n_structural_features": X_train_structural.shape[1],
        "n_total_features": X_train_processed.shape[1],
        "structural_feature_names": "|".join(X_train_structural.columns.tolist()),
        "selected_missing_indicator_columns": "|".join(
            builder.selected_missing_indicator_columns
        ),
        "prefix_zero_groups": "|".join(builder.prefix_zero_members.keys()),
        "prefix_missing_groups": "|".join(builder.prefix_missing_members.keys()),
        "uses_official_test": False,
        "selection_dataset": "valid",
    }
    if builder.metadata:
        metadata.update(builder.metadata)

    return (
        X_train_processed,
        X_valid_processed,
        y_train.copy(),
        y_valid.copy(),
        builder,
        metadata,
    )


def run_structural_feature_valid_experiments(
    train_inner_df: pd.DataFrame,
    valid_df: pd.DataFrame,
    cfg: ScaniaConfig,
    structural_config: dict[str, Any],
    experiment_groups: Iterable[str] | None = None,
) -> dict[str, pd.DataFrame]:
    """运行 Day 13 结构特征 valid-only 实验。"""

    groups = list(experiment_groups or MAIN_EXPERIMENT_GROUPS)
    threshold_frames: list[pd.DataFrame] = []
    metadata_rows: list[dict[str, Any]] = []

    for experiment_group in groups:
        (
            X_train_processed,
            X_valid_processed,
            y_train,
            y_valid,
            _builder,
            metadata,
        ) = _prepare_median_all_with_structural_features(
            train_inner_df=train_inner_df,
            valid_df=valid_df,
            cfg=cfg,
            structural_config=structural_config,
            experiment_group=experiment_group,
        )

        scale_pos_weight = calculate_scale_pos_weight(y_train)
        model = build_xgboost_model(cfg, scale_pos_weight=scale_pos_weight)
        model.fit(X_train_processed, y_train)
        y_valid_proba = _positive_class_proba(model, X_valid_processed)

        threshold_metrics = evaluate_threshold_grid(
            y_true=y_valid,
            y_proba=y_valid_proba,
            cfg=cfg,
            model_name="xgboost_scale_pos_weight",
            strategy=experiment_group,
        )
        threshold_metrics["dataset"] = "valid"
        threshold_metrics["experiment_group"] = experiment_group
        threshold_metrics["n_original_features"] = metadata["n_original_features"]
        threshold_metrics["n_structural_features"] = metadata["n_structural_features"]
        threshold_metrics["n_total_features"] = metadata["n_total_features"]
        threshold_frames.append(threshold_metrics)
        metadata_rows.append(metadata)

    valid_threshold_metrics = pd.concat(threshold_frames, ignore_index=True)
    valid_best_summary = build_threshold_summary(valid_threshold_metrics).reset_index(drop=True)
    valid_best_summary.insert(0, "selection_rank", range(1, len(valid_best_summary) + 1))
    valid_best_summary["selection_dataset"] = "valid"

    experiment_metadata = pd.DataFrame(metadata_rows)
    valid_best_summary = valid_best_summary.merge(
        experiment_metadata[
            [
                "experiment_group",
                "n_original_features",
                "n_structural_features",
                "n_total_features",
                "structural_feature_names",
            ]
        ],
        left_on="strategy",
        right_on="experiment_group",
        how="left",
    ).drop(columns=["experiment_group"])

    return {
        "valid_threshold_metrics": valid_threshold_metrics,
        "valid_best_summary": valid_best_summary,
        "experiment_metadata": experiment_metadata,
    }
