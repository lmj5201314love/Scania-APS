"""Day 14 official test 观察模块的轻量 schema 测试。"""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pandas as pd

from scania_aps.models.structural_feature_test_evaluation import (
    evaluate_structural_feature_candidates_on_test,
)


def _mock_cfg() -> SimpleNamespace:
    return SimpleNamespace(
        label_column="class",
        random_state=42,
        false_positive_cost=10,
        false_negative_cost=500,
        advanced_models={
            "xgboost": {
                "n_estimators": 2,
                "max_depth": 2,
                "learning_rate": 0.2,
                "subsample": 1.0,
                "colsample_bytree": 1.0,
                "eval_metric": "logloss",
                "n_jobs": 1,
            }
        },
    )


def _mock_structural_config() -> dict:
    return {
        "candidate_prefix_groups": {
            "high_priority": ["ag", "ay", "cn"],
            "medium_priority": ["az", "cs"],
            "low_priority": ["ba", "ee"],
        },
        "selected_missing_indicators": {
            "min_missing_rate": 0.05,
            "min_abs_pos_neg_missing_diff": 0.05,
            "max_selected_features": 3,
        },
    }


def _mock_dataset(n_rows: int = 40) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    target = np.array([0, 1] * (n_rows // 2))
    df = pd.DataFrame(
        {
            "class": np.where(target == 1, "pos", "neg"),
            "target": target,
            "ag_000": rng.normal(size=n_rows),
            "ag_001": rng.normal(size=n_rows),
            "ay_000": rng.normal(size=n_rows),
            "cn_000": rng.normal(size=n_rows),
            "br_000": rng.normal(size=n_rows),
        }
    )
    df.loc[df["target"].eq(1), "br_000"] = np.nan
    df.loc[df.index[::4], "ag_000"] = 0.0
    return df


def test_day14_test_evaluation_schema_and_threshold_source() -> None:
    df = _mock_dataset()
    train_inner_df = df.iloc[:24].copy()
    valid_df = df.iloc[24:32].copy()
    test_df = df.iloc[32:].copy()
    valid_best_summary = pd.DataFrame(
        {
            "strategy": [
                "baseline_median_all",
                "median_all_selected_missing_indicators_top30",
            ],
            "best_threshold": [0.16, 0.30],
            "precision": [0.5, 0.6],
            "recall": [0.8, 0.7],
            "f1": [0.6, 0.65],
            "f2": [0.7, 0.68],
            "average_precision": [0.55, 0.56],
            "fp": [2, 1],
            "fn": [1, 2],
            "total_cost": [520, 1010],
        }
    )

    results = evaluate_structural_feature_candidates_on_test(
        train_inner_df=train_inner_df,
        valid_df=valid_df,
        test_df=test_df,
        cfg=_mock_cfg(),
        structural_config=_mock_structural_config(),
        candidate_groups=[
            "baseline_median_all",
            "median_all_selected_missing_indicators_top30",
        ],
        valid_best_summary=valid_best_summary,
    )

    required_result_cols = {
        "candidate_group",
        "threshold",
        "threshold_source",
        "precision",
        "recall",
        "f2",
        "average_precision",
        "fp",
        "fn",
        "total_cost",
    }
    required_prediction_cols = {
        "dataset",
        "sample_id",
        "y_true",
        "y_proba",
        "y_pred",
        "candidate_group",
        "threshold",
    }

    test_results = results["test_results"]
    predictions = results["test_predictions"]

    assert required_result_cols.issubset(test_results.columns)
    assert required_prediction_cols.issubset(predictions.columns)
    assert set(test_results["candidate_group"]) == {
        "baseline_median_all",
        "median_all_selected_missing_indicators_top30",
    }
    assert set(test_results["threshold"]) == {0.16, 0.30}
    assert test_results["threshold_source"].eq("day13_valid_best_summary").all()
