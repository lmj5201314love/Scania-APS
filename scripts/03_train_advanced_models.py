"""运行 Day 5 提升模型对比脚本。"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from scania_aps.config import get_config
from scania_aps.data.load_data import load_train_test_with_target
from scania_aps.models.train_advanced import train_and_evaluate_advanced_models


def main() -> None:
    """读取配置、训练提升模型，并保存本地运行结果。"""

    cfg = get_config(PROJECT_ROOT / "config" / "config.yaml")
    cfg.metrics_dir.mkdir(parents=True, exist_ok=True)
    cfg.predictions_dir.mkdir(parents=True, exist_ok=True)

    train_df, test_df = load_train_test_with_target(cfg)
    strategies = ["median_all", "drop_high_missing_median", "median_with_indicator"]

    metrics_df, predictions_df = train_and_evaluate_advanced_models(
        train_df=train_df,
        test_df=test_df,
        cfg=cfg,
        strategies=strategies,
    )

    metrics_path = cfg.metrics_dir / "day5_model_compare_metrics.csv"
    predictions_path = cfg.predictions_dir / "day5_model_compare_predictions.csv"
    metrics_df.to_csv(metrics_path, index=False, encoding="utf-8-sig")
    predictions_df.to_csv(predictions_path, index=False, encoding="utf-8-sig")

    print("Day 5 提升模型对比已完成。")
    print(f"指标输出：{metrics_path}")
    print(f"预测输出：{predictions_path}")
    print(
        metrics_df[
            [
                "model_name",
                "strategy",
                "precision",
                "recall",
                "f2",
                "average_precision",
                "total_cost",
            ]
        ]
        .sort_values("total_cost")
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
