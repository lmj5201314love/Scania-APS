from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd
import pytest

from scania_aps.config import ReleasePolicy
from scania_aps.database.sql_business_export import (
    PolicyCosts,
    build_model_prediction_results,
)
from scania_aps.evaluation.risk_utils import RISK_LEVEL_ORDER


def _load_script_module(script_name: str, module_name: str):
    script_path = Path(__file__).resolve().parents[1] / "scripts" / script_name
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_day19_module():
    return _load_script_module(
        "17_prepare_sql_business_tables.py",
        "day19_sql_business_tables",
    )


def _load_day20_module():
    return _load_script_module(
        "18_generate_business_insight_figures.py",
        "day20_business_insights",
    )


def _mock_predictions() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "sample_id": range(1, 11),
            "dataset": ["official_test"] * 10,
            "model_version": ["mock"] * 10,
            "strategy": ["mock_strategy"] * 10,
            "threshold": [0.18] * 10,
            "y_true": [1, 1, 0, 0, 1, 0, 0, 1, 0, 0],
            "y_proba": [0.95, 0.80, 0.70, 0.60, 0.40, 0.30, 0.20, 0.10, 0.05, 0.01],
            "y_pred": [1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
            "risk_level": [
                "Critical",
                "Critical",
                "High",
                "High",
                "High",
                "High",
                "High",
                "Medium",
                "Medium",
                "Low",
            ],
            "suggested_action": [
                "immediate_aps_inspection",
                "immediate_aps_inspection",
                "priority_aps_inspection",
                "priority_aps_inspection",
                "priority_aps_inspection",
                "priority_aps_inspection",
                "priority_aps_inspection",
                "aps_recheck_or_additional_diagnosis",
                "aps_recheck_or_additional_diagnosis",
                "continue_non_aps_diagnosis",
            ],
            "confusion_type": ["TP", "TP", "FP", "FP", "TP", "FP", "FP", "FN", "TN", "TN"],
            "fp_cost": [10] * 10,
            "fn_cost": [500] * 10,
            "sample_cost": [0, 0, 10, 10, 0, 10, 10, 500, 0, 0],
            "probability_band": [
                "[0.90,1.00]",
                "[0.80,0.90)",
                "[0.70,0.80)",
                "[0.60,0.70)",
                "[0.40,0.50)",
                "[0.30,0.40)",
                "[0.20,0.30)",
                "[0.10,0.20)",
                "[0.05,0.10)",
                "[0.00,0.05)",
            ],
            "decile": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5],
            "created_at": ["2026-05-24"] * 10,
        }
    )


def _mock_thresholds() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "threshold": [0.05, 0.18, 0.30],
            "predicted_positive_count": [8, 7, 5],
            "predicted_negative_count": [2, 3, 5],
            "tp": [4, 3, 3],
            "fp": [4, 4, 2],
            "tn": [2, 2, 4],
            "fn": [0, 1, 1],
            "precision_score": [0.50, 0.43, 0.60],
            "recall_score": [1.00, 0.75, 0.75],
            "f1_score": [0.67, 0.55, 0.67],
            "f2_score": [0.83, 0.65, 0.71],
            "fp_cost": [10, 10, 10],
            "fn_cost": [500, 500, 500],
            "total_cost": [40, 540, 520],
            "workload_rate": [0.8, 0.7, 0.5],
        }
    )


def _mock_policies() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "policy_name": [
                "day18_oof_ensemble_best",
                "day14_structural_all_final_candidate",
                "naive_all_negative",
                "day14_baseline_median_all",
                "day16_tuned_best",
            ],
            "dataset": ["oof_train", "official_test", "official_test", "official_test", "official_test"],
            "threshold": [0.14, 0.18, None, 0.16, 0.19],
            "fp": [20, 4, 0, 5, 3],
            "fn": [2, 1, 4, 2, 2],
            "fp_cost_total": [200, 40, 0, 50, 30],
            "fn_cost_total": [1000, 500, 2000, 1000, 1000],
            "total_cost": [1200, 540, 2000, 1050, 1030],
            "cost_reduction": [800, 1460, 0, 950, 970],
            "cost_reduction_rate": [0.40, 0.73, 0.0, 0.475, 0.485],
            "note": ["OOF row", "final", "naive", "baseline", "tuned"],
        }
    )


def _release_policy(
    *,
    model_version: str = "day14_structural_all_final_candidate",
    strategy: str = "median_all_structural_all",
    evaluation_rows: int = 16000,
) -> ReleasePolicy:
    return ReleasePolicy(
        target_version="1.0.0",
        stage="v1_0_release_candidate",
        model_version=model_version,
        model_name="xgboost_scale_pos_weight",
        strategy=strategy,
        decision_threshold=0.18,
        threshold_source="day13_valid_best_summary",
        score_semantics="uncalibrated_risk_score",
        fit_dataset="train_inner",
        fit_rows=48000,
        validation_dataset="valid",
        validation_rows=12000,
        evaluation_dataset="official_test",
        evaluation_rows=evaluation_rows,
    )


def test_topk_table_has_required_columns() -> None:
    module = _load_day20_module()

    table = module.build_topk_maintenance_capacity(
        _mock_predictions(),
        fn_cost=500,
        top_k_values=[2, 5],
    )

    required = {
        "top_k",
        "inspected_count",
        "actual_pos_count",
        "precision_at_k",
        "recall_at_k",
        "missed_pos_count",
    }
    assert required.issubset(table.columns)
    assert table.loc[table["top_k"] == 2, "actual_pos_count"].iloc[0] == 2
    assert table["estimated_workload"].eq(table["inspected_count"]).all()


def test_risk_workload_table_has_required_columns() -> None:
    module = _load_day20_module()

    table = module.build_risk_workload_summary(_mock_predictions())

    required = {
        "risk_level",
        "tier_population",
        "actual_pos_count",
        "predicted_pos_count",
        "actual_pos_rate",
        "predicted_pos_rate",
        "avg_risk_score",
        "aps_inspection_queue_count",
        "recheck_queue_count",
    }
    assert required.issubset(table.columns)
    assert "avg_predicted_probability" not in table.columns
    assert "estimated_workload" not in table.columns
    assert table["priority_order"].tolist() == sorted(table["priority_order"].tolist())
    by_tier = table.set_index("risk_level")
    assert by_tier["tier_population"].to_dict() == {
        "Critical": 2,
        "High": 5,
        "Medium": 2,
        "Low": 1,
    }
    assert by_tier["aps_inspection_queue_count"].to_dict() == {
        "Critical": 2,
        "High": 5,
        "Medium": 0,
        "Low": 0,
    }
    assert by_tier["recheck_queue_count"].to_dict() == {
        "Critical": 0,
        "High": 0,
        "Medium": 2,
        "Low": 0,
    }


def test_business_summaries_use_the_central_risk_order() -> None:
    """业务汇总脚本必须复用风险工具中的唯一等级顺序。"""

    module = _load_day20_module()

    assert module.RISK_LEVEL_ORDER is RISK_LEVEL_ORDER


def test_risk_policy_flows_from_sql_export_to_workload_summary() -> None:
    """风险工具生成的等级和动作应原样驱动业务人口及队列汇总。"""

    module = _load_day20_module()
    source_predictions = pd.DataFrame(
        {
            "dataset": ["official_test"] * 4,
            "sample_id": [1, 2, 3, 4],
            "model_name": ["xgboost_scale_pos_weight"] * 4,
            "strategy": ["median_all_structural_all"] * 4,
            "candidate_group": ["median_all_structural_all"] * 4,
            "threshold": [0.18] * 4,
            "threshold_source": ["day13_valid_best_summary"] * 4,
            "y_true": [1, 0, 1, 0],
            "y_proba": [0.90, 0.50, 0.10, 0.01],
        }
    )
    exported_predictions = build_model_prediction_results(
        day14_predictions=source_predictions,
        costs=PolicyCosts(fp_cost=10, fn_cost=500),
        release_policy=_release_policy(evaluation_rows=4),
        created_at="2026-08-04 00:00:00",
    )

    workload = module.build_risk_workload_summary(exported_predictions)
    by_tier = workload.set_index("risk_level")

    assert by_tier["tier_population"].to_dict() == {
        "Critical": 1,
        "High": 1,
        "Medium": 1,
        "Low": 1,
    }
    assert by_tier["aps_inspection_queue_count"].to_dict() == {
        "Critical": 1,
        "High": 1,
        "Medium": 0,
        "Low": 0,
    }
    assert by_tier["recheck_queue_count"].to_dict() == {
        "Critical": 0,
        "High": 0,
        "Medium": 1,
        "Low": 0,
    }


def test_decile_lift_gain_table_has_lift() -> None:
    module = _load_day20_module()

    table = module.build_decile_lift_gain_summary(_mock_predictions())

    required = {
        "decile",
        "sample_count",
        "actual_pos_count",
        "pos_rate",
        "cumulative_recall",
        "lift",
    }
    assert required.issubset(table.columns)
    assert table.loc[table["decile"] == 1, "lift"].iloc[0] > 1.0


def test_threshold_highlights_use_explicit_final_threshold() -> None:
    module = _load_day20_module()
    threshold_summary = module.build_threshold_sensitivity_summary(_mock_thresholds())

    highlights = module.build_threshold_policy_highlights(
        threshold_summary,
        final_threshold=0.18,
    )

    required = {"policy_rule", "threshold", "fp", "fn", "recall", "total_cost"}
    assert required.issubset(highlights.columns)
    assert "final_threshold" in set(highlights["policy_rule"])
    final_row = highlights.loc[highlights["policy_rule"] == "final_threshold"].iloc[0]
    assert final_row["threshold"] == 0.18


def test_threshold_highlights_reject_missing_final_threshold() -> None:
    """敏感性表缺少冻结阈值时不得用最近的阈值代替。"""

    module = _load_day20_module()
    thresholds = _mock_thresholds().loc[lambda df: df["threshold"].ne(0.18)]
    threshold_summary = module.build_threshold_sensitivity_summary(thresholds)

    with pytest.raises(
        ValueError,
        match="final_threshold.*精确匹配|精确匹配.*final_threshold",
    ):
        module.build_threshold_policy_highlights(
            threshold_summary,
            final_threshold=0.18,
        )


def test_policy_comparison_keeps_oof_separate_from_official_test() -> None:
    module = _load_day20_module()

    table = module.build_policy_cost_comparison(
        _mock_policies(),
        release_policy=_release_policy(),
    )

    official_positions = table.index[table["dataset"].eq("official_test")].tolist()
    oof_positions = table.index[table["dataset"].eq("oof_train")].tolist()
    assert max(official_positions) < min(oof_positions)
    oof_note = table.loc[table["dataset"].eq("oof_train"), "note"].iloc[0]
    assert "不可与 official test" in oof_note


def test_business_report_uses_release_policy_metadata() -> None:
    """业务表和报告应从完整发布政策读取 final candidate 元数据。"""

    module = _load_day20_module()
    release_policy = _release_policy(
        model_version="resume_release_candidate",
        strategy="resume_policy_strategy",
    )
    policies = _mock_policies().copy()
    policies.loc[
        policies["policy_name"].eq("day14_structural_all_final_candidate"),
        "policy_name",
    ] = release_policy.model_version

    tables = module.build_all_tables(
        predictions=_mock_predictions(),
        policies=policies,
        thresholds=_mock_thresholds(),
        fp_cost=10,
        fn_cost=500,
        release_policy=release_policy,
    )
    report = module.build_markdown_report(
        tables,
        release_policy=release_policy,
    )

    official_policies = tables["final_policy_cost_comparison"].loc[
        lambda df: df["dataset"].eq("official_test"), "policy_name"
    ]
    assert official_policies.tolist() == [
        "naive_all_negative",
        "day14_baseline_median_all",
        release_policy.model_version,
        "day16_tuned_best",
    ]
    assert f"`{release_policy.model_version}`" in report
    assert f"`{release_policy.strategy}`" in report
    assert "day14_structural_all_final_candidate" not in report


def test_sql_export_manifest_uses_release_policy_metadata() -> None:
    """SQL 导出 manifest 不应写死历史 final candidate 名称。"""

    module = _load_day19_module()
    release_policy = _release_policy(
        model_version="resume_release_candidate",
        strategy="resume_policy_strategy",
    )

    entries = module.build_export_manifest_entries(
        prediction_path=Path("model_prediction_results.csv"),
        policy_path=Path("model_policy_comparison.csv"),
        threshold_path=Path("threshold_sensitivity_results.csv"),
        release_policy=release_policy,
    )
    descriptions = " ".join(description for _, description, _ in entries)

    assert release_policy.model_version in descriptions
    assert release_policy.strategy in descriptions
    assert "Day14 structural_all" not in descriptions


def test_sql_risk_summary_uses_population_and_queue_semantics() -> None:
    """SQL 风险汇总应与 Python 的层级人口和队列字段保持一致。"""

    sql_path = Path(__file__).resolve().parents[1] / "sql" / "09_risk_workload_analysis.sql"
    sql = sql_path.read_text(encoding="utf-8")

    assert "COUNT(*) AS tier_population" in sql
    assert "AVG(y_proba) AS avg_risk_score" in sql
    assert "AS aps_inspection_queue_count" in sql
    assert "AS recheck_queue_count" in sql
    assert "COUNT(*) AS estimated_workload" not in sql
    assert "avg_predicted_probability" not in sql
