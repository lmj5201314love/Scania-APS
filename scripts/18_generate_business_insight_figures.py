"""Day 20: generate SQL business insight tables, figures, and report.

This script only reads Day19 CSV exports under outputs/sql_exports. It does not
connect to MySQL, retrain models, modify raw data, or select a new final
threshold.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from scania_aps.config import ReleasePolicy, get_config
from scania_aps.evaluation.risk_utils import RISK_LEVEL_ORDER

TOP_K_VALUES = [50, 100, 200, 500, 1000]
RISK_ORDER = {
    risk_level: priority
    for priority, risk_level in enumerate(RISK_LEVEL_ORDER, start=1)
}
CONFUSION_ORDER = {"TP": 1, "FP": 2, "FN": 3, "TN": 4}


def _official_policy_order(release_policy: ReleasePolicy) -> dict[str, int]:
    return {
        "naive_all_negative": 1,
        "day14_baseline_median_all": 2,
        release_policy.model_version: 3,
        "day16_tuned_best": 4,
    }


@dataclass(frozen=True)
class Day20Paths:
    sql_export_dir: Path
    final_figure_dir: Path
    final_table_dir: Path
    report_path: Path


def _safe_divide(numerator: float, denominator: float) -> float:
    return float(numerator / denominator) if denominator else 0.0


def _format_pct(value: float) -> str:
    return f"{value:.2%}"


def _format_float(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}"


def _require_columns(df: pd.DataFrame, required: Iterable[str], table_name: str) -> None:
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"{table_name} is missing required columns: {missing}")


def _first_existing_column(
    df: pd.DataFrame,
    candidates: list[str],
    table_name: str,
    canonical_name: str,
) -> str:
    for candidate in candidates:
        if candidate in df.columns:
            if candidate != canonical_name:
                print(
                    f"[INFO] {table_name}: using '{candidate}' as '{canonical_name}' "
                    "for compatibility."
                )
            return candidate
    raise ValueError(
        f"{table_name} is missing one of {candidates} required for {canonical_name}."
    )


def _official_predictions(predictions: pd.DataFrame) -> pd.DataFrame:
    _require_columns(
        predictions,
        [
            "sample_id",
            "dataset",
            "y_true",
            "y_proba",
            "y_pred",
            "risk_level",
            "suggested_action",
            "confusion_type",
            "sample_cost",
            "probability_band",
        ],
        "model_prediction_results",
    )
    official = predictions.loc[predictions["dataset"] == "official_test"].copy()
    if official.empty:
        raise ValueError("model_prediction_results has no official_test rows.")
    for column in ["y_true", "y_pred", "y_proba", "sample_cost"]:
        official[column] = pd.to_numeric(official[column], errors="coerce")
    return official


def build_topk_maintenance_capacity(
    predictions: pd.DataFrame,
    fn_cost: int,
    top_k_values: Iterable[int] = TOP_K_VALUES,
) -> pd.DataFrame:
    official = _official_predictions(predictions)
    total_pos_count = int(official["y_true"].sum())
    ranked = official.sort_values(
        ["y_proba", "sample_id"],
        ascending=[False, True],
    ).reset_index(drop=True)

    rows: list[dict[str, float | int]] = []
    for top_k in top_k_values:
        inspected = ranked.head(min(int(top_k), len(ranked)))
        inspected_count = int(len(inspected))
        actual_pos_count = int(inspected["y_true"].sum())
        rows.append(
            {
                "top_k": int(top_k),
                "inspected_count": inspected_count,
                "actual_pos_count": actual_pos_count,
                "total_pos_count": total_pos_count,
                "precision_at_k": _safe_divide(actual_pos_count, inspected_count),
                "recall_at_k": _safe_divide(actual_pos_count, total_pos_count),
                "missed_pos_count": total_pos_count - actual_pos_count,
                "estimated_workload": inspected_count,
                "estimated_avoided_fn_cost": actual_pos_count * int(fn_cost),
            }
        )
    return pd.DataFrame(rows)


def build_risk_workload_summary(predictions: pd.DataFrame) -> pd.DataFrame:
    official = _official_predictions(predictions)
    grouped = (
        official.groupby(["risk_level", "suggested_action"], dropna=False)
        .agg(
            tier_population=("sample_id", "count"),
            actual_pos_count=("y_true", "sum"),
            predicted_pos_count=("y_pred", "sum"),
            avg_risk_score=("y_proba", "mean"),
        )
        .reset_index()
    )
    confusion_counts = (
        official.assign(_count=1)
        .pivot_table(
            index=["risk_level", "suggested_action"],
            columns="confusion_type",
            values="_count",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
    )
    for confusion_type in ["TP", "FP", "FN"]:
        if confusion_type not in confusion_counts.columns:
            confusion_counts[confusion_type] = 0

    result = grouped.merge(
        confusion_counts[
            ["risk_level", "suggested_action", "TP", "FP", "FN"]
        ],
        on=["risk_level", "suggested_action"],
        how="left",
    )
    result["actual_pos_rate"] = result.apply(
        lambda row: _safe_divide(row["actual_pos_count"], row["tier_population"]),
        axis=1,
    )
    result["predicted_pos_rate"] = result.apply(
        lambda row: _safe_divide(row["predicted_pos_count"], row["tier_population"]),
        axis=1,
    )
    result["tp_count"] = result["TP"].astype(int)
    result["fp_count"] = result["FP"].astype(int)
    result["fn_count"] = result["FN"].astype(int)
    inspection_tiers = result["risk_level"].isin(["Critical", "High"])
    result["aps_inspection_queue_count"] = result["predicted_pos_count"].where(
        inspection_tiers,
        0,
    ).astype(int)
    result["recheck_queue_count"] = result["tier_population"].where(
        result["risk_level"].eq("Medium"),
        0,
    ).astype(int)
    result["priority_order"] = (
        result["risk_level"].map(RISK_ORDER).fillna(99).astype(int)
    )
    columns = [
        "risk_level",
        "suggested_action",
        "tier_population",
        "actual_pos_count",
        "predicted_pos_count",
        "actual_pos_rate",
        "predicted_pos_rate",
        "avg_risk_score",
        "tp_count",
        "fp_count",
        "fn_count",
        "aps_inspection_queue_count",
        "recheck_queue_count",
        "priority_order",
    ]
    return result[columns].sort_values(["priority_order", "suggested_action"])


def build_error_breakdown_summary(predictions: pd.DataFrame) -> pd.DataFrame:
    official = _official_predictions(predictions)

    summary = (
        official.groupby("confusion_type", dropna=False)
        .agg(
            sample_count=("sample_id", "count"),
            avg_probability=("y_proba", "mean"),
            total_sample_cost=("sample_cost", "sum"),
        )
        .reset_index()
    )
    summary["analysis_section"] = "confusion_type_summary"
    summary["risk_level"] = ""
    summary["probability_band"] = ""

    by_risk = (
        official.groupby(["confusion_type", "risk_level"], dropna=False)
        .agg(
            sample_count=("sample_id", "count"),
            avg_probability=("y_proba", "mean"),
            total_sample_cost=("sample_cost", "sum"),
        )
        .reset_index()
    )
    by_risk["analysis_section"] = "confusion_type_by_risk_level"
    by_risk["probability_band"] = ""

    by_band = (
        official.groupby(["confusion_type", "probability_band"], dropna=False)
        .agg(
            sample_count=("sample_id", "count"),
            avg_probability=("y_proba", "mean"),
            total_sample_cost=("sample_cost", "sum"),
        )
        .reset_index()
    )
    by_band["analysis_section"] = "confusion_type_by_probability_band"
    by_band["risk_level"] = ""

    result = pd.concat([summary, by_risk, by_band], ignore_index=True, sort=False)
    result["confusion_order"] = (
        result["confusion_type"].map(CONFUSION_ORDER).fillna(99).astype(int)
    )
    result["risk_order"] = result["risk_level"].map(RISK_ORDER).fillna(99).astype(int)
    result = result.sort_values(
        ["analysis_section", "confusion_order", "risk_order", "probability_band"]
    )
    return result[
        [
            "analysis_section",
            "confusion_type",
            "risk_level",
            "probability_band",
            "sample_count",
            "avg_probability",
            "total_sample_cost",
        ]
    ]


def build_decile_lift_gain_summary(predictions: pd.DataFrame) -> pd.DataFrame:
    official = _official_predictions(predictions)
    if "decile" not in official.columns:
        print("[INFO] model_prediction_results: decile missing; recomputing by y_proba.")
        ranked = official.sort_values(["y_proba", "sample_id"], ascending=[False, True])
        official = ranked.copy()
        official["decile"] = pd.qcut(
            range(len(official)),
            q=10,
            labels=range(1, 11),
        ).astype(int)

    official["decile"] = pd.to_numeric(official["decile"], errors="coerce").astype(int)
    total_pos = int(official["y_true"].sum())
    total_samples = int(len(official))
    overall_pos_rate = _safe_divide(total_pos, total_samples)
    grouped = (
        official.groupby("decile", dropna=False)
        .agg(sample_count=("sample_id", "count"), actual_pos_count=("y_true", "sum"))
        .reset_index()
        .sort_values("decile")
    )
    grouped["pos_rate"] = grouped.apply(
        lambda row: _safe_divide(row["actual_pos_count"], row["sample_count"]),
        axis=1,
    )
    grouped["cumulative_sample_count"] = grouped["sample_count"].cumsum()
    grouped["cumulative_pos_count"] = grouped["actual_pos_count"].cumsum()
    grouped["cumulative_recall"] = grouped["cumulative_pos_count"].apply(
        lambda value: _safe_divide(value, total_pos)
    )
    grouped["overall_pos_rate"] = overall_pos_rate
    grouped["lift"] = grouped["pos_rate"].apply(
        lambda value: _safe_divide(value, overall_pos_rate)
    )
    return grouped[
        [
            "decile",
            "sample_count",
            "actual_pos_count",
            "pos_rate",
            "cumulative_sample_count",
            "cumulative_pos_count",
            "cumulative_recall",
            "overall_pos_rate",
            "lift",
        ]
    ]


def build_threshold_sensitivity_summary(thresholds: pd.DataFrame) -> pd.DataFrame:
    _require_columns(
        thresholds,
        ["threshold", "predicted_positive_count", "workload_rate", "fp", "fn", "total_cost"],
        "threshold_sensitivity_results",
    )
    precision_col = _first_existing_column(
        thresholds,
        ["precision", "precision_score"],
        "threshold_sensitivity_results",
        "precision",
    )
    recall_col = _first_existing_column(
        thresholds,
        ["recall", "recall_score"],
        "threshold_sensitivity_results",
        "recall",
    )
    f2_col = _first_existing_column(
        thresholds,
        ["f2", "f2_score"],
        "threshold_sensitivity_results",
        "f2",
    )
    result = thresholds[
        [
            "threshold",
            "predicted_positive_count",
            "workload_rate",
            "fp",
            "fn",
            precision_col,
            recall_col,
            f2_col,
            "total_cost",
        ]
    ].copy()
    result = result.rename(
        columns={precision_col: "precision", recall_col: "recall", f2_col: "f2"}
    )
    return result.sort_values("threshold").reset_index(drop=True)


def _best_row(frame: pd.DataFrame, note: str) -> dict[str, object] | None:
    if frame.empty:
        return None
    sorted_frame = frame.sort_values(
        ["total_cost", "fn", "recall", "threshold"],
        ascending=[True, True, False, True],
    )
    row = sorted_frame.iloc[0].to_dict()
    row["note"] = note
    return row


def build_threshold_policy_highlights(
    threshold_summary: pd.DataFrame,
    final_threshold: float,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    threshold_values = pd.to_numeric(threshold_summary["threshold"], errors="coerce")
    final_rows = threshold_summary.loc[threshold_values.eq(float(final_threshold))]
    if len(final_rows) != 1:
        raise ValueError(
            "final_threshold 必须在 threshold sensitivity table 中精确匹配且仅匹配一行："
            f"final_threshold={final_threshold}，matched_rows={len(final_rows)}。"
        )

    record = final_rows.iloc[0].to_dict()
    record["policy_rule"] = "final_threshold"
    record["note"] = (
        "Current Day14 final threshold. Sensitivity table is not used to change it."
    )
    rows.append(record)

    rules = [
        (
            "min_cost_threshold",
            threshold_summary,
            "Minimum total cost in the threshold sensitivity curve.",
        ),
        (
            "min_cost_with_recall_ge_096",
            threshold_summary.loc[threshold_summary["recall"] >= 0.96],
            "Minimum cost while keeping recall >= 0.96.",
        ),
        (
            "min_cost_with_recall_ge_097",
            threshold_summary.loc[threshold_summary["recall"] >= 0.97],
            "Minimum cost while keeping recall >= 0.97.",
        ),
        (
            "min_cost_with_fn_le_15",
            threshold_summary.loc[threshold_summary["fn"] <= 15],
            "Minimum cost while keeping FN <= 15.",
        ),
        (
            "min_cost_with_fn_le_12",
            threshold_summary.loc[threshold_summary["fn"] <= 12],
            "Minimum cost while keeping FN <= 12, if feasible.",
        ),
    ]
    for policy_rule, frame, note in rules:
        record = _best_row(frame, note)
        if record is None:
            continue
        record["policy_rule"] = policy_rule
        rows.append(record)

    if rows:
        final_cost = float(rows[0]["total_cost"])
        near_final = threshold_summary.loc[threshold_summary["total_cost"] <= final_cost * 1.10]
        if not near_final.empty:
            workload_row = near_final.sort_values(
                ["predicted_positive_count", "total_cost", "fn"],
                ascending=[True, True, True],
            ).iloc[0]
            record = workload_row.to_dict()
            record["policy_rule"] = "min_workload_under_cost_near_final"
            record["note"] = (
                "Lowest workload among thresholds with total cost within 10% of "
                "the current final threshold; diagnostic only."
            )
            rows.append(record)

    result = pd.DataFrame(rows)
    return result[
        [
            "policy_rule",
            "threshold",
            "predicted_positive_count",
            "workload_rate",
            "fp",
            "fn",
            "precision",
            "recall",
            "f2",
            "total_cost",
            "note",
        ]
    ]


def build_policy_cost_comparison(
    policies: pd.DataFrame,
    release_policy: ReleasePolicy,
) -> pd.DataFrame:
    _require_columns(
        policies,
        [
            "policy_name",
            "dataset",
            "threshold",
            "fp",
            "fn",
            "fp_cost_total",
            "fn_cost_total",
            "total_cost",
            "cost_reduction",
            "cost_reduction_rate",
            "note",
        ],
        "model_policy_comparison",
    )
    result = policies.copy()
    result["note"] = result["note"].fillna("")
    oof_mask = result["dataset"].eq("oof_train")
    result.loc[oof_mask, "note"] = result.loc[oof_mask, "note"].apply(
        lambda value: (
            value
            if "不可与 official test" in value or "not comparable" in value
            else f"{value} OOF train 口径，不可与 official test 直接横向比较。"
        )
    )
    result["_dataset_order"] = result["dataset"].map({"official_test": 1, "oof_train": 2}).fillna(9)
    result["_policy_order"] = (
        result["policy_name"].map(_official_policy_order(release_policy)).fillna(99)
    )
    result = result.sort_values(["_dataset_order", "_policy_order", "policy_name"]).reset_index(drop=True)
    return result[
        [
            "policy_name",
            "dataset",
            "threshold",
            "fp",
            "fn",
            "fp_cost_total",
            "fn_cost_total",
            "total_cost",
            "cost_reduction",
            "cost_reduction_rate",
            "note",
        ]
    ]


def build_all_tables(
    predictions: pd.DataFrame,
    policies: pd.DataFrame,
    thresholds: pd.DataFrame,
    fp_cost: int,
    fn_cost: int,
    release_policy: ReleasePolicy,
) -> dict[str, pd.DataFrame]:
    del fp_cost
    threshold_summary = build_threshold_sensitivity_summary(thresholds)
    return {
        "final_topk_maintenance_capacity": build_topk_maintenance_capacity(
            predictions,
            fn_cost=fn_cost,
        ),
        "final_risk_workload_summary": build_risk_workload_summary(predictions),
        "final_error_breakdown_summary": build_error_breakdown_summary(predictions),
        "final_decile_lift_gain_summary": build_decile_lift_gain_summary(predictions),
        "final_threshold_sensitivity_summary": threshold_summary,
        "final_threshold_policy_highlights": build_threshold_policy_highlights(
            threshold_summary,
            final_threshold=release_policy.decision_threshold,
        ),
        "final_policy_cost_comparison": build_policy_cost_comparison(
            policies,
            release_policy=release_policy,
        ),
    }


def save_tables(tables: dict[str, pd.DataFrame], output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    for name, table in tables.items():
        path = output_dir / f"{name}.csv"
        table.to_csv(path, index=False, encoding="utf-8-sig")
        paths[name] = path
        print(f"[TABLE] {path} shape={table.shape}")
    return paths


def _save_current_figure(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=180, bbox_inches="tight")
    plt.close()
    print(f"[FIGURE] {path}")


def plot_cost_policy_comparison(
    policy_table: pd.DataFrame,
    output_dir: Path,
    release_policy: ReleasePolicy,
) -> Path:
    official = policy_table.loc[policy_table["dataset"] == "official_test"].copy()
    official["_policy_order"] = (
        official["policy_name"].map(_official_policy_order(release_policy)).fillna(99)
    )
    official = official.sort_values("_policy_order")
    labels = official["policy_name"].str.replace("_", "\n")

    plt.figure(figsize=(9, 5))
    bars = plt.bar(labels, official["total_cost"], color=["#8c8c8c", "#4c78a8", "#2f855a", "#d97706"])
    plt.ylabel("Total cost")
    plt.title("Official Test Cost by Policy")
    plt.grid(axis="y", alpha=0.25)
    plt.xticks(rotation=0, ha="center", fontsize=8)
    for bar, cost in zip(bars, official["total_cost"]):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{int(cost):,}",
            ha="center",
            va="bottom",
            fontsize=8,
        )
    path = output_dir / "final_cost_policy_comparison.png"
    _save_current_figure(path)
    return path


def plot_topk_capacity(topk: pd.DataFrame, output_dir: Path) -> Path:
    plt.figure(figsize=(8, 5))
    plt.plot(topk["top_k"], topk["recall_at_k"], marker="o", color="#2f855a")
    for _, row in topk.iterrows():
        plt.text(row["top_k"], row["recall_at_k"], f"{int(row['actual_pos_count'])}", fontsize=8)
    plt.xlabel("Top-K maintenance capacity")
    plt.ylabel("Recall at K")
    plt.title("Top-K Maintenance Capacity vs APS Fault Coverage")
    plt.ylim(0, 1.05)
    plt.grid(alpha=0.25)
    path = output_dir / "final_topk_maintenance_capacity.png"
    _save_current_figure(path)
    return path


def plot_risk_level_workload(risk_summary: pd.DataFrame, output_dir: Path) -> Path:
    risk = risk_summary.sort_values("priority_order")
    x = range(len(risk))
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.bar(
        x,
        risk["tier_population"],
        color="#4c78a8",
        alpha=0.85,
        label="Tier population",
    )
    ax1.set_ylabel("Tier population")
    ax1.set_xlabel("Risk level")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(risk["risk_level"])
    ax1.grid(axis="y", alpha=0.25)

    ax2 = ax1.twinx()
    ax2.plot(x, risk["actual_pos_rate"], color="#c2410c", marker="o", label="Actual pos rate")
    ax2.set_ylabel("Actual APS fault rate")
    ax2.set_ylim(0, max(1.0, float(risk["actual_pos_rate"].max()) * 1.15))

    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc="upper right")
    plt.title("Risk Tier Population and Actual APS Fault Rate")
    path = output_dir / "final_risk_level_workload.png"
    _save_current_figure(path)
    return path


def plot_decile_lift_gain(decile: pd.DataFrame, output_dir: Path) -> Path:
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.bar(decile["decile"], decile["lift"], color="#2f855a", alpha=0.85, label="Lift")
    ax1.axhline(1.0, color="#4b5563", linewidth=1, linestyle="--")
    ax1.set_xlabel("Decile (1 = highest risk)")
    ax1.set_ylabel("Lift")
    ax1.set_xticks(decile["decile"])
    ax1.grid(axis="y", alpha=0.25)

    ax2 = ax1.twinx()
    ax2.plot(
        decile["decile"],
        decile["cumulative_recall"],
        color="#d97706",
        marker="o",
        label="Cumulative recall",
    )
    ax2.set_ylabel("Cumulative recall")
    ax2.set_ylim(0, 1.05)

    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc="upper right")
    plt.title("Decile Lift and Gain")
    path = output_dir / "final_decile_lift_gain.png"
    _save_current_figure(path)
    return path


def plot_threshold_sensitivity(
    threshold_summary: pd.DataFrame,
    output_dir: Path,
    final_threshold: float,
) -> list[Path]:
    paths: list[Path] = []
    plt.figure(figsize=(8, 5))
    plt.plot(
        threshold_summary["threshold"],
        threshold_summary["total_cost"],
        color="#4c78a8",
        linewidth=2,
    )
    plt.axvline(
        final_threshold,
        color="#c2410c",
        linestyle="--",
        label=f"Final threshold = {final_threshold:.2f}",
    )
    plt.xlabel("Threshold")
    plt.ylabel("Total cost")
    plt.title("Threshold Sensitivity: Total Cost")
    plt.legend()
    plt.grid(alpha=0.25)
    path = output_dir / "final_threshold_sensitivity.png"
    _save_current_figure(path)
    paths.append(path)

    plt.figure(figsize=(8, 5))
    plt.plot(threshold_summary["threshold"], threshold_summary["fn"], color="#c2410c")
    plt.axvline(
        final_threshold,
        color="#4b5563",
        linestyle="--",
        label=f"Final threshold = {final_threshold:.2f}",
    )
    plt.xlabel("Threshold")
    plt.ylabel("False negatives")
    plt.title("Threshold Sensitivity: FN Curve")
    plt.legend()
    plt.grid(alpha=0.25)
    path = output_dir / "final_threshold_fn_curve.png"
    _save_current_figure(path)
    paths.append(path)

    plt.figure(figsize=(8, 5))
    plt.plot(
        threshold_summary["threshold"],
        threshold_summary["workload_rate"],
        color="#2f855a",
    )
    plt.axvline(
        final_threshold,
        color="#4b5563",
        linestyle="--",
        label=f"Final threshold = {final_threshold:.2f}",
    )
    plt.xlabel("Threshold")
    plt.ylabel("Predicted positive workload rate")
    plt.title("Threshold Sensitivity: Workload Curve")
    plt.legend()
    plt.grid(alpha=0.25)
    path = output_dir / "final_threshold_workload_curve.png"
    _save_current_figure(path)
    paths.append(path)
    return paths


def plot_confusion_error_breakdown(error_table: pd.DataFrame, output_dir: Path) -> Path:
    summary = error_table.loc[
        error_table["analysis_section"] == "confusion_type_summary"
    ].copy()
    summary["_order"] = summary["confusion_type"].map(CONFUSION_ORDER).fillna(99)
    summary = summary.sort_values("_order")
    plt.figure(figsize=(7, 5))
    bars = plt.bar(summary["confusion_type"], summary["sample_count"], color="#4c78a8")
    plt.ylabel("Sample count")
    plt.title("Confusion Error Breakdown")
    plt.grid(axis="y", alpha=0.25)
    for bar, count in zip(bars, summary["sample_count"]):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{int(count):,}",
            ha="center",
            va="bottom",
            fontsize=8,
        )
    path = output_dir / "final_confusion_error_breakdown.png"
    _save_current_figure(path)
    return path


def save_figures(
    tables: dict[str, pd.DataFrame],
    output_dir: Path,
    release_policy: ReleasePolicy,
) -> dict[str, Path | list[Path]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    return {
        "cost_policy": plot_cost_policy_comparison(
            tables["final_policy_cost_comparison"],
            output_dir,
            release_policy=release_policy,
        ),
        "topk": plot_topk_capacity(tables["final_topk_maintenance_capacity"], output_dir),
        "risk_level": plot_risk_level_workload(
            tables["final_risk_workload_summary"],
            output_dir,
        ),
        "decile": plot_decile_lift_gain(
            tables["final_decile_lift_gain_summary"],
            output_dir,
        ),
        "threshold": plot_threshold_sensitivity(
            tables["final_threshold_sensitivity_summary"],
            output_dir,
            final_threshold=release_policy.decision_threshold,
        ),
        "confusion": plot_confusion_error_breakdown(
            tables["final_error_breakdown_summary"],
            output_dir,
        ),
    }


def _policy_row(policy_table: pd.DataFrame, policy_name: str) -> pd.Series:
    rows = policy_table.loc[policy_table["policy_name"] == policy_name]
    if rows.empty:
        raise ValueError(f"Missing policy row: {policy_name}")
    return rows.iloc[0]


def _highlight_row(highlights: pd.DataFrame, policy_rule: str) -> pd.Series | None:
    rows = highlights.loc[highlights["policy_rule"] == policy_rule]
    return None if rows.empty else rows.iloc[0]


def build_markdown_report(
    tables: dict[str, pd.DataFrame],
    release_policy: ReleasePolicy,
) -> str:
    topk = tables["final_topk_maintenance_capacity"]
    risk = tables["final_risk_workload_summary"]
    policy = tables["final_policy_cost_comparison"]
    decile = tables["final_decile_lift_gain_summary"]
    threshold = tables["final_threshold_policy_highlights"]
    errors = tables["final_error_breakdown_summary"]

    final = _policy_row(policy, release_policy.model_version)
    naive = _policy_row(policy, "naive_all_negative")
    baseline = _policy_row(policy, "day14_baseline_median_all")
    tuned = _policy_row(policy, "day16_tuned_best")

    decile_1 = decile.loc[decile["decile"] == 1].iloc[0]
    decile_2 = decile.loc[decile["decile"] == 2].iloc[0]
    decile_3 = decile.loc[decile["decile"] == 3].iloc[0]

    final_threshold_row = _highlight_row(threshold, "final_threshold")
    min_cost = _highlight_row(threshold, "min_cost_threshold")
    recall_096 = _highlight_row(threshold, "min_cost_with_recall_ge_096")
    recall_097 = _highlight_row(threshold, "min_cost_with_recall_ge_097")
    fn_15 = _highlight_row(threshold, "min_cost_with_fn_le_15")
    fn_12 = _highlight_row(threshold, "min_cost_with_fn_le_12")

    error_summary = errors.loc[errors["analysis_section"] == "confusion_type_summary"]
    confusion_counts = {
        row["confusion_type"]: int(row["sample_count"]) for _, row in error_summary.iterrows()
    }
    fn_by_risk = errors.loc[
        (errors["analysis_section"] == "confusion_type_by_risk_level")
        & (errors["confusion_type"] == "FN")
    ]
    fp_by_risk = errors.loc[
        (errors["analysis_section"] == "confusion_type_by_risk_level")
        & (errors["confusion_type"] == "FP")
    ]
    fn_risk_text = ", ".join(
        f"{row.risk_level}: {int(row.sample_count)}" for row in fn_by_risk.itertuples()
    )
    fp_risk_text = ", ".join(
        f"{row.risk_level}: {int(row.sample_count)}" for row in fp_by_risk.itertuples()
    )

    topk_lines = []
    for row in topk.itertuples():
        topk_lines.append(
            f"- Top {int(row.top_k)}: hit {int(row.actual_pos_count)} positives, "
            f"recall@K = {_format_pct(row.recall_at_k)}, "
            f"precision@K = {_format_pct(row.precision_at_k)}."
        )

    risk_lines = []
    for row in risk.itertuples():
        risk_lines.append(
            f"- {row.risk_level}: tier_population={int(row.tier_population)}, "
            f"{int(row.actual_pos_count)} positives, "
            f"actual_pos_rate = {_format_pct(row.actual_pos_rate)}, "
            f"APS inspection queue={int(row.aps_inspection_queue_count)}, "
            f"recheck queue={int(row.recheck_queue_count)}, "
            f"suggested_action = `{row.suggested_action}`."
        )

    def threshold_line(label: str, row: pd.Series | None) -> str:
        if row is None:
            return f"- {label}: no feasible threshold in the sensitivity grid."
        return (
            f"- {label}: threshold={row['threshold']:.2f}, "
            f"workload={int(row['predicted_positive_count'])} "
            f"({_format_pct(row['workload_rate'])}), "
            f"FP={int(row['fp'])}, FN={int(row['fn'])}, "
            f"recall={_format_pct(row['recall'])}, total_cost={int(row['total_cost'])}."
        )

    return "\n".join(
        [
            "# SQL Business Insights for Scania APS Predictive Maintenance",
            "",
            "本报告由 `scripts/18_generate_business_insight_figures.py` 基于 Day19 `outputs/sql_exports/` CSV 生成。"
            "本轮不连接 MySQL、不重新训练模型、不重新选择阈值，也不修改 `data/raw/`。",
            "",
            "## 1. 当前最终候选方案",
            "",
            f"当前最终候选使用模型 `{release_policy.model_name}` 与策略 "
            f"`{release_policy.strategy}`，"
            f"阈值来源为 `{release_policy.threshold_source}`，"
            f"threshold={release_policy.decision_threshold:.2f}，"
            "并只在 official test 上做最终观察。",
            "",
            f"- model_version: `{release_policy.model_version}`",
            f"- threshold: {final['threshold']:.2f}",
            f"- TP / FP / TN / FN: {confusion_counts.get('TP', 0)} / {confusion_counts.get('FP', 0)} / {confusion_counts.get('TN', 0)} / {confusion_counts.get('FN', 0)}",
            f"- total_cost: {int(final['total_cost'])}",
            "",
            "不采用 Day16 tuned 或 Day18 ensemble 作为最终主结果：Day16 tuned 在 valid 上改善但 official test 没有泛化，"
            "Day18 ensemble 未满足进入 official test 的 OOF 筛选条件。Day6 的 8640 是 test 回溯观察，不作为严谨最终结果。",
            "",
            "![Cost policy comparison](../outputs/figures/final/final_cost_policy_comparison.png)",
            "",
            "## 2. Top-K 维修容量分析",
            "",
            "如果维修团队只能检查风险分数最高的 Top-K 匿名样本，覆盖真实 APS 故障的结果如下：",
            "",
            *topk_lines,
            "",
            "这说明模型排序有维修排队价值：即使不直接讨论某个固定 threshold，最高风险队列也显著富集真实故障样本。",
            "",
            "![Top-K maintenance capacity](../outputs/figures/final/final_topk_maintenance_capacity.png)",
            "",
            "## 3. 风险层级人口与业务队列",
            "",
            *risk_lines,
            "",
            "Critical / High 是最适合优先检修的层级，但 High 中仍包含较多 FP，意味着高风险队列会带来额外检查工作量。"
            "`sample_id` 仅表示匿名样本编号，不是真实车辆 ID。",
            "",
            "![Risk workload](../outputs/figures/final/final_risk_level_workload.png)",
            "",
            "## 4. 成本策略对比",
            "",
            f"- naive_all_negative total_cost = {int(naive['total_cost'])}.",
            f"- day14_baseline_median_all total_cost = {int(baseline['total_cost'])}.",
            f"- {release_policy.model_version} total_cost = {int(final['total_cost'])}.",
            f"- day16_tuned_best total_cost = {int(tuned['total_cost'])}.",
            f"- final candidate 相对 naive baseline 成本下降 {int(final['cost_reduction'])}，下降率 {_format_pct(final['cost_reduction_rate'])}.",
            f"- final candidate 相对 Day14 baseline 降低 {int(baseline['total_cost'] - final['total_cost'])} 成本。",
            "",
            "Day18 OOF policy 在 CSV 中保留为 `oof_train`，只用于内部稳定性观察，不能与 official test policy 直接横向排名。",
            "",
            "## 5. Decile / Lift / Gain 分析",
            "",
            f"- decile=1 pos_rate = {_format_pct(decile_1['pos_rate'])}.",
            f"- overall_pos_rate = {_format_pct(decile_1['overall_pos_rate'])}.",
            f"- decile=1 lift = {_format_float(decile_1['lift'], 2)}.",
            f"- cumulative_recall@decile1 = {_format_pct(decile_1['cumulative_recall'])}.",
            f"- cumulative_recall@decile2 = {_format_pct(decile_2['cumulative_recall'])}.",
            f"- cumulative_recall@decile3 = {_format_pct(decile_3['cumulative_recall'])}.",
            "",
            "最高风险分位明显集中真实 APS 故障，支持“先检修高风险样本”的维修排序逻辑。",
            "",
            "![Decile lift gain](../outputs/figures/final/final_decile_lift_gain.png)",
            "",
            "## 6. 阈值敏感性分析",
            "",
            threshold_line(
                f"final threshold={release_policy.decision_threshold:.2f}",
                final_threshold_row,
            ),
            threshold_line("min cost threshold", min_cost),
            threshold_line("min cost with recall >= 0.96", recall_096),
            threshold_line("min cost with recall >= 0.97", recall_097),
            threshold_line("min cost with FN <= 15", fn_15),
            threshold_line("min cost with FN <= 12", fn_12),
            "",
            "这些结果只用于策略敏感性展示，不能用来反向修改最终 threshold；"
            f"最终推荐阈值仍保留发布政策中的 {release_policy.decision_threshold:.2f}。",
            "",
            "![Threshold sensitivity](../outputs/figures/final/final_threshold_sensitivity.png)",
            "",
            "## 7. FP / FN 错误分析",
            "",
            f"- TP={confusion_counts.get('TP', 0)}, FP={confusion_counts.get('FP', 0)}, TN={confusion_counts.get('TN', 0)}, FN={confusion_counts.get('FN', 0)}.",
            f"- FN by risk_level: {fn_risk_text or 'none'}.",
            f"- FP by risk_level: {fp_risk_text or 'none'}.",
            "",
            "FN 是 APS 项目中最关键的业务风险；后续 Day21 的模型解释性 / SHAP 分析可以优先聚焦 FN 和高置信 FP 样本，"
            "但不能虚构匿名字段的真实物理含义。",
            "",
            "![Confusion error breakdown](../outputs/figures/final/final_confusion_error_breakdown.png)",
            "",
            "## 8. 面试可讲的 3-5 个结论",
            "",
            "- 业务成本角度：final candidate 将 naive baseline 的漏报成本主导问题大幅压低，official test total_cost 为 9980。",
            "- 维修容量角度：Top-K 队列可以把有限检修资源集中到高风险匿名样本上，而不是平均分配。",
            "- 风险分层角度：Critical / High 进入 APS 检查队列，Medium 进入复核队列，Low 继续非 APS 故障诊断。",
            "- 模型排序角度：decile=1 的 lift 显著高于 1，说明风险分数排序对真实 APS 故障有富集能力。",
            "- 阈值策略角度：阈值变化会同时改变工作量、FN 和成本；敏感性分析用于解释策略，不用于反向选择最终阈值。",
            "",
        ]
    )


def save_report(
    tables: dict[str, pd.DataFrame],
    report_path: Path,
    release_policy: ReleasePolicy,
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = build_markdown_report(tables, release_policy=release_policy)
    report_path.write_text(report, encoding="utf-8")
    print(f"[REPORT] {report_path}")


def read_day19_exports(paths: Day20Paths) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    prediction_path = paths.sql_export_dir / "model_prediction_results.csv"
    policy_path = paths.sql_export_dir / "model_policy_comparison.csv"
    threshold_path = paths.sql_export_dir / "threshold_sensitivity_results.csv"
    for path in [prediction_path, policy_path, threshold_path]:
        if not path.exists():
            raise FileNotFoundError(f"Missing Day19 SQL export: {path}")
    return (
        pd.read_csv(prediction_path),
        pd.read_csv(policy_path),
        pd.read_csv(threshold_path),
    )


def main() -> None:
    cfg = get_config(PROJECT_ROOT / "config" / "config.yaml")
    paths = Day20Paths(
        sql_export_dir=cfg.project_root / "outputs" / "sql_exports",
        final_figure_dir=cfg.figures_dir / "final",
        final_table_dir=cfg.tables_dir / "final",
        report_path=cfg.reports_dir / "sql_business_insights.md",
    )

    predictions, policies, thresholds = read_day19_exports(paths)
    tables = build_all_tables(
        predictions=predictions,
        policies=policies,
        thresholds=thresholds,
        fp_cost=int(cfg.false_positive_cost),
        fn_cost=int(cfg.false_negative_cost),
        release_policy=cfg.release,
    )
    save_tables(tables, paths.final_table_dir)
    save_figures(
        tables,
        paths.final_figure_dir,
        release_policy=cfg.release,
    )
    save_report(
        tables,
        paths.report_path,
        release_policy=cfg.release,
    )

    print("Day20 SQL business insight outputs generated.")
    print("No MySQL connection, model training, threshold reselection, or raw data edit was performed.")


if __name__ == "__main__":
    main()
