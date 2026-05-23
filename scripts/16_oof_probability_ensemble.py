"""Day 18 OOF probability ensemble experiment runner.

本脚本只使用 official train 内部的 OOF 预测，不读取 official test 做评估。
"""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from scania_aps.config import get_config  # noqa: E402
from scania_aps.data.load_data import load_train_test_with_target  # noqa: E402
from scania_aps.models.oof_ensemble_experiments import (  # noqa: E402
    run_oof_probability_ensemble_experiments,
)


def load_structural_config(cfg) -> dict:
    """读取结构特征配置。"""

    config_path = cfg.project_root / "config" / "structural_features.yaml"
    with config_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def save_table(df: pd.DataFrame, path: Path) -> None:
    """保存 CSV，并自动创建目录。"""

    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def _plot_cost_compare(best_summary: pd.DataFrame, figures_dir: Path) -> None:
    """绘制 cost_min 下 ensemble 成本对比。"""

    plot_df = (
        best_summary[best_summary["threshold_selection_rule"].eq("cost_min")]
        .sort_values("total_cost")
        .head(12)
    )
    plt.figure(figsize=(12, 7))
    plt.barh(plot_df["ensemble_name"], plot_df["total_cost"], color="#4C78A8")
    plt.xlabel("OOF total cost")
    plt.ylabel("Ensemble recipe")
    plt.title("Day18 OOF Ensemble Cost Compare (cost_min)")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(figures_dir / "day18_oof_ensemble_cost_compare.png", dpi=150)
    plt.close()


def _plot_fn_fp_tradeoff(best_summary: pd.DataFrame, figures_dir: Path) -> None:
    """绘制 cost_min 下 FN/FP 权衡。"""

    plot_df = best_summary[best_summary["threshold_selection_rule"].eq("cost_min")].copy()
    plt.figure(figsize=(9, 7))
    colors = plot_df["ensemble_group"].map(
        {"main": "#4C78A8", "auxiliary": "#F58518", "diagnostic": "#E45756"}
    ).fillna("#999999")
    plt.scatter(plot_df["fp"], plot_df["fn"], s=80, c=colors)
    for _, row in plot_df.iterrows():
        plt.annotate(row["ensemble_name"], (row["fp"], row["fn"]), fontsize=8, alpha=0.8)
    plt.xlabel("OOF FP")
    plt.ylabel("OOF FN")
    plt.title("Day18 OOF Ensemble FN/FP Tradeoff (cost_min)")
    plt.tight_layout()
    plt.savefig(figures_dir / "day18_oof_ensemble_fn_fp_tradeoff.png", dpi=150)
    plt.close()


def _plot_threshold_rule_compare(best_summary: pd.DataFrame, figures_dir: Path) -> None:
    """绘制不同阈值规则下的最低成本。"""

    plot_df = (
        best_summary.groupby("threshold_selection_rule", as_index=False)
        .agg(best_cost=("total_cost", "min"))
        .sort_values("best_cost")
    )
    plt.figure(figsize=(10, 6))
    plt.bar(plot_df["threshold_selection_rule"], plot_df["best_cost"], color="#72B7B2")
    plt.ylabel("Best OOF total cost")
    plt.xlabel("Threshold selection rule")
    plt.title("Day18 Threshold Rule Compare")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(figures_dir / "day18_oof_ensemble_threshold_rule_compare.png", dpi=150)
    plt.close()


def _plot_fn_overlap(fn_overlap_summary: pd.DataFrame, figures_dir: Path) -> None:
    """绘制 structural_all FN 被补回的数量。"""

    if fn_overlap_summary.empty:
        return
    row = fn_overlap_summary.iloc[0]
    labels = [
        "reference_fn_count",
        "indicator_rescued_fn",
        "prefixzero_rescued_fn",
        "either_rescued_fn",
        "all_models_fn",
    ]
    values = [row[label] for label in labels]
    plt.figure(figsize=(10, 6))
    plt.bar(labels, values, color="#54A24B")
    plt.ylabel("OOF sample count")
    plt.title("Day18 OOF FN Overlap Summary")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(figures_dir / "day18_oof_fn_overlap_summary.png", dpi=150)
    plt.close()


def save_figures(outputs: dict[str, pd.DataFrame], figures_dir: Path) -> None:
    """保存 Day18 图表。"""

    figures_dir.mkdir(parents=True, exist_ok=True)
    _plot_cost_compare(outputs["oof_ensemble_best_summary"], figures_dir)
    _plot_fn_fp_tradeoff(outputs["oof_ensemble_best_summary"], figures_dir)
    _plot_threshold_rule_compare(outputs["oof_ensemble_best_summary"], figures_dir)
    _plot_fn_overlap(outputs["oof_fn_overlap_summary"], figures_dir)


def main() -> None:
    """运行 Day18 OOF probability ensemble。"""

    cfg = get_config(PROJECT_ROOT / "config" / "config.yaml")
    structural_config = load_structural_config(cfg)
    ensemble_config = cfg.oof_ensemble

    train_df, _test_df = load_train_test_with_target(cfg)
    outputs = run_oof_probability_ensemble_experiments(
        train_df=train_df,
        cfg=cfg,
        structural_config=structural_config,
        ensemble_config=ensemble_config,
        base_candidate_strategies=ensemble_config["base_candidate_strategies"],
    )

    save_table(
        outputs["oof_base_raw_predictions"],
        cfg.predictions_dir / "day18_oof_base_raw_predictions.csv",
    )
    save_table(
        outputs["oof_base_averaged_predictions"],
        cfg.predictions_dir / "day18_oof_base_averaged_predictions.csv",
    )
    save_table(
        outputs["oof_ensemble_predictions"],
        cfg.predictions_dir / "day18_oof_ensemble_predictions.csv",
    )

    save_table(
        outputs["oof_ensemble_threshold_metrics"],
        cfg.metrics_dir / "day18_oof_ensemble_threshold_metrics.csv",
    )
    save_table(
        outputs["oof_ensemble_best_summary"],
        cfg.metrics_dir / "day18_oof_ensemble_best_summary.csv",
    )
    save_table(
        outputs["oof_ensemble_strategy_compare"],
        cfg.metrics_dir / "day18_oof_ensemble_strategy_compare.csv",
    )
    save_table(
        outputs["oof_base_threshold_metrics"],
        cfg.metrics_dir / "day18_oof_base_threshold_metrics.csv",
    )
    save_table(
        outputs["oof_base_best_summary"],
        cfg.metrics_dir / "day18_oof_base_best_summary.csv",
    )

    save_table(
        outputs["oof_fn_overlap_summary"],
        cfg.tables_dir / "day18_oof_fn_overlap_summary.csv",
    )
    save_table(
        outputs["oof_fp_overlap_summary"],
        cfg.tables_dir / "day18_oof_fp_overlap_summary.csv",
    )
    save_table(
        outputs["oof_rescuable_positive_samples"],
        cfg.tables_dir / "day18_oof_rescuable_positive_samples.csv",
    )
    save_table(
        outputs["oof_ensemble_recipe_metadata"],
        cfg.tables_dir / "day18_oof_ensemble_recipe_metadata.csv",
    )
    save_table(
        outputs["official_test_candidate_recommendations"],
        cfg.tables_dir / "day18_official_test_candidate_recommendations.csv",
    )
    save_table(
        outputs["oof_base_candidate_metadata"],
        cfg.tables_dir / "day18_oof_base_candidate_metadata.csv",
    )
    save_table(
        outputs["oof_base_fold_summary"],
        cfg.tables_dir / "day18_oof_base_fold_summary.csv",
    )

    save_figures(outputs, cfg.figures_dir)

    baseline = outputs["oof_ensemble_best_summary"][
        outputs["oof_ensemble_best_summary"]["ensemble_name"].eq("structural_all_single")
        & outputs["oof_ensemble_best_summary"]["threshold_selection_rule"].eq("cost_min")
    ]
    main_cost = outputs["oof_ensemble_best_summary"][
        outputs["oof_ensemble_best_summary"]["threshold_selection_rule"].eq("cost_min")
        & outputs["oof_ensemble_best_summary"]["ensemble_group"].eq("main")
    ].sort_values("total_cost")

    print("\nDay18 structural_all_single baseline (cost_min):")
    print(baseline[["ensemble_name", "threshold", "recall", "fp", "fn", "total_cost"]].to_string(index=False))

    print("\nDay18 main ensemble cost_min results:")
    print(main_cost[["ensemble_name", "threshold", "recall", "fp", "fn", "total_cost"]].to_string(index=False))

    print("\nDay19 candidate recommendations:")
    print(
        outputs["official_test_candidate_recommendations"][
            [
                "ensemble_name",
                "threshold_selection_rule",
                "threshold",
                "oof_recall",
                "oof_fp",
                "oof_fn",
                "oof_total_cost",
                "recommend_for_day19",
                "recommendation_reason",
            ]
        ]
        .head(12)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
