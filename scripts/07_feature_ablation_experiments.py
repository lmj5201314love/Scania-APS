"""运行缺失值与特征工程消融实验。"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from scania_aps.config import get_config
from scania_aps.data.load_data import load_train_test_with_target
from scania_aps.data.split_data import split_train_valid
from scania_aps.models.feature_ablation import run_feature_ablation_experiments


def main() -> None:
    """读取数据、运行消融实验，并保存本地输出。"""

    cfg = get_config(PROJECT_ROOT / "config" / "config.yaml")
    cfg.metrics_dir.mkdir(parents=True, exist_ok=True)
    cfg.tables_dir.mkdir(parents=True, exist_ok=True)

    train_df, test_df = load_train_test_with_target(cfg)
    train_inner_df, valid_df = split_train_valid(train_df, cfg)
    strategies = cfg.feature_ablation["enable_strategies"]

    results = run_feature_ablation_experiments(
        train_inner_df=train_inner_df,
        valid_df=valid_df,
        test_df=test_df,
        cfg=cfg,
        strategies=strategies,
        model_names=["logistic_regression_balanced", "xgboost_scale_pos_weight"],
    )

    output_map = {
        "valid_threshold_metrics": cfg.metrics_dir / "feature_ablation_valid_threshold_metrics.csv",
        "valid_best_summary": cfg.metrics_dir / "feature_ablation_valid_best_summary.csv",
        "final_test_results": cfg.metrics_dir / "feature_ablation_final_test_results.csv",
        "strategy_metadata": cfg.tables_dir / "feature_ablation_strategy_metadata.csv",
        "missing_indicator_signal_summary": cfg.tables_dir / "missing_indicator_signal_summary.csv",
    }

    for key, path in output_map.items():
        results[key].to_csv(path, index=False, encoding="utf-8-sig")

    best_valid = results["valid_best_summary"].iloc[0]
    best_test = results["final_test_results"].iloc[0]

    print("Feature ablation experiments 已完成。")
    for path in output_map.values():
        print(f"输出：{path}")

    print("\nvalid 上按 total_cost 排名第一：")
    print(
        best_valid[
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

    print("\nofficial test 上按 total_cost 排名第一：")
    print(
        best_test[
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

    print("\n前 10 个 official test 结果：")
    print(
        results["final_test_results"][
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
        ]
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
