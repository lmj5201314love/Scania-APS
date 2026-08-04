"""Day 19 SQL 业务导出逻辑测试。"""

from __future__ import annotations

import pandas as pd
import pytest

from scania_aps.config import ReleasePolicy
from scania_aps.database.sql_business_export import (
    PolicyCosts,
    build_model_policy_comparison,
    build_model_prediction_results,
    build_threshold_sensitivity_results,
)


def _release_policy(
    *,
    strategy: str = "median_all_structural_all",
    decision_threshold: float = 0.18,
    model_version: str = "day14_structural_all_final_candidate",
) -> ReleasePolicy:
    return ReleasePolicy(
        target_version="1.0.0",
        stage="v1_0_release_candidate",
        model_version=model_version,
        model_name="xgboost_scale_pos_weight",
        strategy=strategy,
        decision_threshold=decision_threshold,
        threshold_source="day13_valid_best_summary",
        score_semantics="uncalibrated_risk_score",
        fit_dataset="train_inner",
        fit_rows=48000,
        validation_dataset="valid",
        validation_rows=12000,
        evaluation_dataset="official_test",
        evaluation_rows=16000,
    )


def test_build_model_prediction_results_schema_and_costs() -> None:
    """统一预测结果表应包含 SQL 导入所需字段，并正确计算成本。"""

    predictions = pd.DataFrame(
        {
            "dataset": ["official_test"] * 6,
            "sample_id": [1, 2, 3, 4, 5, 6],
            "y_true": [1, 0, 0, 1, 0, 1],
            "y_proba": [0.95, 0.70, 0.03, 0.10, 0.18, 0.179999],
            "strategy": ["median_all_structural_all"] * 6,
            "candidate_group": ["median_all_structural_all"] * 6,
            "threshold": [0.18] * 6,
        }
    )
    release_policy = _release_policy()
    result = build_model_prediction_results(
        day14_predictions=predictions,
        costs=PolicyCosts(fp_cost=10, fn_cost=500),
        release_policy=release_policy,
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
    assert result["model_version"].eq(release_policy.model_version).all()
    assert result["strategy"].eq(release_policy.strategy).all()
    assert result["threshold"].eq(release_policy.decision_threshold).all()
    assert result["risk_level"].tolist() == [
        "Critical",
        "High",
        "Low",
        "Medium",
        "High",
        "Medium",
    ]
    assert result.loc[result["sample_id"].eq(5), "suggested_action"].iloc[0] == (
        "priority_aps_inspection"
    )
    assert not result.loc[result["risk_level"].isin(["Medium", "Low"]), "y_pred"].any()
    assert result["probability_band"].notna().all()
    assert result["decile"].between(1, 10).all()


@pytest.mark.parametrize(
    ("strategy", "threshold"),
    [
        ("median_all_structural_all_variant", 0.18),
        ("median_all_structural_all", 0.1801),
        ("structural_all", 0.18),
    ],
)
def test_prediction_export_rejects_non_exact_release_candidate(
    strategy: str,
    threshold: float,
) -> None:
    """相似策略、近似阈值和 structural fallback 均不得冒充最终候选。"""

    predictions = pd.DataFrame(
        {
            "candidate_group": [strategy],
            "threshold": [threshold],
            "y_true": [1],
            "y_proba": [0.9],
        }
    )

    with pytest.raises(ValueError, match="release policy.*精确匹配|精确匹配.*release policy"):
        build_model_prediction_results(
            day14_predictions=predictions,
            costs=PolicyCosts(fp_cost=10, fn_cost=500),
            release_policy=_release_policy(),
        )


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

    release_policy = _release_policy()
    comparison = build_model_policy_comparison(
        prediction_results=prediction_results,
        day14_metrics=day14_metrics,
        day16_metrics=None,
        day18_oof_summary=None,
        costs=PolicyCosts(fp_cost=10, fn_cost=500),
        release_policy=release_policy,
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
    assert {"naive_all_negative", release_policy.model_version}.issubset(
        set(comparison["policy_name"])
    )
    final_row = comparison.loc[comparison["policy_name"].eq(release_policy.model_version)].iloc[0]
    assert final_row["threshold"] == release_policy.decision_threshold
    assert str(release_policy.decision_threshold) in final_row["note"]


@pytest.mark.parametrize(
    ("strategy", "threshold"),
    [
        ("median_all_structural_all_variant", 0.18),
        ("median_all_structural_all", 0.1801),
    ],
)
def test_policy_comparison_rejects_non_exact_final_metrics(
    strategy: str,
    threshold: float,
) -> None:
    """策略对比不得用相似名称或近似阈值冒充最终候选。"""

    prediction_results = pd.DataFrame(
        {
            "y_true": [1, 0],
            "y_proba": [0.9, 0.1],
            "y_pred": [1, 0],
        }
    )
    day14_metrics = pd.DataFrame(
        {
            "strategy": [strategy],
            "threshold": [threshold],
            "fp": [0],
            "fn": [0],
            "tp": [1],
            "tn": [1],
            "total_cost": [0],
        }
    )

    with pytest.raises(ValueError, match="release policy.*精确匹配|精确匹配.*release policy"):
        build_model_policy_comparison(
            prediction_results=prediction_results,
            day14_metrics=day14_metrics,
            day16_metrics=None,
            day18_oof_summary=None,
            costs=PolicyCosts(fp_cost=10, fn_cost=500),
            release_policy=_release_policy(),
        )


def test_policy_comparison_rejects_ambiguous_final_metrics() -> None:
    """最终策略和阈值匹配多行时必须失败，不能静默取第一行。"""

    prediction_results = pd.DataFrame(
        {
            "y_true": [1, 0],
            "y_proba": [0.9, 0.1],
            "y_pred": [1, 0],
        }
    )
    day14_metrics = pd.DataFrame(
        {
            "strategy": ["median_all_structural_all"] * 2,
            "threshold": [0.18, 0.18],
            "fp": [0, 1],
            "fn": [0, 0],
            "tp": [1, 1],
            "tn": [1, 0],
            "total_cost": [0, 10],
        }
    )

    with pytest.raises(ValueError, match="仅匹配一行|唯一"):
        build_model_policy_comparison(
            prediction_results=prediction_results,
            day14_metrics=day14_metrics,
            day16_metrics=None,
            day18_oof_summary=None,
            costs=PolicyCosts(fp_cost=10, fn_cost=500),
            release_policy=_release_policy(),
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
