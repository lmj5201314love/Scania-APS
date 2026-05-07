"""运行 Day 6 阈值成本敏感性分析。"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from scania_aps.config import get_config
from scania_aps.evaluation.threshold_utils import (
    build_threshold_summary,
    evaluate_threshold_grid,
)


REQUIRED_PREDICTION_COLUMNS = {
    "y_true",
    "y_proba",
    "y_pred",
    "model_name",
    "strategy",
    "threshold",
}

FOCUS_MODELS = [
    ("logistic_regression_balanced", "drop_high_missing_median"),
    ("xgboost_scale_pos_weight", "drop_high_missing_median"),
    ("xgboost_scale_pos_weight", "median_all"),
]


def load_prediction_file(path: Path, source: str) -> pd.DataFrame:
    """读取预测结果，并做轻量列名校验。"""

    predictions = pd.read_csv(path)
    missing_cols = REQUIRED_PREDICTION_COLUMNS - set(predictions.columns)
    if missing_cols:
        raise ValueError(f"{path} 缺少必要列：{sorted(missing_cols)}")

    predictions = predictions.copy()
    predictions["source"] = source
    return predictions


def load_all_predictions(cfg) -> pd.DataFrame:
    """读取 Day 4 / Day 5 预测概率文件。"""

    prediction_files = [
        (cfg.predictions_dir / "day4_baseline_predictions.csv", "day4_baseline"),
        (cfg.predictions_dir / "day5_model_compare_predictions.csv", "day5_advanced"),
    ]
    parts = [load_prediction_file(path, source) for path, source in prediction_files]
    return pd.concat(parts, ignore_index=True)


def run_threshold_analysis(predictions: pd.DataFrame, cfg) -> pd.DataFrame:
    """对每个 model_name + strategy 执行阈值网格分析。"""

    threshold_results = []
    candidate_predictions = predictions[predictions["y_proba"].notna()].copy()

    for (model_name, strategy), group in candidate_predictions.groupby(
        ["model_name", "strategy"],
        dropna=False,
    ):
        result = evaluate_threshold_grid(
            y_true=group["y_true"],
            y_proba=group["y_proba"],
            cfg=cfg,
            model_name=model_name,
            strategy=strategy,
        )
        if not result.empty:
            threshold_results.append(result)

    if not threshold_results:
        return pd.DataFrame()

    return pd.concat(threshold_results, ignore_index=True)


def select_plot_data(threshold_metrics: pd.DataFrame) -> pd.DataFrame:
    """筛选重点模型用于画图，避免曲线过密。"""

    focus_parts = []
    for model_name, strategy in FOCUS_MODELS:
        part = threshold_metrics[
            threshold_metrics["model_name"].eq(model_name)
            & threshold_metrics["strategy"].eq(strategy)
        ]
        if not part.empty:
            focus_parts.append(part)

    if focus_parts:
        return pd.concat(focus_parts, ignore_index=True)

    best_pairs = (
        build_threshold_summary(threshold_metrics)
        .head(5)[["model_name", "strategy"]]
        .drop_duplicates()
    )
    return threshold_metrics.merge(best_pairs, on=["model_name", "strategy"], how="inner")


def _series_label(row: pd.Series) -> str:
    """生成图例标签。"""

    return f"{row['model_name']} | {row['strategy']}"


def plot_threshold_cost_curve(plot_data: pd.DataFrame, output_path: Path) -> None:
    """绘制 threshold vs total_cost 曲线。"""

    plt.figure(figsize=(10, 6))
    for _, group in plot_data.groupby(["model_name", "strategy"]):
        first_row = group.iloc[0]
        plt.plot(group["threshold"], group["total_cost"], label=_series_label(first_row))
    plt.title("Day 6 threshold vs total cost")
    plt.xlabel("Threshold")
    plt.ylabel("Total cost")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def plot_precision_recall_curve(plot_data: pd.DataFrame, output_path: Path) -> None:
    """绘制 threshold 与 precision / recall 的关系。"""

    plt.figure(figsize=(10, 6))
    for _, group in plot_data.groupby(["model_name", "strategy"]):
        first_row = group.iloc[0]
        label = _series_label(first_row)
        plt.plot(group["threshold"], group["precision"], linestyle="--", label=f"{label} precision")
        plt.plot(group["threshold"], group["recall"], linestyle="-", label=f"{label} recall")
    plt.title("Day 6 threshold vs precision / recall")
    plt.xlabel("Threshold")
    plt.ylabel("Metric value")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def plot_threshold_f2_curve(plot_data: pd.DataFrame, output_path: Path) -> None:
    """绘制 threshold vs F2 曲线。"""

    plt.figure(figsize=(10, 6))
    for _, group in plot_data.groupby(["model_name", "strategy"]):
        first_row = group.iloc[0]
        plt.plot(group["threshold"], group["f2"], label=_series_label(first_row))
    plt.title("Day 6 threshold vs F2")
    plt.xlabel("Threshold")
    plt.ylabel("F2")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def main() -> None:
    """读取预测概率并执行 Day 6 阈值分析。"""

    cfg = get_config(PROJECT_ROOT / "config" / "config.yaml")
    cfg.metrics_dir.mkdir(parents=True, exist_ok=True)
    cfg.figures_dir.mkdir(parents=True, exist_ok=True)

    predictions = load_all_predictions(cfg)
    threshold_metrics = run_threshold_analysis(predictions, cfg)
    best_summary = build_threshold_summary(threshold_metrics)

    threshold_metrics_path = cfg.metrics_dir / "day6_threshold_metrics.csv"
    best_summary_path = cfg.metrics_dir / "day6_best_threshold_summary.csv"
    threshold_metrics.to_csv(threshold_metrics_path, index=False, encoding="utf-8-sig")
    best_summary.to_csv(best_summary_path, index=False, encoding="utf-8-sig")

    plot_data = select_plot_data(threshold_metrics)
    plot_threshold_cost_curve(plot_data, cfg.figures_dir / "day6_threshold_cost_curve.png")
    plot_precision_recall_curve(
        plot_data,
        cfg.figures_dir / "day6_threshold_precision_recall_curve.png",
    )
    plot_threshold_f2_curve(plot_data, cfg.figures_dir / "day6_threshold_f2_curve.png")

    print("Day 6 阈值成本敏感性分析已完成。")
    print(f"完整阈值结果：{threshold_metrics_path}")
    print(f"低成本阈值摘要：{best_summary_path}")
    print(
        best_summary[
            [
                "model_name",
                "strategy",
                "best_threshold",
                "precision",
                "recall",
                "f2",
                "fn",
                "fp",
                "total_cost",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
