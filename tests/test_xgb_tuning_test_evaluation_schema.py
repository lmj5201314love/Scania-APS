"""Day16 tuned XGBoost official test 观察 schema 测试。"""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pandas as pd

from scania_aps.models.xgb_tuning_test_evaluation import (
    evaluate_tuned_xgb_candidates_on_test,
)


def _mock_cfg() -> SimpleNamespace:
    return SimpleNamespace(
        label_column="class",
        random_state=42,
        high_missing_threshold=0.8,
        false_positive_cost=10,
        false_negative_cost=500,
        xgb_tuning={
            "xgb_fixed_params": {
                "objective": "binary:logistic",
                "eval_metric": "aucpr",
                "tree_method": "hist",
                "n_jobs": 1,
            },
            "random_state": 42,
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


def _mock_dataset(n_rows: int = 48) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    target = np.array([0, 1] * (n_rows // 2))
    df = pd.DataFrame(
        {
            "class": np.where(target == 1, "pos", "neg"),
            "target": target,
            "ag_000": rng.normal(size=n_rows),
            "ag_001": rng.normal(size=n_rows),
            "ay_000": rng.normal(size=n_rows),
            "br_000": rng.normal(size=n_rows),
        }
    )
    df.loc[df["target"].eq(1), "br_000"] = np.nan
    df.loc[df.index[::4], "ag_000"] = 0.0
    return df


def _mock_day15_summary() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "candidate_strategy": "baseline_median_all",
                "threshold": 0.2,
                "trial_id": "baseline_median_all_test_trial",
                "search_stage": "broad",
                "param_n_estimators": 2,
                "param_learning_rate": 0.2,
                "param_max_depth": 2,
                "param_min_child_weight": 1,
                "param_subsample": 1.0,
                "param_colsample_bytree": 1.0,
                "param_gamma": 0.0,
                "param_reg_lambda": 1.0,
                "param_reg_alpha": 0.0,
                "param_scale_pos_weight": 1.0,
                "param_max_delta_step": 0,
            }
        ]
    )


def test_tuned_xgb_test_evaluation_outputs_required_schema() -> None:
    df = _mock_dataset()
    train_inner_df = df.iloc[:28].copy()
    valid_df = df.iloc[28:38].copy()
    test_df = df.iloc[38:].copy()

    results = evaluate_tuned_xgb_candidates_on_test(
        train_inner_df=train_inner_df,
        valid_df=valid_df,
        test_df=test_df,
        cfg=_mock_cfg(),
        structural_config=_mock_structural_config(),
        day15_best_summary=_mock_day15_summary(),
        candidate_strategies=["baseline_median_all"],
    )

    test_results = results["tuned_test_results"]
    predictions = results["tuned_test_predictions"]
    compare = results["tuned_valid_test_compare"]

    required_columns = {
        "candidate_strategy",
        "threshold",
        "precision",
        "recall",
        "f1",
        "f2",
        "average_precision",
        "fp",
        "fn",
        "total_cost",
        "n_total_features",
        "selection_dataset",
        "evaluation_dataset",
    }

    assert required_columns.issubset(test_results.columns)
    assert test_results.loc[0, "threshold"] == 0.2
    assert test_results.loc[0, "selection_dataset"] == "valid"
    assert test_results.loc[0, "evaluation_dataset"] == "official_test"
    assert predictions["threshold"].nunique() == 1
    assert predictions["threshold"].iloc[0] == 0.2
    assert "delta_total_cost_test_minus_valid" in compare.columns
