"""生成 Day 7 风险分层和维修优先级 CSV。

"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from scania_aps.config import get_config
from scania_aps.evaluation.metrics import evaluate_binary_classifier
from scania_aps.evaluation.risk_utils import (
    ACTION_MAPPING,
    RISK_LEVEL_ORDER,
    build_maintenance_priority_table,
)


MODEL_NAME = "xgboost_scale_pos_weight"
STRATEGY = "median_all"


def load_best_threshold(cfg) -> float:
    """读取 Day 6 推荐组合的低成本阈值。"""

    summary_path = cfg.metrics_dir / "day6_best_threshold_summary.csv"
    summary = pd.read_csv(summary_path)
    row = summary[
        summary["model_name"].eq(MODEL_NAME)
        & summary["strategy"].eq(STRATEGY)
    ]
    if row.empty:
        raise ValueError(f"未在 {summary_path} 中找到 {MODEL_NAME} + {STRATEGY}。")
    return float(row.iloc[0]["best_threshold"])


def load_selected_predictions(cfg) -> pd.DataFrame:
    """读取 Day 5 predictions 并筛选 XGBoost + median_all。"""

    predictions_path = cfg.predictions_dir / "day5_model_compare_predictions.csv"
    predictions = pd.read_csv(predictions_path)
    selected = predictions[
        predictions["model_name"].eq(MODEL_NAME)
        & predictions["strategy"].eq(STRATEGY)
    ].copy()
    if selected.empty:
        raise ValueError(f"未在 {predictions_path} 中找到 {MODEL_NAME} + {STRATEGY}。")
    return selected


def build_risk_level_summary(priority_table: pd.DataFrame) -> pd.DataFrame:
    """按风险等级汇总维修工作量和实际故障情况。"""

    rows = []
    for risk_level in RISK_LEVEL_ORDER:
        group = priority_table[priority_table["risk_level"].eq(risk_level)]
        type_counts = group["prediction_type"].value_counts()
        rows.append(
            {
                "risk_level": risk_level,
                "sample_count": len(group),
                "actual_pos_count": int(group["y_true"].sum()),
                "predicted_pos_count": int(group["y_pred"].sum()),
                "tp": int(type_counts.get("TP", 0)),
                "fp": int(type_counts.get("FP", 0)),
                "fn": int(type_counts.get("FN", 0)),
                "tn": int(type_counts.get("TN", 0)),
                "avg_y_proba": float(group["y_proba"].mean()) if len(group) else 0.0,
                "suggested_action": ACTION_MAPPING[risk_level],
            }
        )

    return pd.DataFrame(rows)


def build_business_result_summary(priority_table: pd.DataFrame, cfg) -> pd.DataFrame:
    """汇总当前方案相对 naive baseline 的成本下降。"""

    metric = evaluate_binary_classifier(
        y_true=priority_table["y_true"],
        y_pred=priority_table["y_pred"],
        y_proba=priority_table["y_proba"],
        cfg=cfg,
        model_name=MODEL_NAME,
        strategy=STRATEGY,
        threshold=float(priority_table["threshold"].iloc[0]),
    )
    positive_count = int(priority_table["y_true"].sum())
    baseline_total_cost = positive_count * cfg.false_negative_cost
    total_cost = metric["total_cost"]
    cost_reduction = baseline_total_cost - total_cost

    return pd.DataFrame(
        [
            {
                "solution_name": f"{MODEL_NAME}_{STRATEGY}_threshold_{metric['threshold']:.2f}",
                "threshold": metric["threshold"],
                "precision": metric["precision"],
                "recall": metric["recall"],
                "f2": metric["f2"],
                "fp": metric["fp"],
                "fn": metric["fn"],
                "total_cost": total_cost,
                "baseline_total_cost": baseline_total_cost,
                "cost_reduction": cost_reduction,
                "cost_reduction_rate": cost_reduction / baseline_total_cost,
            }
        ]
    )


def main() -> None:
    """生成 Day 7 风险分层和业务汇总表。"""

    cfg = get_config(PROJECT_ROOT / "config" / "config.yaml")
    cfg.tables_dir.mkdir(parents=True, exist_ok=True)

    best_threshold = load_best_threshold(cfg)
    selected_predictions = load_selected_predictions(cfg)
    priority_table = build_maintenance_priority_table(
        predictions_df=selected_predictions,
        best_threshold=best_threshold,
        model_name=MODEL_NAME,
        strategy=STRATEGY,
    )
    risk_summary = build_risk_level_summary(priority_table)
    business_summary = build_business_result_summary(priority_table, cfg)

    priority_path = cfg.tables_dir / "day7_maintenance_priority_list.csv"
    risk_summary_path = cfg.tables_dir / "day7_risk_level_summary.csv"
    business_summary_path = cfg.tables_dir / "day7_business_result_summary.csv"

    priority_table.to_csv(priority_path, index=False, encoding="utf-8-sig")
    risk_summary.to_csv(risk_summary_path, index=False, encoding="utf-8-sig")
    business_summary.to_csv(business_summary_path, index=False, encoding="utf-8-sig")

    print("Day 7 风险分层和维修优先级表已生成。")
    print(f"维修优先级清单：{priority_path}")
    print(f"风险等级汇总：{risk_summary_path}")
    print(f"业务结果汇总：{business_summary_path}")
    print(business_summary.to_string(index=False))


if __name__ == "__main__":
    main()
