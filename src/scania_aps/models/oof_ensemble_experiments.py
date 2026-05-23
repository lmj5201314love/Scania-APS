"""Day 18 OOF probability ensemble experiments.

本模块只使用 official train 内部的 OOF 预测来选择 ensemble recipe 和阈值。
official test 不参与本阶段的任何策略、权重或阈值选择。
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any, Iterable

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.model_selection import RepeatedStratifiedKFold, StratifiedKFold
from xgboost import XGBClassifier

from scania_aps.config import ScaniaConfig
from scania_aps.data.clean_data import split_features_target
from scania_aps.evaluation.threshold_utils import evaluate_threshold_grid
from scania_aps.features.structural_features import (
    fit_structural_feature_builder,
    transform_structural_features,
)
from scania_aps.models.train_advanced import calculate_scale_pos_weight
from scania_aps.models.train_advanced import calculate_scale_pos_weight


BASE_STRATEGY_STRUCTURAL = "median_all_structural_all"
BASE_STRATEGY_INDICATOR = "median_with_selected_missing_indicators"
BASE_STRATEGY_PREFIX_ZERO = "median_all_prefix_zero_rate"

VALID_BASE_STRATEGIES = {
    BASE_STRATEGY_STRUCTURAL,
    BASE_STRATEGY_INDICATOR,
    BASE_STRATEGY_PREFIX_ZERO,
}

RECIPE_COMPONENTS = {
    "structural_all_single": [BASE_STRATEGY_STRUCTURAL],
    "mean_structural_indicator": [BASE_STRATEGY_STRUCTURAL, BASE_STRATEGY_INDICATOR],
    "weighted_70_30_indicator": [BASE_STRATEGY_STRUCTURAL, BASE_STRATEGY_INDICATOR],
    "weighted_80_20_indicator": [BASE_STRATEGY_STRUCTURAL, BASE_STRATEGY_INDICATOR],
    "mean_structural_prefixzero": [BASE_STRATEGY_STRUCTURAL, BASE_STRATEGY_PREFIX_ZERO],
    "weighted_80_20_prefixzero": [BASE_STRATEGY_STRUCTURAL, BASE_STRATEGY_PREFIX_ZERO],
    "mean_three_models": [
        BASE_STRATEGY_STRUCTURAL,
        BASE_STRATEGY_INDICATOR,
        BASE_STRATEGY_PREFIX_ZERO,
    ],
    "weighted_60_25_15": [
        BASE_STRATEGY_STRUCTURAL,
        BASE_STRATEGY_INDICATOR,
        BASE_STRATEGY_PREFIX_ZERO,
    ],
    "weighted_70_20_10": [
        BASE_STRATEGY_STRUCTURAL,
        BASE_STRATEGY_INDICATOR,
        BASE_STRATEGY_PREFIX_ZERO,
    ],
    "rank_average_three": [
        BASE_STRATEGY_STRUCTURAL,
        BASE_STRATEGY_INDICATOR,
        BASE_STRATEGY_PREFIX_ZERO,
    ],
    "weighted_rank_60_25_15": [
        BASE_STRATEGY_STRUCTURAL,
        BASE_STRATEGY_INDICATOR,
        BASE_STRATEGY_PREFIX_ZERO,
    ],
    "max_three_models": [
        BASE_STRATEGY_STRUCTURAL,
        BASE_STRATEGY_INDICATOR,
        BASE_STRATEGY_PREFIX_ZERO,
    ],
}


@dataclass(frozen=True)
class OOFEnsembleSplit:
    """一组 Day18 OOF fold。"""

    repeat_id: int
    fold_id: int
    train_idx: np.ndarray
    valid_idx: np.ndarray


@dataclass(frozen=True)
class OOFBaseFeatureSet:
    """一个 base strategy 在单个 fold 上的训练/验证矩阵。"""

    X_train: pd.DataFrame
    X_valid: pd.DataFrame
    y_train: pd.Series
    y_valid: pd.Series
    metadata: dict[str, Any]


def _ensemble_config(cfg: ScaniaConfig) -> dict[str, Any]:
    """返回 Day18 ensemble 配置。"""

    return cfg.oof_ensemble


def _threshold_values(ensemble_config: dict[str, Any]) -> np.ndarray:
    """根据配置生成阈值网格。"""

    grid = ensemble_config["threshold_grid"]
    start = float(grid["start"])
    stop = float(grid["stop"])
    step = float(grid["step"])
    return np.round(np.arange(start, stop + step / 2, step), 6)


def _build_oof_ensemble_splits(y: pd.Series, cfg: ScaniaConfig) -> list[OOFEnsembleSplit]:
    """使用同一组 folds 生成所有 base strategy 的 OOF 预测。"""

    ensemble_config = _ensemble_config(cfg)
    cv_config = ensemble_config["cv"]
    n_splits = int(os.getenv("SCANIA_APS_DAY18_N_SPLITS", cv_config["n_splits"]))
    n_repeats = int(os.getenv("SCANIA_APS_DAY18_N_REPEATS", cv_config["n_repeats"]))
    random_state = int(ensemble_config.get("random_state", cfg.random_state))
    y_array = pd.Series(y).astype(int).to_numpy()
    indices = np.arange(len(y_array))

    if n_repeats == 1:
        splitter = StratifiedKFold(
            n_splits=n_splits,
            shuffle=bool(cv_config.get("shuffle", True)),
            random_state=random_state,
        )
        return [
            OOFEnsembleSplit(
                repeat_id=1,
                fold_id=fold_index,
                train_idx=train_idx,
                valid_idx=valid_idx,
            )
            for fold_index, (train_idx, valid_idx) in enumerate(
                splitter.split(indices, y_array),
                start=1,
            )
        ]

    splitter = RepeatedStratifiedKFold(
        n_splits=n_splits,
        n_repeats=n_repeats,
        random_state=random_state,
    )
    splits: list[OOFEnsembleSplit] = []
    for split_index, (train_idx, valid_idx) in enumerate(splitter.split(indices, y_array)):
        splits.append(
            OOFEnsembleSplit(
                repeat_id=split_index // n_splits + 1,
                fold_id=split_index % n_splits + 1,
                train_idx=train_idx,
                valid_idx=valid_idx,
            )
        )
    return splits


def _median_impute(
    X_train: pd.DataFrame,
    X_valid: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """只在 fold_train 上拟合 median imputer。"""

    imputer = SimpleImputer(strategy="median")
    X_train_processed = pd.DataFrame(
        imputer.fit_transform(X_train),
        columns=X_train.columns.tolist(),
        index=X_train.index,
    )
    X_valid_processed = pd.DataFrame(
        imputer.transform(X_valid),
        columns=X_train.columns.tolist(),
        index=X_valid.index,
    )
    return X_train_processed, X_valid_processed


def _structural_group_for_base_strategy(base_candidate_strategy: str) -> str | None:
    """将 Day18 base strategy 映射到结构特征构造规则。"""

    if base_candidate_strategy == BASE_STRATEGY_STRUCTURAL:
        return "median_all_structural_all"
    if base_candidate_strategy == BASE_STRATEGY_INDICATOR:
        return "median_all_selected_missing_indicators_top30"
    if base_candidate_strategy == BASE_STRATEGY_PREFIX_ZERO:
        return "median_all_prefix_zero_rate"
    return None


def prepare_base_oof_feature_set(
    fold_train_df: pd.DataFrame,
    fold_valid_df: pd.DataFrame,
    cfg: ScaniaConfig,
    structural_config: dict[str, Any],
    base_candidate_strategy: str,
) -> OOFBaseFeatureSet:
    """为 Day18 的一个 base strategy 准备 fold_train/fold_valid 特征。"""

    if base_candidate_strategy not in VALID_BASE_STRATEGIES:
        raise ValueError(f"Unsupported Day18 base_candidate_strategy: {base_candidate_strategy}")

    X_train_raw, y_train = split_features_target(fold_train_df, cfg.label_column)
    X_valid_raw, y_valid = split_features_target(fold_valid_df, cfg.label_column)
    X_train_original, X_valid_original = _median_impute(X_train_raw, X_valid_raw)

    feature_frames_train = [X_train_original]
    feature_frames_valid = [X_valid_original]
    structural_feature_names: list[str] = []
    selected_missing_indicator_columns: list[str] = []

    structural_group = _structural_group_for_base_strategy(base_candidate_strategy)
    if structural_group is not None:
        builder = fit_structural_feature_builder(
            train_inner_df=fold_train_df,
            cfg=cfg,
            structural_config=structural_config,
            feature_group=structural_group,
        )
        X_train_structural = transform_structural_features(fold_train_df, builder)
        X_valid_structural = transform_structural_features(fold_valid_df, builder)
        structural_feature_names = X_train_structural.columns.tolist()
        selected_missing_indicator_columns = builder.selected_missing_indicator_columns
        feature_frames_train.append(X_train_structural)
        feature_frames_valid.append(X_valid_structural)

    X_train = pd.concat(feature_frames_train, axis=1)
    X_valid = pd.concat(feature_frames_valid, axis=1)
    metadata = {
        "base_candidate_strategy": base_candidate_strategy,
        "fit_dataset": "fold_train",
        "evaluation_dataset": "fold_valid",
        "uses_official_test": False,
        "n_original_features": X_train_original.shape[1],
        "n_structural_features": len(structural_feature_names),
        "n_selected_missing_indicators": len(selected_missing_indicator_columns),
        "n_total_features": X_train.shape[1],
        "structural_feature_names": "|".join(structural_feature_names),
        "selected_missing_indicator_columns": "|".join(selected_missing_indicator_columns),
    }
    return OOFBaseFeatureSet(
        X_train=X_train,
        X_valid=X_valid,
        y_train=y_train.copy(),
        y_valid=y_valid.copy(),
        metadata=metadata,
    )


def _train_base_oof_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    cfg: ScaniaConfig,
) -> XGBClassifier:
    """训练非 tuned XGBoost，避免复用 Day15 tuned 参数。"""

    model_config = dict(cfg.advanced_models["xgboost"])
    return XGBClassifier(
        n_estimators=int(model_config["n_estimators"]),
        max_depth=int(model_config["max_depth"]),
        learning_rate=float(model_config["learning_rate"]),
        subsample=float(model_config["subsample"]),
        colsample_bytree=float(model_config["colsample_bytree"]),
        eval_metric=model_config.get("eval_metric", "aucpr"),
        n_jobs=int(model_config.get("n_jobs", -1)),
        random_state=int(_ensemble_config(cfg).get("random_state", cfg.random_state)),
        scale_pos_weight=calculate_scale_pos_weight(y_train),
    )


def _positive_class_proba(model: Any, X: pd.DataFrame) -> np.ndarray:
    """提取正类概率。"""

    proba = model.predict_proba(X)
    classes = list(getattr(model, "classes_", []))
    positive_index = classes.index(1) if 1 in classes else proba.shape[1] - 1
    return proba[:, positive_index]


def generate_base_oof_predictions_for_ensemble(
    train_df: pd.DataFrame,
    cfg: ScaniaConfig,
    structural_config: dict[str, Any],
    ensemble_config: dict[str, Any],
    base_candidate_strategies: Iterable[str],
) -> dict[str, pd.DataFrame]:
    """生成 Day18 三组 base strategy 的同折 OOF 预测。"""

    y = train_df["target"].astype(int)
    splits = _build_oof_ensemble_splits(y, cfg)
    raw_prediction_frames: list[pd.DataFrame] = []
    metadata_rows: list[dict[str, Any]] = []
    fold_rows: list[dict[str, Any]] = []

    for split in splits:
        fold_train_df = train_df.iloc[split.train_idx].copy()
        fold_valid_df = train_df.iloc[split.valid_idx].copy()
        for base_candidate_strategy in base_candidate_strategies:
            feature_set = prepare_base_oof_feature_set(
                fold_train_df=fold_train_df,
                fold_valid_df=fold_valid_df,
                cfg=cfg,
                structural_config=structural_config,
                base_candidate_strategy=base_candidate_strategy,
            )
            model = _train_base_oof_model(feature_set.X_train, feature_set.y_train, cfg)
            model.fit(feature_set.X_train, feature_set.y_train)
            y_proba = _positive_class_proba(model, feature_set.X_valid)
            raw_prediction_frames.append(
                pd.DataFrame(
                    {
                        "sample_index": fold_valid_df.index.to_numpy(),
                        "y_true": feature_set.y_valid.to_numpy(dtype=int),
                        "y_proba": y_proba,
                        "base_candidate_strategy": base_candidate_strategy,
                        "repeat_id": split.repeat_id,
                        "fold_id": split.fold_id,
                        "model_name": "xgboost_oof_base",
                    }
                )
            )
            metadata_rows.append(
                {
                    **feature_set.metadata,
                    "repeat_id": split.repeat_id,
                    "fold_id": split.fold_id,
                    "fold_train_rows": len(fold_train_df),
                    "fold_valid_rows": len(fold_valid_df),
                    "fold_train_pos": int(feature_set.y_train.sum()),
                    "fold_valid_pos": int(feature_set.y_valid.sum()),
                }
            )
            fold_rows.append(
                {
                    "base_candidate_strategy": base_candidate_strategy,
                    "repeat_id": split.repeat_id,
                    "fold_id": split.fold_id,
                    "train_rows": len(fold_train_df),
                    "valid_rows": len(fold_valid_df),
                    "train_pos": int(feature_set.y_train.sum()),
                    "valid_pos": int(feature_set.y_valid.sum()),
                }
            )

    raw_oof_predictions = (
        pd.concat(raw_prediction_frames, ignore_index=True)
        if raw_prediction_frames
        else pd.DataFrame()
    )
    if raw_oof_predictions.empty:
        averaged_oof_predictions = pd.DataFrame()
    else:
        averaged_oof_predictions = (
            raw_oof_predictions.groupby(["base_candidate_strategy", "sample_index"], as_index=False)
            .agg(
                y_true=("y_true", "first"),
                y_proba=("y_proba", "mean"),
                oof_prediction_count=("y_proba", "size"),
                model_name=("model_name", "first"),
            )
            .sort_values(["base_candidate_strategy", "sample_index"])
            .reset_index(drop=True)
        )

    return {
        "raw_oof_predictions": raw_oof_predictions,
        "averaged_oof_predictions": averaged_oof_predictions,
        "base_candidate_metadata": pd.DataFrame(metadata_rows),
        "base_fold_summary": pd.DataFrame(fold_rows),
    }


def _select_rule_best(
    threshold_df: pd.DataFrame,
    rule: str,
    cfg: ScaniaConfig,
    config_section: dict[str, Any],
) -> pd.Series:
    """按成本、recall floor 或 FN floor 选择一个阈值。"""

    candidates = threshold_df.copy()
    constraint_satisfied = True

    if rule.startswith("recall_floor"):
        floor = float(config_section["recall_floors"][rule])
        candidates = candidates[candidates["recall"] >= floor]
    elif rule.startswith("fn_floor"):
        floor = int(config_section["fn_floors"][rule])
        candidates = candidates[candidates["fn"] <= floor]
    elif rule != "cost_min":
        raise ValueError(f"Unsupported threshold selection rule: {rule}")

    if candidates.empty:
        candidates = threshold_df.copy()
        constraint_satisfied = False

    selected = candidates.sort_values(
        ["total_cost", "fn", "recall", "threshold"],
        ascending=[True, True, False, True],
    ).iloc[0].copy()
    selected["threshold_selection_rule"] = rule
    selected["constraint_satisfied"] = constraint_satisfied
    selected["selection_dataset"] = "oof_averaged"
    return selected


def evaluate_base_oof_thresholds(
    oof_base_predictions: pd.DataFrame,
    cfg: ScaniaConfig,
    ensemble_config: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """为 base strategy 计算 cost_min 阈值，用于 overlap analysis。"""

    thresholds = _threshold_values(ensemble_config)
    threshold_frames: list[pd.DataFrame] = []
    best_rows: list[pd.Series] = []

    for base_candidate_strategy, group in oof_base_predictions.groupby(
        "base_candidate_strategy",
        dropna=False,
    ):
        threshold_df = evaluate_threshold_grid(
            y_true=group["y_true"],
            y_proba=group["y_proba"],
            cfg=cfg,
            model_name="xgboost_oof_base",
            strategy=base_candidate_strategy,
            thresholds=thresholds,
        )
        threshold_df["base_candidate_strategy"] = base_candidate_strategy
        threshold_df["selection_dataset"] = "oof_averaged"
        threshold_frames.append(threshold_df)
        best_rows.append(_select_rule_best(threshold_df, "cost_min", cfg, ensemble_config))

    threshold_metrics = pd.concat(threshold_frames, ignore_index=True)
    best_summary = pd.DataFrame(best_rows).sort_values(
        ["total_cost", "fn", "recall"],
        ascending=[True, True, False],
    )
    return threshold_metrics, best_summary.reset_index(drop=True)


def analyze_fp_fn_overlap(
    oof_base_predictions: pd.DataFrame,
    threshold_by_strategy: dict[str, float],
    reference_strategy: str = BASE_STRATEGY_STRUCTURAL,
) -> dict[str, pd.DataFrame]:
    """分析不同 base strategy 在 OOF 上的 FN/FP 互补空间。"""

    required = {
        BASE_STRATEGY_STRUCTURAL,
        BASE_STRATEGY_INDICATOR,
        BASE_STRATEGY_PREFIX_ZERO,
    }
    available = set(oof_base_predictions["base_candidate_strategy"].unique())
    missing = required - available
    if missing:
        raise ValueError(f"Missing base OOF predictions for strategies: {sorted(missing)}")

    wide = oof_base_predictions.pivot_table(
        index=["sample_index", "y_true"],
        columns="base_candidate_strategy",
        values="y_proba",
        aggfunc="mean",
    ).reset_index()

    for strategy in required:
        threshold = float(threshold_by_strategy[strategy])
        wide[f"pred_{strategy}"] = (wide[strategy] >= threshold).astype(int)
        wide[f"type_{strategy}"] = np.select(
            [
                wide["y_true"].eq(1) & wide[f"pred_{strategy}"].eq(1),
                wide["y_true"].eq(0) & wide[f"pred_{strategy}"].eq(1),
                wide["y_true"].eq(0) & wide[f"pred_{strategy}"].eq(0),
                wide["y_true"].eq(1) & wide[f"pred_{strategy}"].eq(0),
            ],
            ["TP", "FP", "TN", "FN"],
            default="unknown",
        )

    ref_fn = wide["y_true"].eq(1) & wide[f"pred_{reference_strategy}"].eq(0)
    indicator_rescue = ref_fn & wide[f"pred_{BASE_STRATEGY_INDICATOR}"].eq(1)
    prefix_rescue = ref_fn & wide[f"pred_{BASE_STRATEGY_PREFIX_ZERO}"].eq(1)
    either_rescue = indicator_rescue | prefix_rescue
    all_models_fn = (
        wide["y_true"].eq(1)
        & wide[f"pred_{BASE_STRATEGY_STRUCTURAL}"].eq(0)
        & wide[f"pred_{BASE_STRATEGY_INDICATOR}"].eq(0)
        & wide[f"pred_{BASE_STRATEGY_PREFIX_ZERO}"].eq(0)
    )
    structural_only_fn = ref_fn & (
        wide[f"pred_{BASE_STRATEGY_INDICATOR}"].eq(1)
        | wide[f"pred_{BASE_STRATEGY_PREFIX_ZERO}"].eq(1)
    )

    fn_overlap_summary = pd.DataFrame(
        [
            {
                "reference_strategy": reference_strategy,
                "reference_fn_count": int(ref_fn.sum()),
                "indicator_rescued_fn": int(indicator_rescue.sum()),
                "prefixzero_rescued_fn": int(prefix_rescue.sum()),
                "either_rescued_fn": int(either_rescue.sum()),
                "all_models_fn": int(all_models_fn.sum()),
                "structural_only_fn": int(structural_only_fn.sum()),
                "indicator_extra_fp_vs_reference": int(
                    (
                        wide["y_true"].eq(0)
                        & wide[f"pred_{reference_strategy}"].eq(0)
                        & wide[f"pred_{BASE_STRATEGY_INDICATOR}"].eq(1)
                    ).sum()
                ),
                "prefixzero_extra_fp_vs_reference": int(
                    (
                        wide["y_true"].eq(0)
                        & wide[f"pred_{reference_strategy}"].eq(0)
                        & wide[f"pred_{BASE_STRATEGY_PREFIX_ZERO}"].eq(1)
                    ).sum()
                ),
            }
        ]
    )

    structural_fp = wide["y_true"].eq(0) & wide[f"pred_{BASE_STRATEGY_STRUCTURAL}"].eq(1)
    indicator_fp = wide["y_true"].eq(0) & wide[f"pred_{BASE_STRATEGY_INDICATOR}"].eq(1)
    prefix_fp = wide["y_true"].eq(0) & wide[f"pred_{BASE_STRATEGY_PREFIX_ZERO}"].eq(1)
    fp_overlap_summary = pd.DataFrame(
        [
            {"fp_overlap_type": "all_three_fp", "sample_count": int((structural_fp & indicator_fp & prefix_fp).sum())},
            {"fp_overlap_type": "structural_only_fp", "sample_count": int((structural_fp & ~indicator_fp & ~prefix_fp).sum())},
            {"fp_overlap_type": "indicator_only_fp", "sample_count": int((indicator_fp & ~structural_fp & ~prefix_fp).sum())},
            {"fp_overlap_type": "prefixzero_only_fp", "sample_count": int((prefix_fp & ~structural_fp & ~indicator_fp).sum())},
            {"fp_overlap_type": "structural_indicator_fp", "sample_count": int((structural_fp & indicator_fp & ~prefix_fp).sum())},
            {"fp_overlap_type": "structural_prefixzero_fp", "sample_count": int((structural_fp & prefix_fp & ~indicator_fp).sum())},
            {"fp_overlap_type": "indicator_prefixzero_fp", "sample_count": int((indicator_fp & prefix_fp & ~structural_fp).sum())},
        ]
    )

    rescue_type = np.select(
        [all_models_fn, structural_only_fn],
        ["all_models_fn", "ensemble_possible_rescue"],
        default="other",
    )
    rescuable_positive_samples = wide.loc[ref_fn].copy()
    rescuable_positive_samples["rescue_type"] = rescue_type[ref_fn.to_numpy()]
    keep_cols = [
        "sample_index",
        "y_true",
        BASE_STRATEGY_STRUCTURAL,
        BASE_STRATEGY_INDICATOR,
        BASE_STRATEGY_PREFIX_ZERO,
        f"pred_{BASE_STRATEGY_STRUCTURAL}",
        f"pred_{BASE_STRATEGY_INDICATOR}",
        f"pred_{BASE_STRATEGY_PREFIX_ZERO}",
        "rescue_type",
    ]
    return {
        "fn_overlap_summary": fn_overlap_summary,
        "fp_overlap_summary": fp_overlap_summary,
        "rescuable_positive_samples": rescuable_positive_samples[keep_cols].reset_index(drop=True),
    }


def _recipe_group_map(ensemble_recipes: dict[str, list[str]]) -> dict[str, str]:
    """将 recipe name 映射到 main / auxiliary / diagnostic。"""

    mapping: dict[str, str] = {}
    for group_name, recipe_names in ensemble_recipes.items():
        for recipe_name in recipe_names:
            mapping[recipe_name] = group_name
    return mapping


def _base_probability_wide(oof_base_predictions: pd.DataFrame) -> pd.DataFrame:
    """把 base OOF 预测转成每个样本一行。"""

    wide = oof_base_predictions.pivot_table(
        index=["sample_index", "y_true"],
        columns="base_candidate_strategy",
        values="y_proba",
        aggfunc="mean",
    ).reset_index()
    required = [BASE_STRATEGY_STRUCTURAL, BASE_STRATEGY_INDICATOR, BASE_STRATEGY_PREFIX_ZERO]
    missing = [col for col in required if col not in wide.columns]
    if missing:
        raise ValueError(f"Missing base strategies for ensemble recipes: {missing}")
    return wide


def build_oof_probability_ensembles(
    oof_base_predictions: pd.DataFrame,
    ensemble_recipes: dict[str, list[str]],
) -> dict[str, pd.DataFrame]:
    """按固定 recipe 构造 OOF probability ensemble，不做权重搜索。"""

    wide = _base_probability_wide(oof_base_predictions)
    group_map = _recipe_group_map(ensemble_recipes)
    structural = wide[BASE_STRATEGY_STRUCTURAL].astype(float)
    indicator = wide[BASE_STRATEGY_INDICATOR].astype(float)
    prefixzero = wide[BASE_STRATEGY_PREFIX_ZERO].astype(float)
    rank_structural = structural.rank(method="average", pct=True)
    rank_indicator = indicator.rank(method="average", pct=True)
    rank_prefixzero = prefixzero.rank(method="average", pct=True)

    recipe_scores = {
        "structural_all_single": structural,
        "mean_structural_indicator": 0.5 * structural + 0.5 * indicator,
        "weighted_70_30_indicator": 0.7 * structural + 0.3 * indicator,
        "weighted_80_20_indicator": 0.8 * structural + 0.2 * indicator,
        "mean_structural_prefixzero": 0.5 * structural + 0.5 * prefixzero,
        "weighted_80_20_prefixzero": 0.8 * structural + 0.2 * prefixzero,
        "mean_three_models": (structural + indicator + prefixzero) / 3.0,
        "weighted_60_25_15": 0.60 * structural + 0.25 * indicator + 0.15 * prefixzero,
        "weighted_70_20_10": 0.70 * structural + 0.20 * indicator + 0.10 * prefixzero,
        "rank_average_three": (rank_structural + rank_indicator + rank_prefixzero) / 3.0,
        "weighted_rank_60_25_15": (
            0.60 * rank_structural + 0.25 * rank_indicator + 0.15 * rank_prefixzero
        ),
        "max_three_models": pd.concat([structural, indicator, prefixzero], axis=1).max(axis=1),
    }
    recipe_descriptions = {
        "structural_all_single": "structural_all base probability only",
        "mean_structural_indicator": "0.50 structural_all + 0.50 selected missing indicator",
        "weighted_70_30_indicator": "0.70 structural_all + 0.30 selected missing indicator",
        "weighted_80_20_indicator": "0.80 structural_all + 0.20 selected missing indicator",
        "mean_structural_prefixzero": "0.50 structural_all + 0.50 prefix zero rate",
        "weighted_80_20_prefixzero": "0.80 structural_all + 0.20 prefix zero rate",
        "mean_three_models": "mean of structural_all, selected missing indicator and prefix zero rate",
        "weighted_60_25_15": "0.60 structural_all + 0.25 indicator + 0.15 prefix zero",
        "weighted_70_20_10": "0.70 structural_all + 0.20 indicator + 0.10 prefix zero",
        "rank_average_three": "mean rank percentile of three base scores",
        "weighted_rank_60_25_15": "weighted rank percentile: 0.60/0.25/0.15",
        "max_three_models": "max score across three base models; diagnostic recall ceiling only",
    }

    prediction_frames: list[pd.DataFrame] = []
    metadata_rows: list[dict[str, Any]] = []
    for recipe_name, score in recipe_scores.items():
        ensemble_group = group_map.get(recipe_name, "unlisted")
        component_strategies = RECIPE_COMPONENTS[recipe_name]
        prediction_frames.append(
            pd.DataFrame(
                {
                    "sample_index": wide["sample_index"],
                    "y_true": wide["y_true"].astype(int),
                    "ensemble_name": recipe_name,
                    "ensemble_group": ensemble_group,
                    "ensemble_score": score.to_numpy(dtype=float),
                    "component_strategies": "|".join(component_strategies),
                    "recipe_description": recipe_descriptions[recipe_name],
                }
            )
        )
        metadata_rows.append(
            {
                "ensemble_name": recipe_name,
                "ensemble_group": ensemble_group,
                "component_strategies": "|".join(component_strategies),
                "recipe_description": recipe_descriptions[recipe_name],
                "is_diagnostic": ensemble_group == "diagnostic",
            }
        )

    return {
        "oof_ensemble_predictions": pd.concat(prediction_frames, ignore_index=True),
        "ensemble_recipe_metadata": pd.DataFrame(metadata_rows),
    }


def evaluate_oof_ensemble_thresholds(
    oof_ensemble_predictions: pd.DataFrame,
    cfg: ScaniaConfig,
    ensemble_config: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """评估 ensemble threshold grid，并应用 cost/recall/FN 约束。"""

    thresholds = _threshold_values(ensemble_config)
    rules = list(ensemble_config["threshold_selection_rules"])
    threshold_frames: list[pd.DataFrame] = []
    best_rows: list[pd.Series] = []

    for (ensemble_name, ensemble_group), group in oof_ensemble_predictions.groupby(
        ["ensemble_name", "ensemble_group"],
        dropna=False,
    ):
        threshold_df = evaluate_threshold_grid(
            y_true=group["y_true"],
            y_proba=group["ensemble_score"],
            cfg=cfg,
            model_name="xgboost_oof_ensemble",
            strategy=ensemble_name,
            thresholds=thresholds,
        )
        threshold_df["ensemble_name"] = ensemble_name
        threshold_df["ensemble_group"] = ensemble_group
        threshold_df["selection_dataset"] = "oof_averaged"
        threshold_frames.append(threshold_df)

        for rule in rules:
            selected = _select_rule_best(threshold_df, rule, cfg, ensemble_config)
            selected["ensemble_name"] = ensemble_name
            selected["ensemble_group"] = ensemble_group
            best_rows.append(selected)

    threshold_metrics = pd.concat(threshold_frames, ignore_index=True)
    best_summary = pd.DataFrame(best_rows).sort_values(
        ["threshold_selection_rule", "total_cost", "fn", "recall"],
        ascending=[True, True, True, False],
    ).reset_index(drop=True)
    strategy_compare = best_summary.sort_values(
        ["threshold_selection_rule", "ensemble_group", "total_cost", "fn"],
        ascending=[True, True, True, True],
    ).reset_index(drop=True)
    return threshold_metrics, best_summary, strategy_compare


def select_day19_official_test_candidates(
    ensemble_best_summary: pd.DataFrame,
    baseline_ensemble_name: str = "structural_all_single",
    filter_config: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """根据 OOF 结果筛选最多两个 Day19 official test 候选。"""

    filter_config = filter_config or {}
    min_reduction = float(filter_config.get("min_oof_cost_reduction_pct", 0.03))
    min_fn_reduction = int(filter_config.get("min_fn_reduction", 3))
    max_fp_per_fn = float(filter_config.get("max_fp_increase_per_fn_saved", 40))
    allow_diagnostic = bool(filter_config.get("allow_diagnostic_as_final_candidate", False))
    allow_max = bool(filter_config.get("allow_max_three_models", False))

    baseline_rows = ensemble_best_summary[
        ensemble_best_summary["ensemble_name"].eq(baseline_ensemble_name)
        & ensemble_best_summary["threshold_selection_rule"].eq("cost_min")
    ]
    if baseline_rows.empty:
        raise ValueError("Cannot find structural_all_single cost_min baseline row.")
    baseline = baseline_rows.iloc[0]

    rows: list[dict[str, Any]] = []
    for _, row in ensemble_best_summary.iterrows():
        ensemble_name = row["ensemble_name"]
        ensemble_group = row["ensemble_group"]
        baseline_fp = int(baseline["fp"])
        baseline_fn = int(baseline["fn"])
        baseline_cost = float(baseline["total_cost"])
        delta_fp = int(row["fp"]) - baseline_fp
        fn_saved = baseline_fn - int(row["fn"])
        delta_cost = float(row["total_cost"]) - baseline_cost
        cost_reduction_pct = (baseline_cost - float(row["total_cost"])) / baseline_cost
        fp_increase_per_fn_saved = (
            delta_fp / fn_saved if fn_saved > 0 and delta_fp > 0 else 0.0
        )
        threshold_too_aggressive = float(row["threshold"]) < 0.03

        reasons: list[str] = []
        recommend = True
        if ensemble_name == baseline_ensemble_name:
            recommend = False
            reasons.append("baseline reference row")
        if ensemble_group == "diagnostic" and not allow_diagnostic:
            recommend = False
            reasons.append("diagnostic ensemble is not allowed as final candidate")
        if ensemble_name == "max_three_models" and not allow_max:
            recommend = False
            reasons.append("max_three_models is recall ceiling diagnostic only")
        if fn_saved < min_fn_reduction:
            recommend = False
            if fn_saved < 0:
                reasons.append(f"FN increased by {abs(fn_saved)}")
            else:
                reasons.append(f"FN saved {fn_saved} < {min_fn_reduction}")
        if cost_reduction_pct < min_reduction:
            recommend = False
            reasons.append(f"cost reduction {cost_reduction_pct:.3f} < {min_reduction:.3f}")
        if delta_fp > 0 and fn_saved > 0 and fp_increase_per_fn_saved > max_fp_per_fn:
            recommend = False
            reasons.append(
                f"FP increase per FN saved {fp_increase_per_fn_saved:.2f} > {max_fp_per_fn:.2f}"
            )
        if delta_fp > 0 and fn_saved <= 0:
            recommend = False
            reasons.append("FP increases without FN reduction")
        if threshold_too_aggressive:
            reasons.append("threshold below 0.03; marked as aggressive")

        rows.append(
            {
                "ensemble_name": ensemble_name,
                "threshold_selection_rule": row["threshold_selection_rule"],
                "threshold": row["threshold"],
                "oof_precision": row["precision"],
                "oof_recall": row["recall"],
                "oof_f2": row["f2"],
                "oof_ap": row["average_precision"],
                "oof_fp": int(row["fp"]),
                "oof_fn": int(row["fn"]),
                "oof_total_cost": row["total_cost"],
                "baseline_fp": baseline_fp,
                "baseline_fn": baseline_fn,
                "baseline_total_cost": baseline_cost,
                "delta_fp": delta_fp,
                "delta_fn": int(row["fn"]) - baseline_fn,
                "delta_cost": delta_cost,
                "cost_reduction_pct": cost_reduction_pct,
                "fp_increase_per_fn_saved": fp_increase_per_fn_saved,
                "threshold_too_aggressive": threshold_too_aggressive,
                "ensemble_group": ensemble_group,
                "recommend_for_day19": recommend,
                "recommendation_reason": "; ".join(reasons) if reasons else "meets filters",
            }
        )

    recommendations = pd.DataFrame(rows)
    if recommendations.empty:
        return recommendations

    recommendations["group_priority"] = recommendations["ensemble_group"].map(
        {"main": 0, "auxiliary": 1, "diagnostic": 2}
    ).fillna(3)
    recommended_idx = (
        recommendations[recommendations["recommend_for_day19"]]
        .sort_values(
            ["group_priority", "oof_total_cost", "oof_fn", "oof_recall"],
            ascending=[True, True, True, False],
        )
        .head(2)
        .index
    )
    recommendations["recommend_for_day19"] = recommendations.index.isin(recommended_idx)
    recommendations = recommendations.drop(columns=["group_priority"])
    return recommendations.sort_values(
        ["recommend_for_day19", "ensemble_group", "oof_total_cost"],
        ascending=[False, True, True],
    ).reset_index(drop=True)


def run_oof_probability_ensemble_experiments(
    train_df: pd.DataFrame,
    cfg: ScaniaConfig,
    structural_config: dict[str, Any],
    ensemble_config: dict[str, Any] | None = None,
    base_candidate_strategies: Iterable[str] | None = None,
) -> dict[str, pd.DataFrame]:
    """运行 Day18 OOF base prediction、overlap 和 ensemble 实验。"""

    ensemble_config = ensemble_config or _ensemble_config(cfg)
    strategies = list(base_candidate_strategies or ensemble_config["base_candidate_strategies"])

    base_outputs = generate_base_oof_predictions_for_ensemble(
        train_df=train_df,
        cfg=cfg,
        structural_config=structural_config,
        ensemble_config=ensemble_config,
        base_candidate_strategies=strategies,
    )
    base_threshold_metrics, base_best_summary = evaluate_base_oof_thresholds(
        oof_base_predictions=base_outputs["averaged_oof_predictions"],
        cfg=cfg,
        ensemble_config=ensemble_config,
    )
    threshold_by_strategy = {
        row["strategy"]: float(row["threshold"]) for _, row in base_best_summary.iterrows()
    }
    overlap_outputs = analyze_fp_fn_overlap(
        oof_base_predictions=base_outputs["averaged_oof_predictions"],
        threshold_by_strategy=threshold_by_strategy,
        reference_strategy=BASE_STRATEGY_STRUCTURAL,
    )
    ensemble_outputs = build_oof_probability_ensembles(
        oof_base_predictions=base_outputs["averaged_oof_predictions"],
        ensemble_recipes=ensemble_config["ensemble_recipes"],
    )
    threshold_metrics, best_summary, strategy_compare = evaluate_oof_ensemble_thresholds(
        oof_ensemble_predictions=ensemble_outputs["oof_ensemble_predictions"],
        cfg=cfg,
        ensemble_config=ensemble_config,
    )
    recommendations = select_day19_official_test_candidates(
        ensemble_best_summary=best_summary,
        baseline_ensemble_name="structural_all_single",
        filter_config=ensemble_config["official_test_candidate_filter"],
    )

    return {
        "oof_base_raw_predictions": base_outputs["raw_oof_predictions"],
        "oof_base_averaged_predictions": base_outputs["averaged_oof_predictions"],
        "oof_base_candidate_metadata": base_outputs["base_candidate_metadata"],
        "oof_base_fold_summary": base_outputs["base_fold_summary"],
        "oof_base_threshold_metrics": base_threshold_metrics,
        "oof_base_best_summary": base_best_summary,
        "oof_fn_overlap_summary": overlap_outputs["fn_overlap_summary"],
        "oof_fp_overlap_summary": overlap_outputs["fp_overlap_summary"],
        "oof_rescuable_positive_samples": overlap_outputs["rescuable_positive_samples"],
        "oof_ensemble_predictions": ensemble_outputs["oof_ensemble_predictions"],
        "oof_ensemble_recipe_metadata": ensemble_outputs["ensemble_recipe_metadata"],
        "oof_ensemble_threshold_metrics": threshold_metrics,
        "oof_ensemble_best_summary": best_summary,
        "oof_ensemble_strategy_compare": strategy_compare,
        "official_test_candidate_recommendations": recommendations,
    }
