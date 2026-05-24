from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd


def _load_day20_module():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "18_generate_business_insight_figures.py"
    spec = importlib.util.spec_from_file_location("day20_business_insights", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


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
                "Medium",
                "Medium",
                "Medium",
                "Low",
                "Low",
                "Low",
            ],
            "suggested_action": [
                "immediate_inspection",
                "immediate_inspection",
                "priority_inspection",
                "priority_inspection",
                "monitor_and_recheck",
                "monitor_and_recheck",
                "monitor_and_recheck",
                "no_action_now",
                "no_action_now",
                "no_action_now",
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


def test_risk_workload_table_has_required_columns() -> None:
    module = _load_day20_module()

    table = module.build_risk_workload_summary(_mock_predictions())

    required = {
        "risk_level",
        "sample_count",
        "actual_pos_count",
        "actual_pos_rate",
        "avg_predicted_probability",
    }
    assert required.issubset(table.columns)
    assert table["priority_order"].tolist() == sorted(table["priority_order"].tolist())


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


def test_threshold_highlights_include_final_threshold_018() -> None:
    module = _load_day20_module()
    threshold_summary = module.build_threshold_sensitivity_summary(_mock_thresholds())

    highlights = module.build_threshold_policy_highlights(threshold_summary)

    required = {"policy_rule", "threshold", "fp", "fn", "recall", "total_cost"}
    assert required.issubset(highlights.columns)
    assert "final_threshold_018" in set(highlights["policy_rule"])
    final_row = highlights.loc[highlights["policy_rule"] == "final_threshold_018"].iloc[0]
    assert final_row["threshold"] == 0.18


def test_policy_comparison_keeps_oof_separate_from_official_test() -> None:
    module = _load_day20_module()

    table = module.build_policy_cost_comparison(_mock_policies())

    official_positions = table.index[table["dataset"].eq("official_test")].tolist()
    oof_positions = table.index[table["dataset"].eq("oof_train")].tolist()
    assert max(official_positions) < min(oof_positions)
    oof_note = table.loc[table["dataset"].eq("oof_train"), "note"].iloc[0]
    assert "不可与 official test" in oof_note
