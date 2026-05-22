"""OOF threshold selection tests for Day17."""

from __future__ import annotations

from types import SimpleNamespace

import pandas as pd

from scania_aps.models.oof_threshold_experiments import (
    build_oof_splits,
    evaluate_threshold_grid_with_constraints,
)


def _mock_cfg() -> SimpleNamespace:
    return SimpleNamespace(
        random_state=42,
        false_positive_cost=10,
        false_negative_cost=500,
        oof_threshold={
            "cv": {
                "n_splits": 3,
                "n_repeats": 1,
                "stratified": True,
                "shuffle": True,
            },
            "allow_runtime_downgrade": {
                "enabled": False,
                "min_n_splits": 2,
                "min_n_repeats": 1,
            },
            "threshold_grid": {
                "start": 0.1,
                "stop": 0.9,
                "step": 0.4,
            },
            "threshold_selection_rules": [
                "cost_min",
                "recall_floor_975",
                "fn_floor_2",
            ],
            "recall_floors": {
                "recall_floor_975": 0.975,
            },
            "fn_floors": {
                "fn_floor_2": 2,
            },
        },
    )


def test_build_oof_splits_generates_stratified_folds() -> None:
    y = pd.Series([0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1])
    splits = build_oof_splits(y, _mock_cfg())

    assert len(splits) == 3
    assert all(split.repeat_id == 1 for split in splits)
    assert sorted(len(split.valid_idx) for split in splits) == [4, 4, 4]
    assert all(y.iloc[split.valid_idx].sum() == 2 for split in splits)


def test_evaluate_threshold_grid_with_constraints_outputs_required_columns() -> None:
    predictions = pd.DataFrame(
        {
            "candidate_strategy": ["baseline"] * 6,
            "sample_index": range(6),
            "y_true": [0, 0, 1, 1, 1, 0],
            "y_proba": [0.05, 0.20, 0.95, 0.80, 0.40, 0.70],
        }
    )

    threshold_metrics, best_summary = evaluate_threshold_grid_with_constraints(
        oof_predictions=predictions,
        cfg=_mock_cfg(),
        threshold_grid=[0.1, 0.5, 0.9],
        threshold_selection_rules=["cost_min", "recall_floor_975", "fn_floor_2"],
    )

    required = {
        "candidate_strategy",
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
        "selection_dataset",
    }
    assert required.issubset(best_summary.columns)
    assert not threshold_metrics.empty

    recall_row = best_summary[
        best_summary["threshold_selection_rule"].eq("recall_floor_975")
    ].iloc[0]
    assert recall_row["recall"] >= 0.975

    fn_row = best_summary[best_summary["threshold_selection_rule"].eq("fn_floor_2")].iloc[0]
    assert fn_row["fn"] <= 2
