"""运行 Day16 tuned XGBoost official test 观察。

本脚本固定使用 Day15 valid 选出的参数和阈值，不在 official test 上重新调参或选阈值。
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from scania_aps.config import get_config  # noqa: E402
from scania_aps.data.load_data import load_train_test_with_target  # noqa: E402
from scania_aps.data.split_data import split_train_valid  # noqa: E402
from scania_aps.features.structural_feature_design import (  # noqa: E402
    load_structural_feature_config,
)
from scania_aps.models.xgb_tuning_test_evaluation import (  # noqa: E402
    DEFAULT_DAY16_CANDIDATE_STRATEGIES,
    evaluate_tuned_xgb_candidates_on_test,
)


def _plot_outputs(results: dict[str, pd.DataFrame], cfg) -> None:
    """生成 Day16 对比图表。"""

    cfg.figures_dir.mkdir(parents=True, exist_ok=True)
    test_results = results["tuned_test_results"]
    compare = results["tuned_valid_test_compare"]

    if not test_results.empty:
        plot_df = test_results.sort_values("total_cost")
        plt.figure(figsize=(9, 5))
        plt.bar(plot_df["candidate_strategy"], plot_df["total_cost"])
        plt.ylabel("Official test total cost")
        plt.title("Day16 tuned XGBoost official test cost")
        plt.xticks(rotation=25, ha="right")
        plt.tight_layout()
        plt.savefig(cfg.figures_dir / "day16_xgb_tuning_test_cost_compare.png", dpi=150)
        plt.close()

    if not compare.empty:
        plot_df = compare.sort_values("candidate_strategy")
        x = range(len(plot_df))
        plt.figure(figsize=(9, 5))
        plt.plot(x, plot_df["valid_total_cost"], marker="o", label="valid")
        plt.plot(x, plot_df["test_total_cost"], marker="o", label="official test")
        plt.xticks(x, plot_df["candidate_strategy"], rotation=25, ha="right")
        plt.ylabel("Total cost")
        plt.title("Day16 valid vs official test cost")
        plt.legend()
        plt.tight_layout()
        plt.savefig(cfg.figures_dir / "day16_xgb_tuning_valid_vs_test_cost.png", dpi=150)
        plt.close()


def main() -> None:
    """从项目根目录运行 Day16 tuned official test 观察。"""

    cfg = get_config(PROJECT_ROOT / "config" / "config.yaml")
    structural_config = load_structural_feature_config(
        PROJECT_ROOT / "config" / "structural_features.yaml"
    )
    day15_best_summary = pd.read_csv(
        cfg.metrics_dir / "day15_xgb_tuning_valid_best_summary.csv"
    )

    cfg.metrics_dir.mkdir(parents=True, exist_ok=True)
    cfg.predictions_dir.mkdir(parents=True, exist_ok=True)
    cfg.tables_dir.mkdir(parents=True, exist_ok=True)

    train_df, test_df = load_train_test_with_target(cfg)
    train_inner_df, valid_df = split_train_valid(train_df, cfg)

    results = evaluate_tuned_xgb_candidates_on_test(
        train_inner_df=train_inner_df,
        valid_df=valid_df,
        test_df=test_df,
        cfg=cfg,
        structural_config=structural_config,
        day15_best_summary=day15_best_summary,
        candidate_strategies=DEFAULT_DAY16_CANDIDATE_STRATEGIES,
    )

    results["tuned_test_results"].to_csv(
        cfg.metrics_dir / "day16_xgb_tuning_test_results.csv",
        index=False,
    )
    results["tuned_valid_test_compare"].to_csv(
        cfg.metrics_dir / "day16_xgb_tuning_valid_test_compare.csv",
        index=False,
    )
    results["tuned_test_predictions"].to_csv(
        cfg.predictions_dir / "day16_xgb_tuning_test_predictions.csv",
        index=False,
    )
    results["tuned_test_metadata"].to_csv(
        cfg.tables_dir / "day16_xgb_tuning_test_metadata.csv",
        index=False,
    )
    _plot_outputs(results, cfg)

    display_cols = [
        "candidate_strategy",
        "threshold",
        "precision",
        "recall",
        "f2",
        "average_precision",
        "fp",
        "fn",
        "total_cost",
        "trial_id",
        "search_stage",
    ]
    print("Day16 tuned XGBoost official test 观察完成。")
    print("本轮固定 Day15 valid 参数和阈值；official test 没有参与调参或阈值选择。")
    print(results["tuned_test_results"][display_cols].to_string(index=False))


if __name__ == "__main__":
    main()
