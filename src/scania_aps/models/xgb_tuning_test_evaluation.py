"""Day 16 tuned XGBoost official test 观察工具。

本模块只读取 Day15 在 valid 上选出的参数和阈值，然后在 official test 上做一次固定评估。
official test 不参与参数选择、阈值选择或特征规则拟合。
"""

from __future__ import annotations

from typing import Any, Iterable

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer

from scania_aps.config import ScaniaConfig
from scania_aps.data.clean_data import (
    get_high_missing_features,
    split_features_target,
)
from scania_aps.evaluation.metrics import evaluate_binary_classifier
from scania_aps.features.structural_features import (
    fit_structural_feature_builder,
    transform_structural_features,
)
from scania_aps.models.xgb_tuning import (
    INT_PARAMS,
    PARAM_COLUMNS,
    _build_xgb_classifier,
)


DEFAULT_DAY16_CANDIDATE_STRATEGIES = [
    "median_all_structural_all",
    "drop_high_missing_median",
    "baseline_median_all",
]


def _strategy_column(day15_best_summary: pd.DataFrame) -> str:
    """兼容读取 Day15 best summary 中的策略列。"""

    if "candidate_strategy" in day15_best_summary.columns:
        return "candidate_strategy"
    if "strategy" in day15_best_summary.columns:
        return "strategy"
    raise ValueError("day15_best_summary 缺少 candidate_strategy 或 strategy 列。")


def _day15_row_for_strategy(
    day15_best_summary: pd.DataFrame,
    candidate_strategy: str,
) -> pd.Series:
    """读取指定候选策略的 Day15 valid 最优记录。"""

    strategy_col = _strategy_column(day15_best_summary)
    matched = day15_best_summary[day15_best_summary[strategy_col].eq(candidate_strategy)]
    if matched.empty:
        raise ValueError(f"Day15 best summary 中找不到候选策略：{candidate_strategy}")
    return matched.iloc[0]


def _params_from_day15_row(row: pd.Series) -> dict[str, Any]:
    """从 Day15 summary 行中提取 XGBoost 参数。"""

    params: dict[str, Any] = {}
    for name in PARAM_COLUMNS:
        column = f"param_{name}"
        if column not in row or pd.isna(row[column]):
            continue
        value = row[column]
        if name in INT_PARAMS:
            value = int(round(float(value)))
        else:
            value = float(value)
        params[name] = value

    missing = [name for name in PARAM_COLUMNS if name not in params]
    if missing:
        raise ValueError(f"Day15 summary 缺少必要 XGBoost 参数：{missing}")
    return params


def _positive_class_proba(model: Any, X: pd.DataFrame) -> np.ndarray:
    """提取正类预测概率。"""

    proba = model.predict_proba(X)
    classes = list(getattr(model, "classes_", []))
    positive_index = classes.index(1) if 1 in classes else proba.shape[1] - 1
    return proba[:, positive_index]


def _prepare_train_test_feature_set(
    train_inner_df: pd.DataFrame,
    test_df: pd.DataFrame,
    cfg: ScaniaConfig,
    structural_config: dict[str, Any],
    candidate_strategy: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, dict[str, Any]]:
    """复用 Day15 特征规则，在 train_inner 上 fit，再 transform official test。"""

    X_train_raw, y_train = split_features_target(train_inner_df, cfg.label_column)
    X_test_raw, y_test = split_features_target(test_df, cfg.label_column)
    dropped_features: list[str] = []

    if candidate_strategy == "drop_high_missing_median":
        dropped_features = get_high_missing_features(
            X_train=X_train_raw,
            threshold=cfg.high_missing_threshold,
        )
        X_train_raw = X_train_raw.drop(columns=dropped_features)
        X_test_raw = X_test_raw.drop(columns=dropped_features)

    imputer = SimpleImputer(strategy="median")
    X_train_original = pd.DataFrame(
        imputer.fit_transform(X_train_raw),
        columns=X_train_raw.columns.tolist(),
        index=X_train_raw.index,
    )
    X_test_original = pd.DataFrame(
        imputer.transform(X_test_raw),
        columns=X_train_raw.columns.tolist(),
        index=X_test_raw.index,
    )

    X_train_structural = pd.DataFrame(index=train_inner_df.index)
    X_test_structural = pd.DataFrame(index=test_df.index)
    structural_feature_names: list[str] = []

    if candidate_strategy == "median_all_structural_all":
        builder = fit_structural_feature_builder(
            train_inner_df=train_inner_df,
            cfg=cfg,
            structural_config=structural_config,
            feature_group="median_all_structural_all",
        )
        X_train_structural = transform_structural_features(train_inner_df, builder)
        X_test_structural = transform_structural_features(test_df, builder)
        structural_feature_names = X_train_structural.columns.tolist()
    elif candidate_strategy not in {"baseline_median_all", "drop_high_missing_median"}:
        raise ValueError(f"Day16 不支持的候选策略：{candidate_strategy}")

    X_train = pd.concat([X_train_original, X_train_structural], axis=1)
    X_test = pd.concat([X_test_original, X_test_structural], axis=1)
    metadata = {
        "candidate_strategy": candidate_strategy,
        "fit_dataset": "train_inner",
        "selection_dataset": "valid",
        "evaluation_dataset": "official_test",
        "uses_official_test_for_selection": False,
        "threshold_source": "day15_valid_best_summary",
        "params_source": "day15_valid_best_summary",
        "n_original_features": X_train_original.shape[1],
        "n_structural_features": X_train_structural.shape[1],
        "n_total_features": X_train.shape[1],
        "n_dropped_features": len(dropped_features),
        "dropped_features": "|".join(dropped_features),
        "structural_feature_names": "|".join(structural_feature_names),
    }
    return X_train, X_test, y_train.copy(), y_test.copy(), metadata


def _prediction_frame(
    *,
    test_df: pd.DataFrame,
    y_true: pd.Series,
    y_proba: np.ndarray,
    threshold: float,
    candidate_strategy: str,
    trial_id: str,
    search_stage: str,
) -> pd.DataFrame:
    """整理 official test 预测明细。"""

    return pd.DataFrame(
        {
            "dataset": "official_test",
            "sample_id": test_df.index.to_numpy() + 1,
            "y_true": y_true.to_numpy(),
            "y_proba": y_proba,
            "y_pred": (y_proba >= threshold).astype(int),
            "model_name": "xgboost_tuned",
            "candidate_strategy": candidate_strategy,
            "threshold": threshold,
            "threshold_source": "day15_valid_best_summary",
            "trial_id": trial_id,
            "search_stage": search_stage,
        }
    )


def _valid_test_compare(
    day15_best_summary: pd.DataFrame,
    tuned_test_results: pd.DataFrame,
    candidate_strategies: list[str],
) -> pd.DataFrame:
    """对比 Day15 valid 最优结果和 Day16 official test 结果。"""

    strategy_col = _strategy_column(day15_best_summary)
    valid_cols = [
        strategy_col,
        "threshold",
        "precision",
        "recall",
        "f1",
        "f2",
        "average_precision",
        "fp",
        "fn",
        "total_cost",
        "trial_id",
        "search_stage",
    ]
    valid = day15_best_summary[day15_best_summary[strategy_col].isin(candidate_strategies)].copy()
    for column in valid_cols:
        if column not in valid.columns:
            valid[column] = np.nan
    valid = valid[valid_cols].copy()
    valid = valid.rename(
        columns={
            strategy_col: "candidate_strategy",
            "precision": "valid_precision",
            "recall": "valid_recall",
            "f1": "valid_f1",
            "f2": "valid_f2",
            "average_precision": "valid_average_precision",
            "fp": "valid_fp",
            "fn": "valid_fn",
            "total_cost": "valid_total_cost",
            "trial_id": "valid_trial_id",
            "search_stage": "valid_search_stage",
        }
    )

    test = tuned_test_results[
        [
            "candidate_strategy",
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

    compare = valid.merge(test, on=["candidate_strategy", "threshold"], how="left")
    compare["delta_total_cost_test_minus_valid"] = (
        compare["test_total_cost"] - compare["valid_total_cost"]
    )
    compare["delta_fn_test_minus_valid"] = compare["test_fn"] - compare["valid_fn"]
    compare["delta_fp_test_minus_valid"] = compare["test_fp"] - compare["valid_fp"]
    compare["delta_recall_test_minus_valid"] = (
        compare["test_recall"] - compare["valid_recall"]
    )
    compare["delta_f2_test_minus_valid"] = compare["test_f2"] - compare["valid_f2"]
    compare["note"] = "official test 只用于最终观察，不能反向修改 Day15 参数或阈值。"
    return compare.sort_values("test_total_cost").reset_index(drop=True)


def evaluate_tuned_xgb_candidates_on_test(
    train_inner_df: pd.DataFrame,
    valid_df: pd.DataFrame,
    test_df: pd.DataFrame,
    cfg: ScaniaConfig,
    structural_config: dict[str, Any],
    day15_best_summary: pd.DataFrame,
    candidate_strategies: Iterable[str],
) -> dict[str, pd.DataFrame]:
    """使用 Day15 valid 固定参数和阈值，在 official test 上评估 tuned candidates。"""

    _ = valid_df  # 保留参数以明确 Day16 接口边界：valid 只作为 Day15 选择来源。
    strategies = list(candidate_strategies)
    metric_rows: list[dict[str, Any]] = []
    prediction_frames: list[pd.DataFrame] = []
    metadata_rows: list[dict[str, Any]] = []

    for candidate_strategy in strategies:
        day15_row = _day15_row_for_strategy(day15_best_summary, candidate_strategy)
        params = _params_from_day15_row(day15_row)
        threshold = float(day15_row["threshold"])
        trial_id = str(day15_row.get("trial_id", ""))
        search_stage = str(day15_row.get("search_stage", ""))

        X_train, X_test, y_train, y_test, metadata = _prepare_train_test_feature_set(
            train_inner_df=train_inner_df,
            test_df=test_df,
            cfg=cfg,
            structural_config=structural_config,
            candidate_strategy=candidate_strategy,
        )
        model = _build_xgb_classifier(cfg, params)
        model.fit(X_train, y_train)
        y_proba = _positive_class_proba(model, X_test)
        y_pred = (y_proba >= threshold).astype(int)

        metric = evaluate_binary_classifier(
            y_true=y_test,
            y_pred=y_pred,
            y_proba=y_proba,
            cfg=cfg,
            model_name="xgboost_tuned",
            strategy=candidate_strategy,
            threshold=threshold,
        )
        metric.update(
            {
                "dataset": "official_test",
                "candidate_strategy": candidate_strategy,
                "trial_id": trial_id,
                "search_stage": search_stage,
                "selection_dataset": "valid",
                "evaluation_dataset": "official_test",
                "threshold_source": "day15_valid_best_summary",
                "params_source": "day15_valid_best_summary",
                "n_original_features": metadata["n_original_features"],
                "n_structural_features": metadata["n_structural_features"],
                "n_total_features": metadata["n_total_features"],
            }
        )
        metric_rows.append(metric)
        prediction_frames.append(
            _prediction_frame(
                test_df=test_df,
                y_true=y_test,
                y_proba=y_proba,
                threshold=threshold,
                candidate_strategy=candidate_strategy,
                trial_id=trial_id,
                search_stage=search_stage,
            )
        )
        metadata_rows.append(
            {
                **metadata,
                **{f"param_{name}": value for name, value in params.items()},
                "threshold": threshold,
                "trial_id": trial_id,
                "search_stage": search_stage,
                "train_inner_rows": len(train_inner_df),
                "valid_rows": len(valid_df),
                "official_test_rows": len(test_df),
            }
        )

    tuned_test_results = pd.DataFrame(metric_rows).sort_values(
        ["total_cost", "recall", "f2"],
        ascending=[True, False, False],
    ).reset_index(drop=True)
    tuned_test_predictions = pd.concat(prediction_frames, ignore_index=True)
    tuned_test_metadata = pd.DataFrame(metadata_rows)
    tuned_valid_test_compare = _valid_test_compare(
        day15_best_summary=day15_best_summary,
        tuned_test_results=tuned_test_results,
        candidate_strategies=strategies,
    )

    return {
        "tuned_test_results": tuned_test_results,
        "tuned_test_predictions": tuned_test_predictions,
        "tuned_valid_test_compare": tuned_valid_test_compare,
        "tuned_test_metadata": tuned_test_metadata,
    }
