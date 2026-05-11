"""运行 Day 11 前缀组结构信号分析。"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from scania_aps.analysis.prefix_group_analysis import (  # noqa: E402
    build_prefix_feature_members,
    build_prefix_group_signal_ranking,
    build_prefix_group_summary,
)
from scania_aps.config import get_config  # noqa: E402


def _save_horizontal_bar(
    df: pd.DataFrame,
    *,
    value_col: str,
    label_col: str,
    title: str,
    xlabel: str,
    output_path: Path,
    top_n: int = 20,
) -> None:
    """保存 prefix 组 Top N 横向柱状图。"""

    plot_df = (
        df.replace([float("inf"), float("-inf")], pd.NA)
        .dropna(subset=[value_col])
        .sort_values(value_col, ascending=False)
        .head(top_n)
        .sort_values(value_col, ascending=True)
    )
    fig_height = max(5, top_n * 0.28)
    plt.figure(figsize=(10, fig_height))
    plt.barh(plot_df[label_col], plot_df[value_col], color="#4C78A8")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("prefix")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def main() -> None:
    """读取 Day 10 输出，生成 Day 11 prefix 组分析结果。"""

    cfg = get_config(PROJECT_ROOT / "config" / "config.yaml")
    cfg.metrics_dir.mkdir(parents=True, exist_ok=True)
    cfg.tables_dir.mkdir(parents=True, exist_ok=True)
    cfg.figures_dir.mkdir(parents=True, exist_ok=True)

    distribution_summary = pd.read_csv(cfg.metrics_dir / "day10_feature_distribution_summary.csv")
    missing_zero_summary = pd.read_csv(cfg.metrics_dir / "day10_missing_zero_summary.csv")
    pos_neg_diff = pd.read_csv(cfg.metrics_dir / "day10_pos_neg_distribution_diff.csv")
    drift_summary = pd.read_csv(cfg.metrics_dir / "day10_train_valid_test_drift_summary.csv")

    prefix_group_summary = build_prefix_group_summary(
        distribution_summary=distribution_summary,
        missing_zero_summary=missing_zero_summary,
        pos_neg_diff=pos_neg_diff,
        drift_summary=drift_summary,
        reference_dataset="train_inner",
    )
    prefix_signal_ranking = build_prefix_group_signal_ranking(prefix_group_summary)
    prefix_members = build_prefix_feature_members(prefix_group_summary)

    output_paths = {
        "summary": cfg.metrics_dir / "day11_prefix_group_summary.csv",
        "ranking": cfg.metrics_dir / "day11_prefix_group_signal_ranking.csv",
        "members": cfg.tables_dir / "day11_prefix_feature_members.csv",
    }
    prefix_group_summary.to_csv(output_paths["summary"], index=False, encoding="utf-8-sig")
    prefix_signal_ranking.to_csv(output_paths["ranking"], index=False, encoding="utf-8-sig")
    prefix_members.to_csv(output_paths["members"], index=False, encoding="utf-8-sig")

    _save_horizontal_bar(
        prefix_group_summary,
        value_col="avg_missing_rate",
        label_col="prefix",
        title="Day 11 Prefix Average Missing Rate Top 20",
        xlabel="average missing rate",
        output_path=cfg.figures_dir / "day11_prefix_avg_missing_rate_top20.png",
    )
    _save_horizontal_bar(
        prefix_group_summary,
        value_col="avg_zero_rate",
        label_col="prefix",
        title="Day 11 Prefix Average Zero Rate Top 20",
        xlabel="average zero rate",
        output_path=cfg.figures_dir / "day11_prefix_avg_zero_rate_top20.png",
    )
    _save_horizontal_bar(
        prefix_group_summary,
        value_col="avg_abs_pos_neg_missing_diff",
        label_col="prefix",
        title="Day 11 Prefix Pos/Neg Missing Difference Top 20",
        xlabel="average absolute pos/neg missing-rate difference",
        output_path=cfg.figures_dir / "day11_prefix_pos_neg_missing_diff_top20.png",
    )
    _save_horizontal_bar(
        prefix_signal_ranking,
        value_col="signal_score",
        label_col="prefix",
        title="Day 11 Prefix Signal Score Top 20",
        xlabel="signal score",
        output_path=cfg.figures_dir / "day11_prefix_signal_score_top20.png",
    )
    _save_horizontal_bar(
        prefix_signal_ranking,
        value_col="drift_risk_score",
        label_col="prefix",
        title="Day 11 Prefix Drift Risk Top 20",
        xlabel="drift risk score",
        output_path=cfg.figures_dir / "day11_prefix_drift_risk_top20.png",
    )

    print("Day 11 前缀组结构信号分析已完成。")
    print(f"前缀组数量：{prefix_group_summary.shape[0]}")
    for path in output_paths.values():
        print(f"输出：{path}")
    print(f"图表目录：{cfg.figures_dir}")

    print("\n平均缺失率 Top 5：")
    print(
        prefix_group_summary.sort_values("avg_missing_rate", ascending=False)[
            ["prefix", "feature_count", "avg_missing_rate", "max_missing_rate"]
        ]
        .head(5)
        .to_string(index=False)
    )
    print("\n平均零值率 Top 5：")
    print(
        prefix_group_summary.sort_values("avg_zero_rate", ascending=False)[
            ["prefix", "feature_count", "avg_zero_rate", "max_zero_rate"]
        ]
        .head(5)
        .to_string(index=False)
    )
    print("\n结构信号得分 Top 10：")
    print(
        prefix_signal_ranking[
            [
                "prefix",
                "feature_count",
                "signal_score",
                "drift_risk_score",
                "recommendation",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
