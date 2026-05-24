"""Day 19 SQL 业务导出逻辑测试。"""

from __future__ import annotations

import pandas as pd

from scania_aps.database.sql_business_export import (
    PolicyCosts,
    build_model_policy_comparison,
    build_model_prediction_results,
    build_threshold_sensitivity_results,
)


def test_build_model_prediction_results_schema_and_costs() -> None:
    """统一预测结果表应包含 SQL 导入所需字段，并正确计算成本。"""

    predictions = pd.DataFrame(
        {
            "dataset": ["official_test"] * 4,
            "sample_id": [1, 2, 3, 4],
            "y_true": [1, 0, 0, 1],
            "y_proba": [0.95, 0.70, 0.03, 0.10],
            "strategy": ["median_all_structural_all"] * 4,
            "candidate_group": ["median_all_structural_all"] * 4,
            "threshold": [0.18] * 4,
        }
    )
    result = build_model_prediction_results(
        day14_predictions=predictions,
        costs=PolicyCosts(fp_cost=10, fn_cost=500),
    )

    required_columns = {
        "sample_id",
        "dataset",
        "model_version",
        "strategy",
        "threshold",
        "y_true",
        "y_proba",
        "y_pred",
        "risk_level",
        "suggested_action",
        "confusion_type",
        "fp_cost",
        "fn_cost",
        "sample_cost",
        "probability_band",
        "decile",
    }
    assert required_columns.issubset(result.columns)
    assert result.loc[result["sample_id"].eq(2), "confusion_type"].iloc[0] == "FP"
    assert result.loc[result["sample_id"].eq(4), "confusion_type"].iloc[0] == "FN"
    assert result.loc[result["sample_id"].eq(2), "sample_cost"].iloc[0] == 10
    assert result.loc[result["sample_id"].eq(4), "sample_cost"].iloc[0] == 500
    assert result["risk_level"].tolist() == ["Critical", "High", "Low", "Medium"]
    assert result["probability_band"].notna().all()
    assert result["decile"].between(1, 10).all()


def test_build_model_policy_comparison_contains_naive_and_final() -> None:
    """策略对比表至少应包含 naive baseline 和 final candidate。"""

    prediction_results = pd.DataFrame(
        {
            "y_true": [1, 0, 1, 0],
            "y_proba": [0.9, 0.8, 0.1, 0.01],
            "y_pred": [1, 1, 0, 0],
        }
    )
    day14_metrics = pd.DataFrame(
        {
            "strategy": ["median_all_structural_all"],
            "threshold": [0.18],
            "fp": [1],
            "fn": [1],
            "tp": [1],
            "tn": [1],
            "total_cost": [510],
        }
    )

    comparison = build_model_policy_comparison(
        prediction_results=prediction_results,
        day14_metrics=day14_metrics,
        day16_metrics=None,
        day18_oof_summary=None,
        costs=PolicyCosts(fp_cost=10, fn_cost=500),
    )

    required_columns = {
        "policy_name",
        "dataset",
        "fp",
        "fn",
        "fp_cost_total",
        "fn_cost_total",
        "total_cost",
        "cost_reduction",
        "cost_reduction_rate",
    }
    assert required_columns.issubset(comparison.columns)
    assert {"naive_all_negative", "day14_structural_all_final_candidate"}.issubset(
        set(comparison["policy_name"])
    )


def test_build_threshold_sensitivity_results_schema() -> None:
    """阈值敏感性表应包含 SQL 友好的指标列名。"""

    prediction_results = pd.DataFrame(
        {
            "y_true": [1, 0, 1, 0],
            "y_proba": [0.9, 0.8, 0.1, 0.01],
        }
    )
    result = build_threshold_sensitivity_results(
        prediction_results=prediction_results,
        costs=PolicyCosts(fp_cost=10, fn_cost=500),
        thresholds=pd.Series([0.10, 0.50]).to_numpy(),
    )

    required_columns = {
        "threshold",
        "tp",
        "fp",
        "tn",
        "fn",
        "precision_score",
        "recall_score",
        "f2_score",
        "total_cost",
    }
    assert required_columns.issubset(result.columns)
    assert len(result) == 2
