"""Day 19 SQL 业务分析导出工具。

本模块只负责把已经完成的模型预测结果整理成可导入 MySQL 的 CSV。
不连接数据库，不重新训练模型，也不修改原始数据。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from scania_aps.config import ReleasePolicy
from scania_aps.evaluation.risk_utils import (
    assign_risk_level,
    assign_suggested_action,
    classify_prediction_type,
)

OFFICIAL_TEST_DATASET = "official_test"
OOF_DATASET = "oof_train"

PROBABILITY_BINS = [0.0, 0.05, 0.10, 0.20, 0.40, 0.60, 0.80, 1.000000001]
PROBABILITY_LABELS = [
    "[0.00,0.05)",
    "[0.05,0.10)",
    "[0.10,0.20)",
    "[0.20,0.40)",
    "[0.40,0.60)",
    "[0.60,0.80)",
    "[0.80,1.00]",
]


@dataclass(frozen=True)
class PolicyCosts:
    """业务误判成本配置。"""

    fp_cost: int
    fn_cost: int


def _first_existing_column(df: pd.DataFrame, candidates: list[str]) -> str:
    """返回候选列名中第一个存在的列。"""

    for column in candidates:
        if column in df.columns:
            return column
    raise ValueError(f"缺少必要字段，候选字段为：{candidates}")


def _select_final_candidate_predictions(
    predictions: pd.DataFrame,
    release_policy: ReleasePolicy,
) -> pd.DataFrame:
    """从 Day14 predictions 中筛选最终候选方案。"""

    required_columns = {
        "candidate_group",
        "dataset",
        "model_name",
        "sample_id",
        "strategy",
        "threshold",
        "threshold_source",
    }
    missing_columns = required_columns - set(predictions.columns)
    if missing_columns:
        raise ValueError(
            "Day14 predictions 缺少发布来源字段："
            f"{sorted(missing_columns)}。"
        )

    strategy_mask = predictions["candidate_group"].astype(str).eq(release_policy.strategy)
    threshold_mask = np.isclose(
        predictions["threshold"].astype(float),
        release_policy.decision_threshold,
        rtol=0.0,
        atol=1e-12,
    )
    selected = predictions[strategy_mask & threshold_mask].copy()

    if selected.empty:
        raise ValueError(
            "未能在 Day14 predictions 中找到与 release policy 精确匹配的候选："
            f"strategy={release_policy.strategy}, "
            f"threshold={release_policy.decision_threshold}。"
        )

    expected_provenance = {
        "model_name": release_policy.model_name,
        "dataset": release_policy.evaluation_dataset,
        "strategy": release_policy.strategy,
        "threshold_source": release_policy.threshold_source,
    }
    for field, expected_value in expected_provenance.items():
        invalid_values = selected.loc[
            selected[field].astype(str).ne(str(expected_value)),
            field,
        ]
        if not invalid_values.empty:
            actual_values = sorted(invalid_values.astype(str).unique().tolist())
            raise ValueError(
                f"Day14 predictions 的 {field} 与 release policy 不一致："
                f"expected={expected_value}, actual={actual_values}。"
            )

    if len(selected) != release_policy.evaluation_rows:
        raise ValueError(
            "Day14 predictions 最终候选行数与 release policy.evaluation_rows "
            "不一致："
            f"expected={release_policy.evaluation_rows}, actual={len(selected)}。"
        )

    if selected["sample_id"].isna().any():
        raise ValueError("Day14 predictions 的 sample_id 不得为空。")
    if selected["sample_id"].duplicated().any():
        duplicate_count = int(selected["sample_id"].duplicated(keep=False).sum())
        raise ValueError(
            "Day14 predictions 的 sample_id 必须唯一："
            f"duplicate_rows={duplicate_count}。"
        )

    return selected.reset_index(drop=True)


def calculate_sample_cost(
    confusion_type: pd.Series,
    fp_cost: int,
    fn_cost: int,
) -> pd.Series:
    """按单样本误判类型计算业务成本。"""

    return pd.Series(
        np.select(
            [confusion_type.eq("FP"), confusion_type.eq("FN")],
            [fp_cost, fn_cost],
            default=0,
        ),
        index=confusion_type.index,
    ).astype(int)


def assign_probability_band(y_proba: pd.Series) -> pd.Series:
    """按历史兼容字段 y_proba 生成固定风险分数区间标签。"""

    return pd.cut(
        pd.Series(y_proba, dtype="float64").clip(0, 1),
        bins=PROBABILITY_BINS,
        labels=PROBABILITY_LABELS,
        right=False,
        include_lowest=True,
    ).astype(str)


def assign_descending_decile(y_proba: pd.Series) -> pd.Series:
    """按风险分数从高到低生成 decile，1 表示最高风险 10%。"""

    proba = pd.Series(y_proba, dtype="float64")
    rank = proba.rank(method="first", ascending=False)
    decile = (((rank - 1) * 10 // len(proba)) + 1).astype(int)
    return decile.clip(lower=1, upper=10).astype(int)


def build_model_prediction_results(
    day14_predictions: pd.DataFrame,
    costs: PolicyCosts,
    release_policy: ReleasePolicy,
    created_at: str | None = None,
) -> pd.DataFrame:
    """构造统一预测结果表；y_proba 为历史兼容的未校准风险分数字段。"""

    selected = _select_final_candidate_predictions(
        day14_predictions,
        release_policy=release_policy,
    )

    y_true_col = _first_existing_column(selected, ["y_true"])
    y_proba_col = _first_existing_column(selected, ["y_proba", "proba", "probability"])
    sample_id_col = "sample_id" if "sample_id" in selected.columns else None
    result = pd.DataFrame()
    result["sample_id"] = (
        selected[sample_id_col].astype(int).to_numpy()
        if sample_id_col
        else np.arange(1, len(selected) + 1)
    )
    result["dataset"] = release_policy.evaluation_dataset
    result["model_version"] = release_policy.model_version
    result["strategy"] = release_policy.strategy
    result["threshold"] = float(release_policy.decision_threshold)
    result["y_true"] = selected[y_true_col].astype(int).to_numpy()
    result["y_proba"] = selected[y_proba_col].astype(float).to_numpy()
    result["y_pred"] = (
        result["y_proba"] >= release_policy.decision_threshold
    ).astype(int)
    result["risk_level"] = assign_risk_level(
        result["y_proba"],
        release_policy.decision_threshold,
    )
    result["suggested_action"] = assign_suggested_action(result["risk_level"])
    result["confusion_type"] = classify_prediction_type(
        result["y_true"],
        result["y_pred"],
    )
    result["fp_cost"] = int(costs.fp_cost)
    result["fn_cost"] = int(costs.fn_cost)
    result["sample_cost"] = calculate_sample_cost(
        result["confusion_type"],
        costs.fp_cost,
        costs.fn_cost,
    )
    result["probability_band"] = assign_probability_band(result["y_proba"])
    result["decile"] = assign_descending_decile(result["y_proba"])
    result["created_at"] = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return result.sort_values("sample_id").reset_index(drop=True)


def _safe_metric(row: pd.Series, column: str, default: Any = np.nan) -> Any:
    """安全读取指标行字段。"""

    return row[column] if column in row.index else default


def _policy_row_from_metrics(
    row: pd.Series,
    policy_name: str,
    dataset: str,
    baseline_total_cost: int,
    costs: PolicyCosts,
    source_file: str,
    note: str,
) -> dict[str, Any]:
    """从指标 CSV 的一行生成 policy comparison 记录。"""

    fp = int(_safe_metric(row, "fp", 0))
    fn = int(_safe_metric(row, "fn", 0))
    tp = int(_safe_metric(row, "tp", 0))
    tn = int(_safe_metric(row, "tn", 0))
    total_cost = int(_safe_metric(row, "total_cost", fp * costs.fp_cost + fn * costs.fn_cost))
    cost_reduction = baseline_total_cost - total_cost
    return {
        "policy_name": policy_name,
        "dataset": dataset,
        "threshold": float(_safe_metric(row, "threshold", np.nan)),
        "fp": fp,
        "fn": fn,
        "tp": tp,
        "tn": tn,
        "fp_cost": int(costs.fp_cost),
        "fn_cost": int(costs.fn_cost),
        "fp_cost_total": fp * costs.fp_cost,
        "fn_cost_total": fn * costs.fn_cost,
        "total_cost": total_cost,
        "baseline_total_cost": baseline_total_cost,
        "cost_reduction": cost_reduction,
        "cost_reduction_rate": cost_reduction / baseline_total_cost
        if baseline_total_cost
        else np.nan,
        "source_file": source_file,
        "note": note,
    }


def build_model_policy_comparison(
    prediction_results: pd.DataFrame,
    day14_metrics: pd.DataFrame,
    day16_metrics: pd.DataFrame | None,
    day18_oof_summary: pd.DataFrame | None,
    costs: PolicyCosts,
    release_policy: ReleasePolicy,
) -> pd.DataFrame:
    """构造策略级成本对比表。"""

    positive_count = int(prediction_results["y_true"].sum())
    official_baseline_cost = positive_count * costs.fn_cost
    rows: list[dict[str, Any]] = [
        {
            "policy_name": "naive_all_negative",
            "dataset": OFFICIAL_TEST_DATASET,
            "threshold": np.nan,
            "fp": 0,
            "fn": positive_count,
            "tp": 0,
            "tn": int((prediction_results["y_true"] == 0).sum()),
            "fp_cost": int(costs.fp_cost),
            "fn_cost": int(costs.fn_cost),
            "fp_cost_total": 0,
            "fn_cost_total": official_baseline_cost,
            "total_cost": official_baseline_cost,
            "baseline_total_cost": official_baseline_cost,
            "cost_reduction": 0,
            "cost_reduction_rate": 0.0,
            "source_file": "outputs/predictions/day14_structural_feature_test_predictions.csv",
            "note": "全预测为 neg 的 naive baseline，作为 official test 成本下降基准。",
        }
    ]

    if not day14_metrics.empty:
        required_metrics_columns = {
            "candidate_group",
            "dataset",
            "model_name",
            "strategy",
            "threshold",
            "threshold_source",
        }
        missing_metrics_columns = required_metrics_columns - set(day14_metrics.columns)
        if missing_metrics_columns:
            raise ValueError(
                "Day14 metrics 缺少发布来源字段："
                f"{sorted(missing_metrics_columns)}。"
            )

        baseline_rows = day14_metrics[
            day14_metrics.get("strategy", pd.Series(dtype=str))
            .astype(str)
            .eq("baseline_median_all")
        ]
        if not baseline_rows.empty:
            rows.append(
                _policy_row_from_metrics(
                    baseline_rows.iloc[0],
                    "day14_baseline_median_all",
                    OFFICIAL_TEST_DATASET,
                    official_baseline_cost,
                    costs,
                    "outputs/metrics/day14_structural_feature_test_results.csv",
                    "Day14 未调参 baseline_median_all official test 结果。",
                )
            )

        strategy_mask = (
            day14_metrics.get("strategy", pd.Series(index=day14_metrics.index, dtype=str))
            .astype(str)
            .eq(release_policy.strategy)
        )
        threshold_values = pd.to_numeric(
            day14_metrics.get(
                "threshold",
                pd.Series(index=day14_metrics.index, dtype=float),
            ),
            errors="coerce",
        )
        threshold_mask = np.isclose(
            threshold_values,
            release_policy.decision_threshold,
            rtol=0.0,
            atol=1e-12,
        )
        final_rows = day14_metrics[strategy_mask & threshold_mask]
    else:
        final_rows = day14_metrics

    if len(final_rows) != 1:
        raise ValueError(
            "Day14 metrics 中与 release policy 精确匹配的最终候选必须仅匹配一行："
            f"strategy={release_policy.strategy}, "
            f"threshold={release_policy.decision_threshold}，"
            f"matched_rows={len(final_rows)}。"
        )

    final_metrics = final_rows.iloc[0]
    expected_metrics_provenance = {
        "model_name": release_policy.model_name,
        "dataset": release_policy.evaluation_dataset,
        "candidate_group": release_policy.strategy,
        "threshold_source": release_policy.threshold_source,
    }
    for field, expected_value in expected_metrics_provenance.items():
        actual_value = str(final_metrics[field])
        if actual_value != str(expected_value):
            raise ValueError(
                f"Day14 metrics 的 {field} 与 release policy 不一致："
                f"expected={expected_value}, actual={actual_value}。"
            )

    rows.append(
        _policy_row_from_metrics(
            final_metrics,
            release_policy.model_version,
            OFFICIAL_TEST_DATASET,
            official_baseline_cost,
            costs,
            "outputs/metrics/day14_structural_feature_test_results.csv",
            "当前最终推荐候选，使用 Day13 valid 选择的 "
            f"threshold={release_policy.decision_threshold}。",
        )
    )

    if day16_metrics is not None and not day16_metrics.empty:
        best_day16 = day16_metrics.sort_values("total_cost", ascending=True).iloc[0]
        rows.append(
            _policy_row_from_metrics(
                best_day16,
                "day16_tuned_best",
                OFFICIAL_TEST_DATASET,
                official_baseline_cost,
                costs,
                "outputs/metrics/day16_xgb_tuning_test_results.csv",
                "Day15 tuned 参数在 Day16 official test 上的最低成本方案，用于说明调参未稳定泛化。",
            )
        )

    if day18_oof_summary is not None and not day18_oof_summary.empty:
        oof_cost_min = day18_oof_summary[
            day18_oof_summary.get("threshold_selection_rule", pd.Series(dtype=str))
            .astype(str)
            .eq("cost_min")
        ]
        if oof_cost_min.empty:
            oof_cost_min = day18_oof_summary
        best_oof = oof_cost_min.sort_values("total_cost", ascending=True).iloc[0]
        oof_positive_count = int(_safe_metric(best_oof, "tp", 0) + _safe_metric(best_oof, "fn", 0))
        oof_baseline_cost = oof_positive_count * costs.fn_cost
        rows.append(
            _policy_row_from_metrics(
                best_oof,
                "day18_oof_ensemble_best",
                OOF_DATASET,
                oof_baseline_cost,
                costs,
                "outputs/metrics/day18_oof_ensemble_best_summary.csv",
                "OOF train 内部口径结果，不可与 official test 成本直接横向比较。",
            )
        )

    return pd.DataFrame(rows)


def _binary_metrics_from_counts(tp: int, fp: int, tn: int, fn: int) -> dict[str, float]:
    """根据混淆矩阵计数计算基础分类指标。"""

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    beta2 = 4
    f2 = (
        (1 + beta2) * precision * recall / (beta2 * precision + recall)
        if (beta2 * precision + recall)
        else 0.0
    )
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "f2": f2,
    }


def build_threshold_sensitivity_results(
    prediction_results: pd.DataFrame,
    costs: PolicyCosts,
    thresholds: np.ndarray | None = None,
) -> pd.DataFrame:
    """基于最终候选风险分数生成阈值敏感性表。"""

    if thresholds is None:
        thresholds = np.round(np.arange(0.01, 1.00, 0.01), 2)

    y_true = prediction_results["y_true"].astype(int).to_numpy()
    y_proba = prediction_results["y_proba"].astype(float).to_numpy()
    rows = []

    for threshold in thresholds:
        y_pred = (y_proba >= float(threshold)).astype(int)
        tp = int(((y_true == 1) & (y_pred == 1)).sum())
        fp = int(((y_true == 0) & (y_pred == 1)).sum())
        tn = int(((y_true == 0) & (y_pred == 0)).sum())
        fn = int(((y_true == 1) & (y_pred == 0)).sum())
        metrics = _binary_metrics_from_counts(tp, fp, tn, fn)
        predicted_positive_count = int(y_pred.sum())
        total_cost = fp * costs.fp_cost + fn * costs.fn_cost
        rows.append(
            {
                "threshold": float(threshold),
                "predicted_positive_count": predicted_positive_count,
                "predicted_negative_count": int(len(y_pred) - predicted_positive_count),
                "tp": tp,
                "fp": fp,
                "tn": tn,
                "fn": fn,
                "precision_score": metrics["precision"],
                "recall_score": metrics["recall"],
                "f1_score": metrics["f1"],
                "f2_score": metrics["f2"],
                "fp_cost": int(costs.fp_cost),
                "fn_cost": int(costs.fn_cost),
                "total_cost": total_cost,
                "workload_rate": predicted_positive_count / len(y_pred)
                if len(y_pred)
                else 0.0,
            }
        )

    return pd.DataFrame(rows)


def build_export_manifest(
    exported_files: list[tuple[Path, str, str]],
) -> pd.DataFrame:
    """生成 SQL 导出文件清单。"""

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = []
    for path, description, target_table in exported_files:
        df = pd.read_csv(path)
        parts = path.parts
        relative_path = path.as_posix()
        if "outputs" in parts:
            output_index = parts.index("outputs")
            relative_path = Path(*parts[output_index:]).as_posix()
        rows.append(
            {
                "file_name": path.name,
                "relative_path": relative_path,
                "row_count": len(df),
                "column_count": len(df.columns),
                "description": description,
                "target_mysql_table": target_table,
                "generated_at": generated_at,
            }
        )
    return pd.DataFrame(rows)
