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


FINAL_MODEL_VERSION = "day14_structural_all_final_candidate"
FINAL_STRATEGY = "median_all_structural_all"
FINAL_THRESHOLD = 0.18
OFFICIAL_TEST_DATASET = "official_test"
OOF_DATASET = "oof_train"

RISK_ACTION_MAPPING = {
    "Critical": "immediate_inspection",
    "High": "priority_inspection",
    "Medium": "monitor_and_recheck",
    "Low": "no_action_now",
}

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
    final_strategy: str = FINAL_STRATEGY,
    final_threshold: float = FINAL_THRESHOLD,
) -> pd.DataFrame:
    """从 Day14 predictions 中筛选最终候选方案。"""

    strategy_col = _first_existing_column(
        predictions,
        ["candidate_group", "candidate_strategy", "strategy", "model_name"],
    )
    threshold_col = _first_existing_column(predictions, ["threshold"])

    strategy_mask = predictions[strategy_col].astype(str).str.contains(
        final_strategy,
        case=False,
        regex=False,
    )
    threshold_mask = np.isclose(
        predictions[threshold_col].astype(float),
        final_threshold,
        atol=1e-9,
    )
    selected = predictions[strategy_mask & threshold_mask].copy()

    if selected.empty:
        fallback_mask = predictions[strategy_col].astype(str).str.contains(
            "structural_all",
            case=False,
            regex=False,
        )
        selected = predictions[fallback_mask].copy()

    if selected.empty:
        raise ValueError("未能在 Day14 predictions 中找到 structural_all 最终候选方案。")

    return selected.reset_index(drop=True)


def assign_sql_export_risk_level(y_proba: pd.Series) -> pd.Series:
    """按 Day19 SQL 导出口径生成风险等级。"""

    proba = pd.Series(y_proba, dtype="float64")
    levels = np.select(
        [
            proba >= 0.80,
            (proba >= 0.20) & (proba < 0.80),
            (proba >= 0.05) & (proba < 0.20),
            proba < 0.05,
        ],
        ["Critical", "High", "Medium", "Low"],
        default="Unknown",
    )
    return pd.Series(levels, index=proba.index)


def classify_confusion_type(y_true: pd.Series, y_pred: pd.Series) -> pd.Series:
    """生成 TP / FP / TN / FN。"""

    true = pd.Series(y_true).astype(int)
    pred = pd.Series(y_pred).astype(int)
    labels = np.select(
        [
            (true == 1) & (pred == 1),
            (true == 0) & (pred == 1),
            (true == 0) & (pred == 0),
            (true == 1) & (pred == 0),
        ],
        ["TP", "FP", "TN", "FN"],
        default="Unknown",
    )
    return pd.Series(labels, index=true.index)


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
    """生成固定概率区间标签，便于 SQL 错误分析。"""

    return pd.cut(
        pd.Series(y_proba, dtype="float64").clip(0, 1),
        bins=PROBABILITY_BINS,
        labels=PROBABILITY_LABELS,
        right=False,
        include_lowest=True,
    ).astype(str)


def assign_descending_decile(y_proba: pd.Series) -> pd.Series:
    """按预测概率从高到低生成 decile，1 表示最高风险 10%。"""

    proba = pd.Series(y_proba, dtype="float64")
    rank = proba.rank(method="first", ascending=False)
    decile = (((rank - 1) * 10 // len(proba)) + 1).astype(int)
    return decile.clip(lower=1, upper=10).astype(int)


def build_model_prediction_results(
    day14_predictions: pd.DataFrame,
    costs: PolicyCosts,
    final_strategy: str = FINAL_STRATEGY,
    final_threshold: float = FINAL_THRESHOLD,
    created_at: str | None = None,
) -> pd.DataFrame:
    """构造可导入 MySQL 的统一预测结果表。"""

    selected = _select_final_candidate_predictions(
        day14_predictions,
        final_strategy=final_strategy,
        final_threshold=final_threshold,
    )

    y_true_col = _first_existing_column(selected, ["y_true"])
    y_proba_col = _first_existing_column(selected, ["y_proba", "proba", "probability"])
    sample_id_col = "sample_id" if "sample_id" in selected.columns else None
    strategy_col = _first_existing_column(
        selected,
        ["strategy", "candidate_group", "candidate_strategy", "model_name"],
    )

    result = pd.DataFrame()
    result["sample_id"] = (
        selected[sample_id_col].astype(int).to_numpy()
        if sample_id_col
        else np.arange(1, len(selected) + 1)
    )
    result["dataset"] = OFFICIAL_TEST_DATASET
    result["model_version"] = FINAL_MODEL_VERSION
    result["strategy"] = selected[strategy_col].astype(str).to_numpy()
    result["threshold"] = float(final_threshold)
    result["y_true"] = selected[y_true_col].astype(int).to_numpy()
    result["y_proba"] = selected[y_proba_col].astype(float).to_numpy()
    result["y_pred"] = (result["y_proba"] >= final_threshold).astype(int)
    result["risk_level"] = assign_sql_export_risk_level(result["y_proba"])
    result["suggested_action"] = result["risk_level"].map(RISK_ACTION_MAPPING)
    result["confusion_type"] = classify_confusion_type(result["y_true"], result["y_pred"])
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

        final_rows = day14_metrics[
            day14_metrics.get("strategy", pd.Series(dtype=str))
            .astype(str)
            .eq(FINAL_STRATEGY)
        ]
        if not final_rows.empty:
            rows.append(
                _policy_row_from_metrics(
                    final_rows.iloc[0],
                    "day14_structural_all_final_candidate",
                    OFFICIAL_TEST_DATASET,
                    official_baseline_cost,
                    costs,
                    "outputs/metrics/day14_structural_feature_test_results.csv",
                    "当前最终推荐候选，使用 Day13 valid 选择的 threshold=0.18。",
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
    """基于最终候选概率生成阈值敏感性表。"""

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
