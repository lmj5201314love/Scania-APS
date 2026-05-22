"""Day 17: run OOF threshold stability and bin projection experiments."""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from scania_aps.config import get_config
from scania_aps.data.load_data import load_train_test_with_target
from scania_aps.models.oof_threshold_experiments import (
    run_oof_recall_floor_bin_projection_experiments,
)


def _load_structural_config(cfg) -> dict:
    """Read structural feature config."""

    config_path = cfg.project_root / "config" / "structural_features.yaml"
    with config_path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def _ensure_output_dirs(cfg) -> None:
    """Create output directories used by this script."""

    for directory in [cfg.metrics_dir, cfg.predictions_dir, cfg.tables_dir, cfg.figures_dir]:
        directory.mkdir(parents=True, exist_ok=True)


def _save_outputs(outputs: dict[str, pd.DataFrame], cfg) -> None:
    """Save Day17 result tables."""

    outputs["oof_threshold_metrics"].to_csv(
        cfg.metrics_dir / "day17_oof_threshold_metrics.csv",
        index=False,
    )
    outputs["oof_best_threshold_summary"].to_csv(
        cfg.metrics_dir / "day17_oof_best_threshold_summary.csv",
        index=False,
    )
    outputs["oof_stability_summary"].to_csv(
        cfg.metrics_dir / "day17_oof_stability_summary.csv",
        index=False,
    )
    outputs["oof_strategy_compare"].to_csv(
        cfg.metrics_dir / "day17_oof_strategy_compare.csv",
        index=False,
    )
    outputs["raw_oof_predictions"].to_csv(
        cfg.predictions_dir / "day17_oof_raw_predictions.csv",
        index=False,
    )
    outputs["averaged_oof_predictions"].to_csv(
        cfg.predictions_dir / "day17_oof_averaged_predictions.csv",
        index=False,
    )
    outputs["oof_fold_summary"].to_csv(
        cfg.tables_dir / "day17_oof_fold_summary.csv",
        index=False,
    )
    outputs["bin_projection_metadata"].to_csv(
        cfg.tables_dir / "day17_bin_projection_metadata.csv",
        index=False,
    )
    outputs["oof_candidate_metadata"].to_csv(
        cfg.tables_dir / "day17_oof_candidate_metadata.csv",
        index=False,
    )


def _plot_threshold_curves(outputs: dict[str, pd.DataFrame], cfg) -> None:
    """Save compact Day17 diagnostic plots."""

    threshold_metrics = outputs["oof_threshold_metrics"]
    best_summary = outputs["oof_best_threshold_summary"]
    if threshold_metrics.empty or best_summary.empty:
        return

    plt.figure(figsize=(11, 7))
    for strategy, group in threshold_metrics.groupby("candidate_strategy"):
        plt.plot(group["threshold"], group["total_cost"], label=strategy)
    plt.xlabel("Threshold")
    plt.ylabel("OOF total cost")
    plt.title("Day17 OOF threshold vs total cost")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(cfg.figures_dir / "day17_oof_cost_threshold_curve.png", dpi=160)
    plt.close()

    plt.figure(figsize=(11, 7))
    for strategy, group in threshold_metrics.groupby("candidate_strategy"):
        plt.plot(group["threshold"], group["recall"], label=strategy)
    plt.xlabel("Threshold")
    plt.ylabel("OOF recall")
    plt.title("Day17 OOF threshold vs recall")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(cfg.figures_dir / "day17_oof_recall_threshold_curve.png", dpi=160)
    plt.close()

    cost_min = best_summary[best_summary["threshold_selection_rule"].eq("cost_min")]
    plt.figure(figsize=(10, 6))
    plt.barh(cost_min["candidate_strategy"], cost_min["total_cost"])
    plt.xlabel("OOF total cost")
    plt.title("Day17 OOF cost_min by strategy")
    plt.tight_layout()
    plt.savefig(cfg.figures_dir / "day17_oof_strategy_cost_compare.png", dpi=160)
    plt.close()

    pivot = best_summary.pivot_table(
        index="threshold_selection_rule",
        columns="candidate_strategy",
        values="total_cost",
        aggfunc="min",
    )
    ax = pivot.plot(kind="bar", figsize=(12, 7))
    ax.set_xlabel("Threshold selection rule")
    ax.set_ylabel("OOF total cost")
    ax.set_title("Day17 OOF threshold rule comparison")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(cfg.figures_dir / "day17_oof_threshold_rule_compare.png", dpi=160)
    plt.close()


def _print_summary(outputs: dict[str, pd.DataFrame], cfg) -> None:
    """Print short console summary."""

    best_summary = outputs["oof_best_threshold_summary"]
    n_splits = int(cfg.oof_threshold["cv"]["n_splits"])
    n_repeats = int(cfg.oof_threshold["cv"]["n_repeats"])
    print(f"Day17 OOF experiment finished. Configured CV: {n_splits} folds x {n_repeats} repeats.")
    if "SCANIA_APS_DAY17_N_REPEATS" in __import__("os").environ:
        print(
            "Runtime override detected: "
            f"n_repeats={__import__('os').environ['SCANIA_APS_DAY17_N_REPEATS']}"
        )
    columns = [
        "candidate_strategy",
        "threshold_selection_rule",
        "threshold",
        "precision",
        "recall",
        "f2",
        "fp",
        "fn",
        "total_cost",
    ]
    print(best_summary[columns].to_string(index=False))


def main() -> None:
    """Run Day17 OOF experiments from the project root."""

    cfg = get_config(PROJECT_ROOT / "config" / "config.yaml")
    structural_config = _load_structural_config(cfg)
    _ensure_output_dirs(cfg)

    train_df, _test_df = load_train_test_with_target(cfg)
    outputs = run_oof_recall_floor_bin_projection_experiments(
        train_df=train_df,
        cfg=cfg,
        structural_config=structural_config,
        oof_config=cfg.oof_threshold,
        candidate_strategies=cfg.oof_threshold["candidate_strategies"],
    )
    _save_outputs(outputs, cfg)
    _plot_threshold_curves(outputs, cfg)
    _print_summary(outputs, cfg)


if __name__ == "__main__":
    main()
