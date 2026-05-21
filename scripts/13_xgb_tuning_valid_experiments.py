"""运行 Day 15 Controlled XGBoost Tuning。

本脚本只使用 official train 内部划分出的 train_inner / valid，不使用 official test。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from scania_aps.config import get_config  # noqa: E402
from scania_aps.data.load_data import load_train_test_with_target  # noqa: E402
from scania_aps.data.split_data import split_train_valid  # noqa: E402
from scania_aps.features.structural_feature_design import (  # noqa: E402
    load_structural_feature_config,
)
from scania_aps.models.xgb_tuning import run_xgb_tuning_experiments  # noqa: E402


def _apply_trial_runtime_controls(cfg) -> dict[str, int | str]:
    """根据环境变量或配置中的自动降级开关确定实际 trial 数。"""

    runtime = cfg.xgb_tuning.get("max_runtime_control", {})
    source = "config"
    broad_trials = int(cfg.xgb_tuning["broad_trials_per_strategy"])
    refine_trials = int(cfg.xgb_tuning["refine_trials_per_strategy"])

    if os.getenv("SCANIA_APS_DAY15_USE_MIN_TRIALS") == "1":
        broad_trials = int(runtime.get("min_broad_trials_per_strategy", broad_trials))
        refine_trials = int(runtime.get("min_refine_trials_per_strategy", refine_trials))
        source = "min_runtime_control"

    if os.getenv("SCANIA_APS_DAY15_BROAD_TRIALS"):
        broad_trials = int(os.environ["SCANIA_APS_DAY15_BROAD_TRIALS"])
        source = "environment_override"
    if os.getenv("SCANIA_APS_DAY15_REFINE_TRIALS"):
        refine_trials = int(os.environ["SCANIA_APS_DAY15_REFINE_TRIALS"])
        source = "environment_override"

    cfg.xgb_tuning["broad_trials_per_strategy"] = broad_trials
    cfg.xgb_tuning["refine_trials_per_strategy"] = refine_trials
    return {
        "broad_trials_per_strategy": broad_trials,
        "refine_trials_per_strategy": refine_trials,
        "trial_count_source": source,
    }


def _plot_outputs(results: dict, figures_dir: Path) -> None:
    """生成少量 Day15 复盘图表。"""

    figures_dir.mkdir(parents=True, exist_ok=True)
    trial_results = results["tuning_trial_results"]
    best_summary = results["tuning_best_summary"]
    refinement_summary = results["tuning_refinement_summary"]

    if not trial_results.empty:
        top20 = trial_results.head(20).sort_values("total_cost", ascending=True).copy()
        strategy_labels = {
            "baseline_median_all": "base",
            "median_all_structural_all": "struct_all",
            "drop_high_missing_median": "drop80",
        }
        color_map = {
            "baseline_median_all": "#4C78A8",
            "median_all_structural_all": "#F58518",
            "drop_high_missing_median": "#54A24B",
        }

        def compact_trial_label(row) -> str:
            trial_id = str(row["trial_id"])
            stage = "B" if row["search_stage"] == "broad" else "R"
            trial_no = trial_id.rsplit("_", 1)[-1]
            strategy = strategy_labels.get(row["candidate_strategy"], row["candidate_strategy"])
            return f"{int(row['global_trial_rank']):02d}. {strategy} {stage}{trial_no}"

        labels = top20.apply(compact_trial_label, axis=1)
        colors = top20["candidate_strategy"].map(color_map).fillna("#888888")
        fig, ax = plt.subplots(figsize=(12, 8))
        bars = ax.barh(labels, top20["total_cost"], color=colors)
        ax.invert_yaxis()
        ax.set_xlabel("Valid total cost")
        ax.set_ylabel("Trial rank / strategy / stage")
        ax.set_title("Day15 Top 20 XGBoost tuning trials by valid cost")
        ax.grid(axis="x", alpha=0.25)
        ax.set_xlim(0, top20["total_cost"].max() * 1.10)
        for bar, value in zip(bars, top20["total_cost"]):
            ax.text(
                value + top20["total_cost"].max() * 0.01,
                bar.get_y() + bar.get_height() / 2,
                f"{int(value)}",
                va="center",
                fontsize=8,
            )
        ax.legend(
            handles=[
                Patch(color=color, label=label)
                for label, color in {
                    "base = baseline_median_all": color_map["baseline_median_all"],
                    "struct_all = median_all_structural_all": color_map[
                        "median_all_structural_all"
                    ],
                    "drop80 = drop_high_missing_median": color_map[
                        "drop_high_missing_median"
                    ],
                }.items()
            ],
            loc="upper center",
            bbox_to_anchor=(0.5, -0.08),
            ncol=3,
            fontsize=8,
        )
        fig.tight_layout(rect=[0, 0.04, 1, 1])
        fig.savefig(figures_dir / "day15_xgb_tuning_valid_cost_top20.png", dpi=150)
        plt.close()

    if not best_summary.empty:
        plt.figure(figsize=(8, 5))
        plt.bar(best_summary["candidate_strategy"], best_summary["total_cost"])
        plt.ylabel("Best valid total cost")
        plt.title("Day15 best valid cost by candidate strategy")
        plt.xticks(rotation=25, ha="right")
        plt.tight_layout()
        plt.savefig(figures_dir / "day15_xgb_tuning_strategy_cost_compare.png", dpi=150)
        plt.close()

    if not refinement_summary.empty:
        plot_df = refinement_summary.sort_values("candidate_strategy")
        x = range(len(plot_df))
        plt.figure(figsize=(9, 5))
        plt.plot(x, plot_df["broad_best_total_cost"], marker="o", label="broad best")
        plt.plot(x, plot_df["refined_best_total_cost"], marker="o", label="refined best")
        plt.xticks(x, plot_df["candidate_strategy"], rotation=25, ha="right")
        plt.ylabel("Valid total cost")
        plt.title("Day15 broad vs refined search")
        plt.legend()
        plt.tight_layout()
        plt.savefig(figures_dir / "day15_xgb_tuning_broad_vs_refined.png", dpi=150)
        plt.close()


def main() -> None:
    """从项目根目录运行 Day15 valid-only XGBoost 调参。"""

    cfg = get_config(PROJECT_ROOT / "config" / "config.yaml")
    structural_config = load_structural_feature_config(
        PROJECT_ROOT / "config" / "structural_features.yaml"
    )
    runtime_info = _apply_trial_runtime_controls(cfg)

    cfg.metrics_dir.mkdir(parents=True, exist_ok=True)
    cfg.tables_dir.mkdir(parents=True, exist_ok=True)
    cfg.predictions_dir.mkdir(parents=True, exist_ok=True)
    cfg.figures_dir.mkdir(parents=True, exist_ok=True)

    train_df, _official_test_df = load_train_test_with_target(cfg)
    train_inner_df, valid_df = split_train_valid(train_df, cfg)

    results = run_xgb_tuning_experiments(
        train_inner_df=train_inner_df,
        valid_df=valid_df,
        cfg=cfg,
        structural_config=structural_config,
        candidate_strategies=cfg.xgb_tuning["candidate_strategies"],
    )

    results["tuning_trial_results"].to_csv(
        cfg.metrics_dir / "day15_xgb_tuning_valid_trial_results.csv",
        index=False,
    )
    results["tuning_best_summary"].to_csv(
        cfg.metrics_dir / "day15_xgb_tuning_valid_best_summary.csv",
        index=False,
    )
    results["tuning_threshold_metrics"].to_csv(
        cfg.metrics_dir / "day15_xgb_tuning_valid_threshold_metrics.csv",
        index=False,
    )
    results["tuning_refinement_summary"].to_csv(
        cfg.metrics_dir / "day15_xgb_tuning_refinement_summary.csv",
        index=False,
    )
    results["tuning_candidate_metadata"].assign(**runtime_info).to_csv(
        cfg.tables_dir / "day15_xgb_tuning_candidate_metadata.csv",
        index=False,
    )
    results["tuning_search_space"].to_csv(
        cfg.tables_dir / "day15_xgb_tuning_search_space.csv",
        index=False,
    )
    results["tuning_top_trials_by_strategy"].to_csv(
        cfg.tables_dir / "day15_xgb_tuning_top_trials_by_strategy.csv",
        index=False,
    )
    results["tuning_best_predictions"].to_csv(
        cfg.predictions_dir / "day15_xgb_tuning_valid_best_predictions.csv",
        index=False,
    )
    _plot_outputs(results, cfg.figures_dir)

    display_cols = [
        "candidate_strategy",
        "search_stage",
        "trial_id",
        "threshold",
        "precision",
        "recall",
        "f2",
        "average_precision",
        "fp",
        "fn",
        "total_cost",
    ]
    print("Day 15 Controlled XGBoost Tuning 完成。")
    print(
        "本轮只使用 train_inner / valid；official test 没有参与调参、阈值选择或结果排序。"
    )
    print(
        "实际 trial 数："
        f"broad={runtime_info['broad_trials_per_strategy']}，"
        f"refined={runtime_info['refine_trials_per_strategy']}，"
        f"来源={runtime_info['trial_count_source']}"
    )
    print(results["tuning_best_summary"][display_cols].to_string(index=False))


if __name__ == "__main__":
    main()
