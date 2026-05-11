"""运行 Day 10 字段级分布诊断。"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from scania_aps.analysis.distribution_diagnostics import (  # noqa: E402
    build_feature_distribution_summary,
    build_missing_zero_summary,
    build_pos_neg_distribution_diff,
    build_top_feature_diagnostics,
    build_train_valid_test_drift_summary,
    get_numeric_feature_columns,
)
from scania_aps.config import get_config  # noqa: E402
from scania_aps.data.load_data import load_train_test_with_target  # noqa: E402
from scania_aps.data.split_data import split_train_valid  # noqa: E402


def _save_horizontal_bar(
    df: pd.DataFrame,
    *,
    value_col: str,
    label_col: str,
    title: str,
    xlabel: str,
    output_path: Path,
    top_n: int = 20,
    value_abs: bool = False,
) -> None:
    """保存横向 Top N 柱状图。"""

    plot_df = df.copy()
    plot_df["plot_value"] = plot_df[value_col].abs() if value_abs else plot_df[value_col]
    plot_df = (
        plot_df.replace([float("inf"), float("-inf")], pd.NA)
        .dropna(subset=["plot_value"])
        .sort_values("plot_value", ascending=False)
        .head(top_n)
        .sort_values("plot_value", ascending=True)
    )

    fig_height = max(5, top_n * 0.28)
    plt.figure(figsize=(10, fig_height))
    plt.barh(plot_df[label_col], plot_df["plot_value"], color="#4C78A8")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel("feature")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def _build_drift_plot_frame(drift_summary: pd.DataFrame) -> pd.DataFrame:
    """为 train/test 漂移图构建综合分数。"""

    drift = drift_summary.copy()
    median_scale = drift[["train_inner_median", "test_median"]].abs().max(axis=1).clip(lower=1.0)
    p99_scale = drift[["train_inner_p99", "test_p99"]].abs().max(axis=1).clip(lower=1.0)
    drift["train_test_drift_score"] = pd.concat(
        [
            drift["train_test_missing_diff_abs"],
            drift["train_test_median_diff_abs"] / median_scale,
            drift["train_test_p99_diff_abs"] / p99_scale,
        ],
        axis=1,
    ).max(axis=1)
    return drift


def main() -> None:
    """读取数据、生成字段分布诊断表和基础图表。"""

    cfg = get_config(PROJECT_ROOT / "config" / "config.yaml")
    cfg.metrics_dir.mkdir(parents=True, exist_ok=True)
    cfg.figures_dir.mkdir(parents=True, exist_ok=True)

    train_df, test_df = load_train_test_with_target(cfg)
    train_inner_df, valid_df = split_train_valid(train_df, cfg)
    feature_cols = get_numeric_feature_columns(train_inner_df, cfg.label_column)

    distribution_summary = pd.concat(
        [
            build_feature_distribution_summary(train_inner_df, feature_cols, "train_inner"),
            build_feature_distribution_summary(valid_df, feature_cols, "valid"),
            build_feature_distribution_summary(test_df, feature_cols, "official_test"),
        ],
        ignore_index=True,
    )
    missing_zero_summary = pd.concat(
        [
            build_missing_zero_summary(train_inner_df, feature_cols, "train_inner"),
            build_missing_zero_summary(valid_df, feature_cols, "valid"),
            build_missing_zero_summary(test_df, feature_cols, "official_test"),
        ],
        ignore_index=True,
    )
    pos_neg_diff = build_pos_neg_distribution_diff(
        train_inner_df,
        feature_cols,
        label_col=cfg.label_column,
    )
    drift_summary = build_train_valid_test_drift_summary(
        train_inner_df,
        valid_df,
        test_df,
        feature_cols,
    )
    top_diagnostics = build_top_feature_diagnostics(
        distribution_summary,
        missing_zero_summary,
        pos_neg_diff,
        drift_summary,
        top_n=20,
    )

    output_map = {
        "distribution_summary": cfg.metrics_dir / "day10_feature_distribution_summary.csv",
        "missing_zero_summary": cfg.metrics_dir / "day10_missing_zero_summary.csv",
        "pos_neg_diff": cfg.metrics_dir / "day10_pos_neg_distribution_diff.csv",
        "drift_summary": cfg.metrics_dir / "day10_train_valid_test_drift_summary.csv",
        "top_diagnostics": cfg.metrics_dir / "day10_top_feature_diagnostics.csv",
    }
    distribution_summary.to_csv(output_map["distribution_summary"], index=False, encoding="utf-8-sig")
    missing_zero_summary.to_csv(output_map["missing_zero_summary"], index=False, encoding="utf-8-sig")
    pos_neg_diff.to_csv(output_map["pos_neg_diff"], index=False, encoding="utf-8-sig")
    drift_summary.to_csv(output_map["drift_summary"], index=False, encoding="utf-8-sig")
    top_diagnostics.to_csv(output_map["top_diagnostics"], index=False, encoding="utf-8-sig")

    train_dist = distribution_summary[distribution_summary["dataset"].eq("train_inner")]
    train_missing_zero = missing_zero_summary[missing_zero_summary["dataset"].eq("train_inner")]
    drift_plot = _build_drift_plot_frame(drift_summary)

    _save_horizontal_bar(
        train_dist,
        value_col="skew",
        label_col="feature_name",
        title="Day 10 Top Skewed Features",
        xlabel="abs(skew)",
        output_path=cfg.figures_dir / "day10_top_skewed_features.png",
        value_abs=True,
    )
    _save_horizontal_bar(
        pos_neg_diff,
        value_col="missing_rate_diff_abs",
        label_col="feature_name",
        title="Day 10 Pos/Neg Missing Rate Difference Top 20",
        xlabel="absolute missing-rate difference",
        output_path=cfg.figures_dir / "day10_pos_neg_missing_diff_top20.png",
    )
    _save_horizontal_bar(
        drift_plot,
        value_col="train_test_drift_score",
        label_col="feature_name",
        title="Day 10 Train/Test Drift Score Top 20",
        xlabel="combined drift score",
        output_path=cfg.figures_dir / "day10_train_test_drift_top20.png",
    )
    _save_horizontal_bar(
        train_missing_zero,
        value_col="zero_rate",
        label_col="feature_name",
        title="Day 10 Zero Rate Top 20",
        xlabel="zero rate",
        output_path=cfg.figures_dir / "day10_zero_rate_top20.png",
    )

    print("Day 10 字段级分布诊断已完成。")
    print(f"数值特征数：{len(feature_cols)}")
    for path in output_map.values():
        print(f"输出：{path}")
    print(f"图表目录：{cfg.figures_dir}")

    print("\n高缺失 Top 5：")
    print(
        train_missing_zero.sort_values("missing_rate", ascending=False)[
            ["feature_name", "missing_rate"]
        ]
        .head(5)
        .to_string(index=False)
    )
    print("\n高零值 Top 5：")
    print(
        train_missing_zero.sort_values("zero_rate", ascending=False)[
            ["feature_name", "zero_rate"]
        ]
        .head(5)
        .to_string(index=False)
    )
    print("\npos/neg 缺失率差异 Top 5：")
    print(
        pos_neg_diff.sort_values("missing_rate_diff_abs", ascending=False)[
            ["feature_name", "missing_rate_diff_abs"]
        ]
        .head(5)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
