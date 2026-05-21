"""Day 15 受控 XGBoost 调参工具。

本模块只使用 train_inner / valid。official test 不参与参数、特征方案或阈值选择。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from xgboost import XGBClassifier

from scania_aps.config import ScaniaConfig
from scania_aps.data.clean_data import (
    get_high_missing_features,
    split_features_target,
)
from scania_aps.evaluation.threshold_utils import (
    evaluate_threshold_grid,
)
from scania_aps.features.structural_features import (
    fit_structural_feature_builder,
    transform_structural_features,
)


INT_PARAMS = {"n_estimators", "max_depth", "max_delta_step"}
VALID_STRATEGIES = {
    "baseline_median_all",
    "median_all_structural_all",
    "drop_high_missing_median",
    "drop_80_missing_median",
}
PARAM_COLUMNS = [
    "n_estimators",
    "learning_rate",
    "max_depth",
    "min_child_weight",
    "subsample",
    "colsample_bytree",
    "gamma",
    "reg_lambda",
    "reg_alpha",
    "scale_pos_weight",
    "max_delta_step",
]


@dataclass(frozen=True)
class TuningFeatureSet:
    """单个候选策略对应的 train_inner / valid 特征矩阵。"""

    X_train: pd.DataFrame
    X_valid: pd.DataFrame
    y_train: pd.Series
    y_valid: pd.Series
    metadata: dict[str, Any]


def _threshold_values(cfg: ScaniaConfig) -> np.ndarray:
    """从 cfg 读取 Day15 阈值网格。"""

    grid = cfg.xgb_tuning["threshold_grid"]
    start = float(grid["start"])
    stop = float(grid["stop"])
    step = float(grid["step"])
    return np.round(np.arange(start, stop + step / 2, step), 6)


def _ranking_columns() -> tuple[list[str], list[bool]]:
    """Day15 valid 排序规则：先成本，再 FN，再 recall/F2/AP。"""

    return (
        ["total_cost", "fn", "recall", "f2", "average_precision"],
        [True, True, False, False, False],
    )


def _sort_trial_rows(df: pd.DataFrame) -> pd.DataFrame:
    """按 Day15 规则排序 trial 级结果。"""

    if df.empty:
        return df
    columns, ascending = _ranking_columns()
    return df.sort_values(columns, ascending=ascending).reset_index(drop=True)


def _param_columns_present(df: pd.DataFrame) -> list[str]:
    """返回结果表中实际存在的参数列。"""

    return [f"param_{name}" for name in PARAM_COLUMNS if f"param_{name}" in df.columns]


def sample_xgb_params(search_space: dict[str, Any], rng: np.random.Generator) -> dict[str, Any]:
    """从配置化搜索空间随机采样一组 XGBoost 参数。"""

    params: dict[str, Any] = {}
    for name, spec in search_space.items():
        if "values" in spec:
            value = rng.choice(spec["values"]).item()
        else:
            low = float(spec["min"])
            high = float(spec["max"])
            distribution = spec.get("distribution", "uniform")
            if distribution == "log_uniform":
                if low <= 0 or high <= 0:
                    raise ValueError(f"{name} 使用 log_uniform 时 min/max 必须大于 0。")
                value = float(np.exp(rng.uniform(np.log(low), np.log(high))))
            elif distribution == "uniform":
                value = float(rng.uniform(low, high))
            else:
                raise ValueError(f"不支持的参数分布：{distribution}")

        if name in INT_PARAMS:
            value = int(round(value))
        params[name] = value

    return params


def _numeric_interval(values: pd.Series, original_spec: dict[str, Any]) -> dict[str, Any]:
    """基于 top trials 的分位数构造不过窄的连续 refine 区间。"""

    values = values.dropna().astype(float)
    if values.empty:
        return original_spec

    original_min = float(original_spec["min"])
    original_max = float(original_spec["max"])
    q10 = float(values.quantile(0.10))
    q90 = float(values.quantile(0.90))
    if q10 == q90:
        span = max(abs(q10) * 0.25, (original_max - original_min) * 0.05)
    else:
        span = (q90 - q10) * 0.25

    refined_min = max(original_min, q10 - span)
    refined_max = min(original_max, q90 + span)
    if refined_min >= refined_max:
        refined_min, refined_max = original_min, original_max

    refined = {
        "min": refined_min,
        "max": refined_max,
    }
    if "distribution" in original_spec:
        refined["distribution"] = original_spec["distribution"]
    return refined


def _discrete_values(
    values: pd.Series,
    original_spec: dict[str, Any],
    *,
    width: int = 1,
) -> dict[str, Any]:
    """基于 top trials 为离散参数生成邻近候选值。"""

    original_values = list(original_spec["values"])
    selected: set[Any] = set()
    for value in values.dropna().astype(int).unique().tolist():
        if value in original_values:
            index = original_values.index(value)
            for near_index in range(max(0, index - width), min(len(original_values), index + width + 1)):
                selected.add(original_values[near_index])
    if not selected:
        selected = set(original_values)
    return {"values": sorted(selected)}


def summarize_top_trials_for_refinement(top_trials: pd.DataFrame) -> dict[str, Any]:
    """根据 broad 阶段 top trials 生成 refined search space。"""

    if top_trials.empty:
        raise ValueError("top_trials 为空，无法构造 refined search space。")
    if "original_search_space" not in top_trials.attrs:
        raise ValueError("top_trials.attrs 缺少 original_search_space。")

    original_space: dict[str, Any] = top_trials.attrs["original_search_space"]
    refined_space: dict[str, Any] = {}

    for name, original_spec in original_space.items():
        column = f"param_{name}"
        if column not in top_trials.columns:
            refined_space[name] = original_spec
            continue

        if "values" in original_spec:
            refined_space[name] = _discrete_values(top_trials[column], original_spec)
        elif name in INT_PARAMS:
            interval = _numeric_interval(top_trials[column], original_spec)
            refined_space[name] = {
                "min": int(max(int(original_spec["min"]), round(interval["min"]))),
                "max": int(min(int(original_spec["max"]), round(interval["max"]))),
            }
            if refined_space[name]["min"] >= refined_space[name]["max"]:
                refined_space[name] = original_spec
        else:
            refined_space[name] = _numeric_interval(top_trials[column], original_spec)

    return refined_space


def _impute_median(
    X_train: pd.DataFrame,
    X_valid: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, SimpleImputer]:
    """只在 train_inner 上 fit median imputer，再 transform valid。"""

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
    return X_train_processed, X_valid_processed, imputer


def prepare_tuning_feature_set(
    train_inner_df: pd.DataFrame,
    valid_df: pd.DataFrame,
    cfg: ScaniaConfig,
    structural_config: dict[str, Any],
    candidate_strategy: str,
) -> TuningFeatureSet:
    """为 Day15 候选策略准备 train_inner / valid 特征矩阵。"""

    if candidate_strategy not in VALID_STRATEGIES:
        raise ValueError(f"Day15 不支持的 candidate_strategy：{candidate_strategy}")

    normalized_strategy = (
        "drop_high_missing_median"
        if candidate_strategy == "drop_80_missing_median"
        else candidate_strategy
    )

    X_train_raw, y_train = split_features_target(train_inner_df, cfg.label_column)
    X_valid_raw, y_valid = split_features_target(valid_df, cfg.label_column)
    dropped_features: list[str] = []

    if normalized_strategy == "drop_high_missing_median":
        dropped_features = get_high_missing_features(
            X_train=X_train_raw,
            threshold=cfg.high_missing_threshold,
        )
        X_train_raw = X_train_raw.drop(columns=dropped_features)
        X_valid_raw = X_valid_raw.drop(columns=dropped_features)

    X_train_original, X_valid_original, _imputer = _impute_median(X_train_raw, X_valid_raw)
    X_train_structural = pd.DataFrame(index=train_inner_df.index)
    X_valid_structural = pd.DataFrame(index=valid_df.index)
    structural_feature_names: list[str] = []

    if normalized_strategy == "median_all_structural_all":
        builder = fit_structural_feature_builder(
            train_inner_df=train_inner_df,
            cfg=cfg,
            structural_config=structural_config,
            feature_group="median_all_structural_all",
        )
        X_train_structural = transform_structural_features(train_inner_df, builder)
        X_valid_structural = transform_structural_features(valid_df, builder)
        structural_feature_names = X_train_structural.columns.tolist()

    X_train = pd.concat([X_train_original, X_train_structural], axis=1)
    X_valid = pd.concat([X_valid_original, X_valid_structural], axis=1)
    metadata = {
        "candidate_strategy": candidate_strategy,
        "normalized_strategy": normalized_strategy,
        "fit_dataset": "train_inner",
        "evaluation_dataset": "valid",
        "uses_official_test": False,
        "n_original_features": X_train_original.shape[1],
        "n_structural_features": X_train_structural.shape[1],
        "n_total_features": X_train.shape[1],
        "n_dropped_features": len(dropped_features),
        "dropped_features": "|".join(dropped_features),
        "structural_feature_names": "|".join(structural_feature_names),
    }
    return TuningFeatureSet(
        X_train=X_train,
        X_valid=X_valid,
        y_train=y_train.copy(),
        y_valid=y_valid.copy(),
        metadata=metadata,
    )


def _build_xgb_classifier(cfg: ScaniaConfig, params: dict[str, Any]) -> XGBClassifier:
    """用 fixed params + sampled params 构造 XGBoost。"""

    fixed_params = dict(cfg.xgb_tuning["xgb_fixed_params"])
    model_params = {
        **fixed_params,
        **params,
        "random_state": int(cfg.xgb_tuning.get("random_state", cfg.random_state)),
    }
    return XGBClassifier(**model_params)


def _positive_class_proba(model: Any, X: pd.DataFrame) -> np.ndarray:
    """提取正类预测概率。"""

    proba = model.predict_proba(X)
    classes = list(getattr(model, "classes_", []))
    positive_index = classes.index(1) if 1 in classes else proba.shape[1] - 1
    return proba[:, positive_index]


def _best_trial_from_threshold_metrics(threshold_metrics: pd.DataFrame) -> pd.Series:
    """从一个 trial 的阈值结果中选择 valid total_cost 最低的记录。"""

    columns, ascending = _ranking_columns()
    return threshold_metrics.sort_values(columns, ascending=ascending).iloc[0]


def evaluate_xgb_trial(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_valid: pd.DataFrame,
    y_valid: pd.Series,
    cfg: ScaniaConfig,
    params: dict[str, Any],
    candidate_strategy: str,
    trial_id: str,
    search_stage: str,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """训练单个 XGBoost trial，并在 valid 上遍历阈值。"""

    model = _build_xgb_classifier(cfg, params)
    model.fit(X_train, y_train)
    y_valid_proba = _positive_class_proba(model, X_valid)

    threshold_metrics = evaluate_threshold_grid(
        y_true=y_valid,
        y_proba=y_valid_proba,
        cfg=cfg,
        model_name="xgboost_tuned",
        strategy=candidate_strategy,
        thresholds=_threshold_values(cfg),
    )
    threshold_metrics["dataset"] = "valid"
    threshold_metrics["candidate_strategy"] = candidate_strategy
    threshold_metrics["trial_id"] = trial_id
    threshold_metrics["search_stage"] = search_stage
    threshold_metrics["n_total_features"] = X_train.shape[1]
    for name, value in params.items():
        threshold_metrics[f"param_{name}"] = value

    best = _best_trial_from_threshold_metrics(threshold_metrics)
    best_record = best.to_dict()
    return threshold_metrics, best_record


def _trial_count(cfg: ScaniaConfig, key: str) -> int:
    """读取 trial 数；支持脚本通过环境变量在资源受限时显式覆盖。"""

    return int(cfg.xgb_tuning[key])


def _top_trials_for_refinement(
    best_records: pd.DataFrame,
    broad_space: dict[str, Any],
    *,
    top_n: int,
) -> pd.DataFrame:
    """取 broad 阶段 top trials，并附带原始 search space。"""

    top = _sort_trial_rows(best_records).head(top_n).copy()
    top.attrs["original_search_space"] = broad_space
    return top


def _search_space_to_rows(
    search_space: dict[str, Any],
    *,
    candidate_strategy: str,
    search_stage: str,
) -> list[dict[str, Any]]:
    """展开搜索空间，便于保存复盘。"""

    rows = []
    for param_name, spec in search_space.items():
        row = {
            "candidate_strategy": candidate_strategy,
            "search_stage": search_stage,
            "param_name": param_name,
            "distribution": spec.get("distribution", "values" if "values" in spec else "uniform"),
            "min": spec.get("min"),
            "max": spec.get("max"),
            "values": "|".join(map(str, spec.get("values", []))) if "values" in spec else None,
        }
        rows.append(row)
    return rows


def _fit_predict_best_trial(
    feature_set: TuningFeatureSet,
    cfg: ScaniaConfig,
    best_row: pd.Series,
) -> pd.DataFrame:
    """重新训练每个候选策略的 best trial，保存 valid 预测概率。"""

    params = {
        name.replace("param_", ""): best_row[name]
        for name in _param_columns_present(pd.DataFrame([best_row]))
    }
    for int_param in INT_PARAMS:
        if int_param in params:
            params[int_param] = int(params[int_param])

    model = _build_xgb_classifier(cfg, params)
    model.fit(feature_set.X_train, feature_set.y_train)
    y_proba = _positive_class_proba(model, feature_set.X_valid)
    threshold = float(best_row["threshold"])
    return pd.DataFrame(
        {
            "dataset": "valid",
            "original_index": feature_set.y_valid.index.to_numpy(),
            "y_true": feature_set.y_valid.to_numpy(),
            "y_proba": y_proba,
            "y_pred": (y_proba >= threshold).astype(int),
            "model_name": "xgboost_tuned",
            "candidate_strategy": best_row["candidate_strategy"],
            "threshold": threshold,
            "trial_id": best_row["trial_id"],
            "search_stage": best_row["search_stage"],
        }
    )


def run_xgb_tuning_experiments(
    train_inner_df: pd.DataFrame,
    valid_df: pd.DataFrame,
    cfg: ScaniaConfig,
    structural_config: dict[str, Any],
    candidate_strategies: Iterable[str] | None = None,
) -> dict[str, pd.DataFrame]:
    """运行 Day15 two-stage randomized search。"""

    strategies = list(candidate_strategies or cfg.xgb_tuning["candidate_strategies"])
    rng = np.random.default_rng(int(cfg.xgb_tuning.get("random_state", cfg.random_state)))
    broad_trials = _trial_count(cfg, "broad_trials_per_strategy")
    refine_trials = _trial_count(cfg, "refine_trials_per_strategy")
    broad_space = cfg.xgb_tuning["search_space_broad"]

    threshold_frames: list[pd.DataFrame] = []
    trial_best_rows: list[dict[str, Any]] = []
    metadata_rows: list[dict[str, Any]] = []
    refinement_rows: list[dict[str, Any]] = []
    top_trial_frames: list[pd.DataFrame] = []
    search_space_rows: list[dict[str, Any]] = []
    best_prediction_frames: list[pd.DataFrame] = []

    for candidate_strategy in strategies:
        try:
            feature_set = prepare_tuning_feature_set(
                train_inner_df=train_inner_df,
                valid_df=valid_df,
                cfg=cfg,
                structural_config=structural_config,
                candidate_strategy=candidate_strategy,
            )
            metadata_rows.append(
                {
                    **feature_set.metadata,
                    "status": "success",
                    "broad_trials_requested": broad_trials,
                    "refine_trials_requested": refine_trials,
                }
            )
            search_space_rows.extend(
                _search_space_to_rows(
                    broad_space,
                    candidate_strategy=candidate_strategy,
                    search_stage="broad",
                )
            )

            broad_best_rows: list[dict[str, Any]] = []
            for trial_index in range(1, broad_trials + 1):
                params = sample_xgb_params(broad_space, rng)
                trial_id = f"{candidate_strategy}_broad_{trial_index:03d}"
                threshold_metrics, best_record = evaluate_xgb_trial(
                    X_train=feature_set.X_train,
                    y_train=feature_set.y_train,
                    X_valid=feature_set.X_valid,
                    y_valid=feature_set.y_valid,
                    cfg=cfg,
                    params=params,
                    candidate_strategy=candidate_strategy,
                    trial_id=trial_id,
                    search_stage="broad",
                )
                threshold_metrics = threshold_metrics.assign(**feature_set.metadata)
                best_record.update(feature_set.metadata)
                threshold_frames.append(threshold_metrics)
                trial_best_rows.append(best_record)
                broad_best_rows.append(best_record)

            broad_best_df = _sort_trial_rows(pd.DataFrame(broad_best_rows))
            top_n = min(max(10, broad_trials // 5), 20, len(broad_best_df))
            top_trials = _top_trials_for_refinement(
                broad_best_df,
                broad_space,
                top_n=top_n,
            )
            top_trial_frames.append(top_trials.assign(top_rank=range(1, len(top_trials) + 1)))
            refined_space = summarize_top_trials_for_refinement(top_trials)
            search_space_rows.extend(
                _search_space_to_rows(
                    refined_space,
                    candidate_strategy=candidate_strategy,
                    search_stage="refined",
                )
            )

            refined_best_rows: list[dict[str, Any]] = []
            for trial_index in range(1, refine_trials + 1):
                params = sample_xgb_params(refined_space, rng)
                trial_id = f"{candidate_strategy}_refined_{trial_index:03d}"
                threshold_metrics, best_record = evaluate_xgb_trial(
                    X_train=feature_set.X_train,
                    y_train=feature_set.y_train,
                    X_valid=feature_set.X_valid,
                    y_valid=feature_set.y_valid,
                    cfg=cfg,
                    params=params,
                    candidate_strategy=candidate_strategy,
                    trial_id=trial_id,
                    search_stage="refined",
                )
                threshold_metrics = threshold_metrics.assign(**feature_set.metadata)
                best_record.update(feature_set.metadata)
                threshold_frames.append(threshold_metrics)
                trial_best_rows.append(best_record)
                refined_best_rows.append(best_record)

            refined_best_df = _sort_trial_rows(pd.DataFrame(refined_best_rows))
            broad_best = broad_best_df.iloc[0]
            refined_best = refined_best_df.iloc[0]
            combined_best = _sort_trial_rows(
                pd.concat([broad_best_df.head(1), refined_best_df.head(1)], ignore_index=True)
            ).iloc[0]
            refinement_rows.append(
                {
                    "candidate_strategy": candidate_strategy,
                    "broad_trials": broad_trials,
                    "refine_trials": refine_trials,
                    "top_trials_used_for_refinement": top_n,
                    "broad_best_trial_id": broad_best["trial_id"],
                    "broad_best_total_cost": broad_best["total_cost"],
                    "broad_best_fn": broad_best["fn"],
                    "refined_best_trial_id": refined_best["trial_id"],
                    "refined_best_total_cost": refined_best["total_cost"],
                    "refined_best_fn": refined_best["fn"],
                    "best_stage": combined_best["search_stage"],
                    "best_trial_id": combined_best["trial_id"],
                    "best_total_cost": combined_best["total_cost"],
                    "refined_cost_delta_vs_broad": refined_best["total_cost"] - broad_best["total_cost"],
                }
            )

            strategy_best = _sort_trial_rows(
                pd.DataFrame([row for row in trial_best_rows if row["candidate_strategy"] == candidate_strategy])
            ).iloc[0]
            best_prediction_frames.append(_fit_predict_best_trial(feature_set, cfg, strategy_best))

        except Exception as exc:  # noqa: BLE001
            metadata_rows.append(
                {
                    "candidate_strategy": candidate_strategy,
                    "status": "failed",
                    "error_message": str(exc),
                    "uses_official_test": False,
                }
            )

    tuning_threshold_metrics = (
        pd.concat(threshold_frames, ignore_index=True)
        if threshold_frames
        else pd.DataFrame()
    )
    tuning_trial_results = (
        _sort_trial_rows(pd.DataFrame(trial_best_rows)) if trial_best_rows else pd.DataFrame()
    )
    if not tuning_trial_results.empty:
        tuning_trial_results.insert(0, "global_trial_rank", range(1, len(tuning_trial_results) + 1))

    best_summary_rows = []
    if not tuning_trial_results.empty:
        for candidate_strategy, group in tuning_trial_results.groupby("candidate_strategy", dropna=False):
            best_summary_rows.append(_sort_trial_rows(group).iloc[0].to_dict())
    tuning_best_summary = _sort_trial_rows(pd.DataFrame(best_summary_rows))
    if not tuning_best_summary.empty:
        tuning_best_summary.insert(0, "selection_rank", range(1, len(tuning_best_summary) + 1))
        tuning_best_summary["selection_dataset"] = "valid"

    tuning_candidate_metadata = pd.DataFrame(metadata_rows)
    tuning_refinement_summary = pd.DataFrame(refinement_rows)
    tuning_top_trials_by_strategy = (
        pd.concat(top_trial_frames, ignore_index=True) if top_trial_frames else pd.DataFrame()
    )
    tuning_search_space = pd.DataFrame(search_space_rows)
    tuning_best_predictions = (
        pd.concat(best_prediction_frames, ignore_index=True)
        if best_prediction_frames
        else pd.DataFrame()
    )

    return {
        "tuning_trial_results": tuning_trial_results,
        "tuning_best_summary": tuning_best_summary,
        "tuning_threshold_metrics": tuning_threshold_metrics,
        "tuning_candidate_metadata": tuning_candidate_metadata,
        "tuning_best_predictions": tuning_best_predictions,
        "tuning_refinement_summary": tuning_refinement_summary,
        "tuning_top_trials_by_strategy": tuning_top_trials_by_strategy,
        "tuning_search_space": tuning_search_space,
    }
