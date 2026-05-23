from __future__ import annotations

from types import SimpleNamespace

import pandas as pd

from scania_aps.models.oof_ensemble_experiments import (
    build_oof_probability_ensembles,
    evaluate_oof_ensemble_thresholds,
    select_day19_official_test_candidates,
)


def _mock_base_predictions() -> pd.DataFrame:
    rows = []
    values = {
        "median_all_structural_all": [0.10, 0.80, 0.35, 0.60],
        "median_with_selected_missing_indicators": [0.20, 0.70, 0.50, 0.40],
        "median_all_prefix_zero_rate": [0.05, 0.90, 0.30, 0.70],
    }
    y_true = [0, 1, 0, 1]
    for strategy, probs in values.items():
        for sample_index, proba in enumerate(probs):
            rows.append(
                {
                    "sample_index": sample_index,
                    "y_true": y_true[sample_index],
                    "y_proba": proba,
                    "base_candidate_strategy": strategy,
                    "repeat_id": 1,
                    "fold_id": 1,
                    "model_name": "xgboost_oof_base",
                }
            )
    return pd.DataFrame(rows)


def _mock_cfg() -> SimpleNamespace:
    return SimpleNamespace(false_positive_cost=10, false_negative_cost=500)


def _mock_ensemble_config() -> dict:
    return {
        "threshold_grid": {"start": 0.10, "stop": 0.90, "step": 0.20},
        "threshold_selection_rules": ["cost_min", "recall_floor_960", "fn_floor_1"],
        "recall_floors": {"recall_floor_960": 0.960},
        "fn_floors": {"fn_floor_1": 1},
    }


def test_build_oof_probability_ensembles_calculates_weighted_scores() -> None:
    outputs = build_oof_probability_ensembles(
        _mock_base_predictions(),
        {
            "main": [
                "structural_all_single",
                "weighted_70_30_indicator",
                "weighted_60_25_15",
                "weighted_rank_60_25_15",
            ],
            "auxiliary": ["rank_average_three"],
            "diagnostic": ["max_three_models"],
        },
    )
    predictions = outputs["oof_ensemble_predictions"]

    weighted_70_30 = predictions[
        predictions["ensemble_name"].eq("weighted_70_30_indicator")
        & predictions["sample_index"].eq(0)
    ].iloc[0]
    assert weighted_70_30["ensemble_score"] == 0.7 * 0.10 + 0.3 * 0.20

    weighted_60_25_15 = predictions[
        predictions["ensemble_name"].eq("weighted_60_25_15")
        & predictions["sample_index"].eq(1)
    ].iloc[0]
    assert weighted_60_25_15["ensemble_score"] == 0.60 * 0.80 + 0.25 * 0.70 + 0.15 * 0.90

    rank_scores = predictions[predictions["ensemble_name"].eq("rank_average_three")]
    assert rank_scores["ensemble_score"].between(0, 1).all()

    max_score = predictions[
        predictions["ensemble_name"].eq("max_three_models")
        & predictions["sample_index"].eq(3)
    ].iloc[0]
    assert max_score["ensemble_score"] == 0.70


def test_evaluate_oof_ensemble_thresholds_outputs_required_columns() -> None:
    outputs = build_oof_probability_ensembles(
        _mock_base_predictions(),
        {
            "main": ["structural_all_single", "weighted_70_30_indicator"],
            "auxiliary": ["rank_average_three"],
            "diagnostic": ["max_three_models"],
        },
    )
    threshold_metrics, best_summary, _strategy_compare = evaluate_oof_ensemble_thresholds(
        outputs["oof_ensemble_predictions"],
        cfg=_mock_cfg(),
        ensemble_config=_mock_ensemble_config(),
    )

    required_columns = {
        "ensemble_name",
        "ensemble_group",
        "threshold_selection_rule",
        "threshold",
        "precision",
        "recall",
        "f1",
        "f2",
        "average_precision",
        "fp",
        "fn",
        "total_cost",
    }
    assert required_columns.issubset(set(best_summary.columns))
    assert {"model_name", "strategy", "threshold"}.issubset(set(threshold_metrics.columns))
    assert {"cost_min", "recall_floor_960", "fn_floor_1"}.issubset(
        set(best_summary["threshold_selection_rule"])
    )


def test_select_day19_candidates_excludes_diagnostic_and_max() -> None:
    best_summary = pd.DataFrame(
        [
            {
                "ensemble_name": "structural_all_single",
                "ensemble_group": "main",
                "threshold_selection_rule": "cost_min",
                "threshold": 0.2,
                "precision": 0.5,
                "recall": 0.96,
                "f2": 0.7,
                "average_precision": 0.8,
                "fp": 100,
                "fn": 40,
                "total_cost": 21000,
            },
            {
                "ensemble_name": "weighted_70_30_indicator",
                "ensemble_group": "main",
                "threshold_selection_rule": "cost_min",
                "threshold": 0.2,
                "precision": 0.5,
                "recall": 0.97,
                "f2": 0.72,
                "average_precision": 0.81,
                "fp": 180,
                "fn": 35,
                "total_cost": 19300,
            },
            {
                "ensemble_name": "max_three_models",
                "ensemble_group": "diagnostic",
                "threshold_selection_rule": "cost_min",
                "threshold": 0.2,
                "precision": 0.4,
                "recall": 0.99,
                "f2": 0.75,
                "average_precision": 0.8,
                "fp": 300,
                "fn": 20,
                "total_cost": 13000,
            },
        ]
    )
    recommendations = select_day19_official_test_candidates(
        best_summary,
        filter_config={
            "min_oof_cost_reduction_pct": 0.03,
            "min_fn_reduction": 3,
            "max_fp_increase_per_fn_saved": 40,
            "allow_max_three_models": False,
            "allow_diagnostic_as_final_candidate": False,
        },
    )

    max_row = recommendations[recommendations["ensemble_name"].eq("max_three_models")].iloc[0]
    assert not bool(max_row["recommend_for_day19"])
    assert "diagnostic" in max_row["recommendation_reason"]
