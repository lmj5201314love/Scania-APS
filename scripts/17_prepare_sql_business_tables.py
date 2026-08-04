"""Day 19：生成 MySQL 业务分析导入 CSV。

本脚本只读取已有 Day14/Day16/Day18 输出，整理为 MySQL Workbench 可手动导入的 CSV。
不连接 MySQL，不重新训练模型，不修改 data/raw/。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from scania_aps.config import get_config
from scania_aps.database.sql_business_export import (
    PolicyCosts,
    build_export_manifest,
    build_model_policy_comparison,
    build_model_prediction_results,
    build_threshold_sensitivity_results,
)


def read_optional_csv(path: Path) -> pd.DataFrame | None:
    """读取可选 CSV，文件不存在时返回 None。"""

    if not path.exists():
        print(f"[WARN] 可选文件不存在，已跳过：{path}")
        return None
    return pd.read_csv(path)


def main() -> None:
    """生成 Day19 SQL 导入 CSV。"""

    cfg = get_config(PROJECT_ROOT / "config" / "config.yaml")
    export_dir = cfg.project_root / "outputs" / "sql_exports"
    export_dir.mkdir(parents=True, exist_ok=True)

    day14_predictions_path = cfg.predictions_dir / "day14_structural_feature_test_predictions.csv"
    day14_metrics_path = cfg.metrics_dir / "day14_structural_feature_test_results.csv"
    day16_metrics_path = cfg.metrics_dir / "day16_xgb_tuning_test_results.csv"
    day18_oof_summary_path = cfg.metrics_dir / "day18_oof_ensemble_best_summary.csv"

    day14_predictions = pd.read_csv(day14_predictions_path)
    day14_metrics = pd.read_csv(day14_metrics_path)
    day16_metrics = read_optional_csv(day16_metrics_path)
    day18_oof_summary = read_optional_csv(day18_oof_summary_path)

    costs = PolicyCosts(
        fp_cost=int(cfg.false_positive_cost),
        fn_cost=int(cfg.false_negative_cost),
    )

    model_prediction_results = build_model_prediction_results(
        day14_predictions=day14_predictions,
        costs=costs,
        release_policy=cfg.release,
    )
    model_policy_comparison = build_model_policy_comparison(
        prediction_results=model_prediction_results,
        day14_metrics=day14_metrics,
        day16_metrics=day16_metrics,
        day18_oof_summary=day18_oof_summary,
        costs=costs,
        release_policy=cfg.release,
    )
    threshold_sensitivity_results = build_threshold_sensitivity_results(
        prediction_results=model_prediction_results,
        costs=costs,
    )

    prediction_path = export_dir / "model_prediction_results.csv"
    policy_path = export_dir / "model_policy_comparison.csv"
    threshold_path = export_dir / "threshold_sensitivity_results.csv"
    manifest_path = export_dir / "sql_export_manifest.csv"

    model_prediction_results.to_csv(prediction_path, index=False, encoding="utf-8-sig")
    model_policy_comparison.to_csv(policy_path, index=False, encoding="utf-8-sig")
    threshold_sensitivity_results.to_csv(threshold_path, index=False, encoding="utf-8-sig")

    manifest = build_export_manifest(
        [
            (
                prediction_path,
                "Day14 structural_all final candidate 的 official test 样本级预测结果。",
                "model_prediction_results",
            ),
            (
                policy_path,
                "naive baseline、Day14、Day16 和 Day18 OOF 的策略级成本对比。",
                "model_policy_comparison",
            ),
            (
                threshold_path,
                "基于 Day14 final candidate 风险分数的阈值敏感性分析结果。",
                "threshold_sensitivity_results",
            ),
        ]
    )
    manifest.to_csv(manifest_path, index=False, encoding="utf-8-sig")

    print("Day19 SQL 导入 CSV 已生成：")
    print(f"- {prediction_path} shape={model_prediction_results.shape}")
    print(f"- {policy_path} policies={model_policy_comparison['policy_name'].tolist()}")
    print(f"- {threshold_path} thresholds={len(threshold_sensitivity_results)}")
    print(f"- {manifest_path}")


if __name__ == "__main__":
    main()
