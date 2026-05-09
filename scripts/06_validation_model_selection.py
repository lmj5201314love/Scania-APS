"""运行 validation-based model selection 增强流程。"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

import pandas as pd

from scania_aps.config import get_config
from scania_aps.data.load_data import load_train_test_with_target
from scania_aps.data.split_data import save_split_indices, split_train_valid
from scania_aps.models.validation_selection import run_validation_model_selection


def _build_split_summary(train_df: pd.DataFrame, train_inner_df: pd.DataFrame, valid_df: pd.DataFrame) -> pd.DataFrame:
    """整理 train_inner / valid 划分摘要。"""

    rows = []
    for dataset_name, df in [
        ("official_train", train_df),
        ("train_inner", train_inner_df),
        ("valid", valid_df),
    ]:
        pos_count = int(df["target"].sum())
        rows.append(
            {
                "dataset": dataset_name,
                "row_count": len(df),
                "pos_count": pos_count,
                "neg_count": len(df) - pos_count,
                "pos_rate": pos_count / len(df),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    """读取配置、划分 valid、训练候选模型，并在官方 test 上做最终评估。"""

    cfg = get_config(PROJECT_ROOT / "config" / "config.yaml")
    cfg.metrics_dir.mkdir(parents=True, exist_ok=True)
    cfg.predictions_dir.mkdir(parents=True, exist_ok=True)
    cfg.tables_dir.mkdir(parents=True, exist_ok=True)

    train_df, test_df = load_train_test_with_target(cfg)
    train_inner_df, valid_df = split_train_valid(train_df, cfg)
    save_split_indices(train_inner_df, valid_df, cfg)

    split_summary = _build_split_summary(train_df, train_inner_df, valid_df)
    split_summary_path = cfg.tables_dir / "validation_split_summary.csv"
    split_summary.to_csv(split_summary_path, index=False, encoding="utf-8-sig")

    results = run_validation_model_selection(
        train_inner_df=train_inner_df,
        valid_df=valid_df,
        test_df=test_df,
        cfg=cfg,
        day6_best_summary_path=cfg.metrics_dir / "day6_best_threshold_summary.csv",
        strategies=["median_all", "drop_high_missing_median"],
        model_names=["logistic_regression_balanced", "xgboost_scale_pos_weight"],
    )

    output_map = {
        "validation_threshold_metrics": cfg.metrics_dir / "validation_threshold_metrics.csv",
        "validation_best_summary": cfg.metrics_dir / "validation_best_threshold_summary.csv",
        "final_test_evaluation": cfg.metrics_dir / "final_test_evaluation_from_valid_selection.csv",
        "comparison_with_day6_backtest": cfg.metrics_dir / "validation_vs_day6_backtest_compare.csv",
        "validation_predictions": cfg.predictions_dir / "validation_predictions.csv",
        "final_test_predictions": cfg.predictions_dir / "final_test_predictions_from_valid_selection.csv",
    }

    for key, path in output_map.items():
        results[key].to_csv(path, index=False, encoding="utf-8-sig")

    best = results["validation_best_summary"].iloc[0]
    final = results["final_test_evaluation"].iloc[0]
    compare = results["comparison_with_day6_backtest"]

    print("Validation-based model selection 已完成。")
    print(f"划分摘要：{split_summary_path}")
    for path in output_map.values():
        print(f"输出：{path}")
    print("\nvalid 最优组合：")
    print(
        best[
            [
                "model_name",
                "strategy",
                "best_threshold",
                "precision",
                "recall",
                "f2",
                "total_cost",
            ]
        ].to_string()
    )
    print("\nofficial test 最终评估：")
    print(
        final[
            [
                "model_name",
                "strategy",
                "threshold",
                "precision",
                "recall",
                "f2",
                "fp",
                "fn",
                "total_cost",
            ]
        ].to_string()
    )
    print("\n与 Day 6 test 回溯最优对比：")
    print(compare.to_string(index=False))


if __name__ == "__main__":
    main()
