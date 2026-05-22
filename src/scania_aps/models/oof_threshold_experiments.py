"""Day 17 OOF threshold selection and bin projection experiments.

Official test data is intentionally not used in this module. All threshold
rules are selected from out-of-fold predictions generated inside official train.
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
from scania_aps.evaluation.metrics import evaluate_binary_classifier
from scania_aps.evaluation.threshold_utils import evaluate_threshold_grid
from scania_aps.features.bin_projection import (
    build_bin_projection_metadata,
    fit_bin_projection_builder,
    transform_bin_projection_features,
)
from scania_aps.features.structural_features import (
    fit_structural_feature_builder,
    transform_structural_features,
)
from scania_aps.models.train_advanced import calculate_scale_pos_weight


VALID_OOF_STRATEGIES = {
    "baseline_median_all",
    "median_all_structural_all",
    "median_all_bin_projection",
    "median_all_structural_all_plus_bin_projection",
}


@dataclass(frozen=True)
class OOFSplit:
    """A single OOF split definition."""

    repeat_id: int
    fold_id: int
    train_idx: np.ndarray
    valid_idx: np.ndarray


@dataclass(frozen=True)
class OOFTuningFeatureSet:
    """Prepared fold_train/fold_valid matrices for one OOF strategy."""

    X_train: pd.DataFrame
    X_valid: pd.DataFrame
    y_train: pd.Series
    y_valid: pd.Series
    metadata: dict[str, Any]
    bin_projection_metadata: pd.DataFrame


def _oof_config(cfg: ScaniaConfig) -> dict[str, Any]:
    """Return Day17 OOF config."""

    return cfg.oof_threshold


def _effective_cv_values(cfg: ScaniaConfig) -> tuple[int, int]:
    """Read CV values, allowing explicit runtime environment overrides."""

    oof_config = _oof_config(cfg)
    cv_config = oof_config["cv"]
    n_splits = int(os.getenv("SCANIA_APS_DAY17_N_SPLITS", cv_config["n_splits"]))
    n_repeats = int(os.getenv("SCANIA_APS_DAY17_N_REPEATS", cv_config["n_repeats"]))

    downgrade = oof_config.get("allow_runtime_downgrade", {})
    if downgrade.get("enabled", False):
        n_splits = max(n_splits, int(downgrade.get("min_n_splits", 2)))
        n_repeats = max(n_repeats, int(downgrade.get("min_n_repeats", 1)))

    return n_splits, n_repeats


def _threshold_values(oof_config: dict[str, Any]) -> np.ndarray:
    """Generate threshold values from config."""

    grid = oof_config["threshold_grid"]
    start = float(grid["start"])
    stop = float(grid["stop"])
    step = float(grid["step"])
    return np.round(np.arange(start, stop + step / 2, step), 6)


def build_oof_splits(y: pd.Series, cfg: ScaniaConfig) -> list[OOFSplit]:
    """Build stratified OOF splits from official train labels."""

    n_splits, n_repeats = _effective_cv_values(cfg)
    random_state = int(_oof_config(cfg).get("random_state", cfg.random_state))
    y_array = pd.Series(y).astype(int).to_numpy()
    indices = np.arange(len(y_array))
    splits: list[OOFSplit] = []

    if n_repeats == 1:
        splitter = StratifiedKFold(
            n_splits=n_splits,
            shuffle=bool(_oof_config(cfg)["cv"].get("shuffle", True)),
            random_state=random_state,
        )
        for fold_index, (train_idx, valid_idx) in enumerate(splitter.split(indices, y_array), start=1):
            splits.append(
                OOFSplit(
                    repeat_id=1,
                    fold_id=fold_index,
                    train_idx=train_idx,
                    valid_idx=valid_idx,
                )
            )
        return splits

    splitter = RepeatedStratifiedKFold(
        n_splits=n_splits,
        n_repeats=n_repeats,
        random_state=random_state,
    )
    for split_index, (train_idx, valid_idx) in enumerate(splitter.split(indices, y_array)):
        repeat_id = split_index // n_splits + 1
        fold_id = split_index % n_splits + 1
        splits.append(
            OOFSplit(
                repeat_id=repeat_id,
                fold_id=fold_id,
                train_idx=train_idx,
                valid_idx=valid_idx,
            )
        )
    return splits


def _impute_median(
    X_train: pd.DataFrame,
    X_valid: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Fit median imputer on fold_train and transform fold_valid."""

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


def _bin_projection_section(oof_config: dict[str, Any]) -> dict[str, Any]:
    """Return Day17 bin projection config section."""

    return oof_config["bin_projection"]


def prepare_oof_feature_set(
    fold_train_df: pd.DataFrame,
    fold_valid_df: pd.DataFrame,
    cfg: ScaniaConfig,
    structural_config: dict[str, Any],
    oof_config: dict[str, Any],
    candidate_strategy: str,
) -> OOFTuningFeatureSet:
    """Prepare one candidate strategy for a single OOF fold."""

    if candidate_strategy not in VALID_OOF_STRATEGIES:
        raise ValueError(f"Unsupported Day17 candidate_strategy: {candidate_strategy}")

    X_train_raw, y_train = split_features_target(fold_train_df, cfg.label_column)
    X_valid_raw, y_valid = split_features_target(fold_valid_df, cfg.label_column)
    X_train_original, X_valid_original = _impute_median(X_train_raw, X_valid_raw)

    feature_frames_train = [X_train_original]
    feature_frames_valid = [X_valid_original]
    structural_feature_names: list[str] = []
    bin_feature_names: list[str] = []
    bin_metadata = pd.DataFrame()

    if candidate_strategy in {
        "median_all_structural_all",
        "median_all_structural_all_plus_bin_projection",
    }:
        structural_builder = fit_structural_feature_builder(
            train_inner_df=fold_train_df,
            cfg=cfg,
            structural_config=structural_config,
            feature_group="median_all_structural_all",
        )
        X_train_structural = transform_structural_features(fold_train_df, structural_builder)
        X_valid_structural = transform_structural_features(fold_valid_df, structural_builder)
        structural_feature_names = X_train_structural.columns.tolist()
        feature_frames_train.append(X_train_structural)
        feature_frames_valid.append(X_valid_structural)

    if candidate_strategy in {
        "median_all_bin_projection",
        "median_all_structural_all_plus_bin_projection",
    }:
        bin_config = _bin_projection_section(oof_config)
        bin_builder = fit_bin_projection_builder(
            train_df=fold_train_df,
            feature_cols=X_train_raw.columns.tolist(),
            candidate_prefix_groups=list(bin_config["candidate_prefix_groups"]),
            config=bin_config,
        )
        X_train_bin = transform_bin_projection_features(fold_train_df, bin_builder)
        X_valid_bin = transform_bin_projection_features(fold_valid_df, bin_builder)
        bin_feature_names = X_train_bin.columns.tolist()
        feature_frames_train.append(X_train_bin)
        feature_frames_valid.append(X_valid_bin)
        bin_metadata = build_bin_projection_metadata(bin_builder)

    X_train = pd.concat(feature_frames_train, axis=1)
    X_valid = pd.concat(feature_frames_valid, axis=1)
    metadata = {
        "candidate_strategy": candidate_strategy,
        "fit_dataset": "fold_train",
        "evaluation_dataset": "fold_valid",
        "uses_official_test": False,
        "n_original_features": X_train_original.shape[1],
        "n_structural_features": len(structural_feature_names),
        "n_bin_projection_features": len(bin_feature_names),
        "n_total_features": X_train.shape[1],
        "structural_feature_names": "|".join(structural_feature_names),
        "bin_projection_feature_names": "|".join(bin_feature_names),
    }
    return OOFTuningFeatureSet(
        X_train=X_train,
        X_valid=X_valid,
        y_train=y_train.copy(),
        y_valid=y_valid.copy(),
        metadata=metadata,
        bin_projection_metadata=bin_metadata,
    )


def train_oof_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    cfg: ScaniaConfig,
    candidate_strategy: str,
) -> XGBClassifier:
    """Train a non-tuned XGBoost model for one OOF fold."""

    model_config = _oof_config(cfg)["model"]
    base_params = dict(cfg.advanced_models["xgboost"])
    params = {
        "n_estimators": int(base_params["n_estimators"]),
        "max_depth": int(base_params["max_depth"]),
        "learning_rate": float(base_params["learning_rate"]),
        "subsample": float(base_params["subsample"]),
        "colsample_bytree": float(base_params["colsample_bytree"]),
        "objective": model_config.get("objective", "binary:logistic"),
        "eval_metric": model_config.get("eval_metric", base_params.get("eval_metric", "aucpr")),
        "tree_method": model_config.get("tree_method", "hist"),
        "n_jobs": int(model_config.get("n_jobs", base_params.get("n_jobs", -1))),
        "random_state": int(_oof_config(cfg).get("random_state", cfg.random_state)),
        "scale_pos_weight": calculate_scale_pos_weight(y_train),
    }
    return XGBClassifier(**params)


def _positive_class_proba(model: Any, X: pd.DataFrame) -> np.ndarray:
    """Extract positive-class probability."""

    proba = model.predict_proba(X)
    classes = list(getattr(model, "classes_", []))
    positive_index = classes.index(1) if 1 in classes else proba.shape[1] - 1
    return proba[:, positive_index]


def generate_oof_predictions(
    train_df: pd.DataFrame,
    cfg: ScaniaConfig,
    structural_config: dict[str, Any],
    oof_config: dict[str, Any],
    candidate_strategies: Iterable[str],
) -> dict[str, pd.DataFrame]:
    """Generate raw and averaged OOF predictions for candidate strategies."""

    y = train_df["target"].astype(int)
    splits = build_oof_splits(y, cfg)
    raw_prediction_frames: list[pd.DataFrame] = []
    metadata_rows: list[dict[str, Any]] = []
    bin_metadata_frames: list[pd.DataFrame] = []
    fold_rows: list[dict[str, Any]] = []

    for candidate_strategy in candidate_strategies:
        for split in splits:
            fold_train_df = train_df.iloc[split.train_idx].copy()
            fold_valid_df = train_df.iloc[split.valid_idx].copy()
            feature_set = prepare_oof_feature_set(
                fold_train_df=fold_train_df,
                fold_valid_df=fold_valid_df,
                cfg=cfg,
                structural_config=structural_config,
                oof_config=oof_config,
                candidate_strategy=candidate_strategy,
            )
            model = train_oof_model(
                X_train=feature_set.X_train,
                y_train=feature_set.y_train,
                cfg=cfg,
                candidate_strategy=candidate_strategy,
            )
            model.fit(feature_set.X_train, feature_set.y_train)
            y_proba = _positive_class_proba(model, feature_set.X_valid)

            raw_prediction_frames.append(
                pd.DataFrame(
                    {
                        "sample_index": fold_valid_df.index.to_numpy(),
                        "y_true": feature_set.y_valid.to_numpy(dtype=int),
                        "y_proba": y_proba,
                        "candidate_strategy": candidate_strategy,
                        "repeat_id": split.repeat_id,
                        "fold_id": split.fold_id,
                        "model_name": "xgboost_oof",
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
                    "candidate_strategy": candidate_strategy,
                    "repeat_id": split.repeat_id,
                    "fold_id": split.fold_id,
                    "train_rows": len(fold_train_df),
                    "valid_rows": len(fold_valid_df),
                    "train_pos": int(feature_set.y_train.sum()),
                    "valid_pos": int(feature_set.y_valid.sum()),
                }
            )
            if not feature_set.bin_projection_metadata.empty:
                bin_metadata_frames.append(
                    feature_set.bin_projection_metadata.assign(
                        candidate_strategy=candidate_strategy,
                        repeat_id=split.repeat_id,
                        fold_id=split.fold_id,
                    )
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
            raw_oof_predictions.groupby(["candidate_strategy", "sample_index"], as_index=False)
            .agg(
                y_true=("y_true", "first"),
                y_proba=("y_proba", "mean"),
                oof_prediction_count=("y_proba", "size"),
                model_name=("model_name", "first"),
            )
            .sort_values(["candidate_strategy", "sample_index"])
            .reset_index(drop=True)
        )

    return {
        "raw_oof_predictions": raw_oof_predictions,
        "averaged_oof_predictions": averaged_oof_predictions,
        "candidate_metadata": pd.DataFrame(metadata_rows),
        "fold_summary": pd.DataFrame(fold_rows),
        "bin_projection_metadata": (
            pd.concat(bin_metadata_frames, ignore_index=True)
            if bin_metadata_frames
            else pd.DataFrame()
        ),
    }


def _select_rule_best(
    threshold_df: pd.DataFrame,
    rule: str,
    cfg: ScaniaConfig,
) -> pd.Series:
    """Select one threshold under a cost/recall/FN rule."""

    candidates = threshold_df.copy()
    constraint_satisfied = True
    oof_config = _oof_config(cfg)

    if rule.startswith("recall_floor"):
        floor = float(oof_config["recall_floors"][rule])
        candidates = candidates[candidates["recall"] >= floor]
    elif rule.startswith("fn_floor"):
        floor = int(oof_config["fn_floors"][rule])
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


def evaluate_threshold_grid_with_constraints(
    oof_predictions: pd.DataFrame,
    cfg: ScaniaConfig,
    threshold_grid: Iterable[float] | None = None,
    threshold_selection_rules: Iterable[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Evaluate OOF threshold grid and apply business constraints."""

    oof_config = _oof_config(cfg)
    thresholds = list(threshold_grid) if threshold_grid is not None else _threshold_values(oof_config)
    rules = list(threshold_selection_rules or oof_config["threshold_selection_rules"])

    threshold_frames: list[pd.DataFrame] = []
    summary_rows: list[pd.Series] = []

    for candidate_strategy, group in oof_predictions.groupby("candidate_strategy", dropna=False):
        threshold_df = evaluate_threshold_grid(
            y_true=group["y_true"],
            y_proba=group["y_proba"],
            cfg=cfg,
            model_name="xgboost_oof",
            strategy=candidate_strategy,
            thresholds=thresholds,
        )
        threshold_df["candidate_strategy"] = candidate_strategy
        threshold_df["selection_dataset"] = "oof_averaged"
        threshold_frames.append(threshold_df)

        for rule in rules:
            summary_rows.append(_select_rule_best(threshold_df, rule, cfg))

    threshold_metrics = (
        pd.concat(threshold_frames, ignore_index=True) if threshold_frames else pd.DataFrame()
    )
    best_threshold_summary = pd.DataFrame(summary_rows)
    if not best_threshold_summary.empty:
        best_threshold_summary = best_threshold_summary.sort_values(
            ["threshold_selection_rule", "total_cost", "fn", "recall"],
            ascending=[True, True, True, False],
        ).reset_index(drop=True)
    return threshold_metrics, best_threshold_summary


def summarize_oof_stability(
    raw_oof_predictions: pd.DataFrame,
    threshold_summary: pd.DataFrame,
    cfg: ScaniaConfig,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Summarize fold/repeat metric variability under selected thresholds."""

    fold_rows: list[dict[str, Any]] = []
    for _, selected in threshold_summary.iterrows():
        candidate_strategy = selected["candidate_strategy"]
        threshold = float(selected["threshold"])
        rule = selected["threshold_selection_rule"]
        strategy_predictions = raw_oof_predictions[
            raw_oof_predictions["candidate_strategy"].eq(candidate_strategy)
        ]
        for (repeat_id, fold_id), group in strategy_predictions.groupby(["repeat_id", "fold_id"]):
            y_pred = (group["y_proba"].to_numpy(dtype=float) >= threshold).astype(int)
            metrics = evaluate_binary_classifier(
                y_true=group["y_true"].astype(int),
                y_pred=y_pred,
                y_proba=group["y_proba"],
                cfg=cfg,
                model_name="xgboost_oof",
                strategy=candidate_strategy,
                threshold=threshold,
            )
            fold_rows.append(
                {
                    "candidate_strategy": candidate_strategy,
                    "threshold_selection_rule": rule,
                    "repeat_id": repeat_id,
                    "fold_id": fold_id,
                    "threshold": threshold,
                    **metrics,
                }
            )

    fold_metrics = pd.DataFrame(fold_rows)
    if fold_metrics.empty:
        return pd.DataFrame(), pd.DataFrame()

    stability_summary = (
        fold_metrics.groupby(["candidate_strategy", "threshold_selection_rule"], as_index=False)
        .agg(
            selected_threshold=("threshold", "first"),
            mean_cost=("total_cost", "mean"),
            std_cost=("total_cost", "std"),
            mean_fn=("fn", "mean"),
            std_fn=("fn", "std"),
            mean_recall=("recall", "mean"),
            std_recall=("recall", "std"),
            mean_precision=("precision", "mean"),
            std_precision=("precision", "std"),
            mean_f2=("f2", "mean"),
            std_f2=("f2", "std"),
        )
        .fillna(0.0)
    )
    return stability_summary, fold_metrics


def run_oof_recall_floor_bin_projection_experiments(
    train_df: pd.DataFrame,
    cfg: ScaniaConfig,
    structural_config: dict[str, Any],
    oof_config: dict[str, Any] | None = None,
    candidate_strategies: Iterable[str] | None = None,
) -> dict[str, pd.DataFrame]:
    """Run Day17 OOF threshold and bin projection experiments."""

    oof_config = oof_config or _oof_config(cfg)
    strategies = list(candidate_strategies or oof_config["candidate_strategies"])
    prediction_outputs = generate_oof_predictions(
        train_df=train_df,
        cfg=cfg,
        structural_config=structural_config,
        oof_config=oof_config,
        candidate_strategies=strategies,
    )
    threshold_metrics, best_threshold_summary = evaluate_threshold_grid_with_constraints(
        oof_predictions=prediction_outputs["averaged_oof_predictions"],
        cfg=cfg,
        threshold_grid=_threshold_values(oof_config),
        threshold_selection_rules=oof_config["threshold_selection_rules"],
    )
    stability_summary, fold_metric_summary = summarize_oof_stability(
        raw_oof_predictions=prediction_outputs["raw_oof_predictions"],
        threshold_summary=best_threshold_summary,
        cfg=cfg,
    )

    strategy_compare = best_threshold_summary.sort_values(
        ["threshold_selection_rule", "total_cost", "fn"],
        ascending=[True, True, True],
    ).reset_index(drop=True)

    return {
        "oof_threshold_metrics": threshold_metrics,
        "oof_best_threshold_summary": best_threshold_summary,
        "oof_stability_summary": stability_summary,
        "oof_strategy_compare": strategy_compare,
        "raw_oof_predictions": prediction_outputs["raw_oof_predictions"],
        "averaged_oof_predictions": prediction_outputs["averaged_oof_predictions"],
        "oof_fold_summary": prediction_outputs["fold_summary"],
        "bin_projection_metadata": prediction_outputs["bin_projection_metadata"],
        "oof_candidate_metadata": prediction_outputs["candidate_metadata"],
        "oof_fold_metric_summary": fold_metric_summary,
    }
