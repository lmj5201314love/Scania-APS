"""Day15 XGBoost 调参模块的轻量 schema 测试。"""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pandas as pd

from scania_aps.models.xgb_tuning import (
    evaluate_xgb_trial,
    prepare_tuning_feature_set,
    sample_xgb_params,
    summarize_top_trials_for_refinement,
)


def _mock_cfg() -> SimpleNamespace:
    return SimpleNamespace(
        label_column="class",
        random_state=42,
        high_missing_threshold=0.8,
        false_positive_cost=10,
        false_negative_cost=500,
        xgb_tuning={
            "random_state": 42,
            "threshold_grid": {"start": 0.1, "stop": 0.3, "step": 0.1},
            "xgb_fixed_params": {
                "objective": "binary:logistic",
                "eval_metric": "aucpr",
                "tree_method": "hist",
                "n_jobs": 1,
            },
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
            "br_000": rng.normal(size=n_rows),
        }
    )
    df.loc[df["target"].eq(1), "br_000"] = np.nan
    df.loc[df.index[::5], "ag_000"] = 0.0
    return df


def test_sample_xgb_params_supports_uniform_log_uniform_and_values() -> None:
    rng = np.random.default_rng(7)
    params = sample_xgb_params(
        {
            "n_estimators": {"min": 10, "max": 20},
            "learning_rate": {"min": 0.01, "max": 0.20, "distribution": "log_uniform"},
            "max_depth": {"values": [2, 3, 4]},
            "subsample": {"min": 0.5, "max": 1.0},
        },
        rng,
    )

    assert isinstance(params["n_estimators"], int)
    assert 10 <= params["n_estimators"] <= 20
    assert 0.01 <= params["learning_rate"] <= 0.20
    assert params["max_depth"] in {2, 3, 4}
    assert 0.5 <= params["subsample"] <= 1.0


def test_summarize_top_trials_for_refinement_builds_refined_space() -> None:
    top_trials = pd.DataFrame(
        {
            "param_n_estimators": [100, 120, 140],
            "param_learning_rate": [0.02, 0.03, 0.04],
            "param_max_depth": [3, 4, 4],
        }
    )
    top_trials.attrs["original_search_space"] = {
        "n_estimators": {"min": 50, "max": 300},
        "learning_rate": {"min": 0.005, "max": 0.20, "distribution": "log_uniform"},
        "max_depth": {"values": [2, 3, 4, 5]},
    }

    refined = summarize_top_trials_for_refinement(top_trials)

    assert set(refined) == {"n_estimators", "learning_rate", "max_depth"}
    assert refined["n_estimators"]["min"] >= 50
    assert refined["n_estimators"]["max"] <= 300
    assert refined["learning_rate"]["distribution"] == "log_uniform"
    assert set(refined["max_depth"]["values"]).issubset({2, 3, 4, 5})


def test_prepare_tuning_feature_set_returns_expected_parts() -> None:
    df = _mock_dataset()
    train_inner_df = df.iloc[:28].copy()
    valid_df = df.iloc[28:].copy()

    prepared = prepare_tuning_feature_set(
        train_inner_df=train_inner_df,
        valid_df=valid_df,
        cfg=_mock_cfg(),
        structural_config=_mock_structural_config(),
        candidate_strategy="baseline_median_all",
    )

    assert prepared.X_train.shape[0] == len(train_inner_df)
    assert prepared.X_valid.shape[0] == len(valid_df)
    assert prepared.y_train.tolist() == train_inner_df["target"].tolist()
    assert prepared.metadata["uses_official_test"] is False


def test_evaluate_xgb_trial_outputs_required_columns() -> None:
    df = _mock_dataset()
    train_inner_df = df.iloc[:28].copy()
    valid_df = df.iloc[28:].copy()
    cfg = _mock_cfg()
    prepared = prepare_tuning_feature_set(
        train_inner_df=train_inner_df,
        valid_df=valid_df,
        cfg=cfg,
        structural_config=_mock_structural_config(),
        candidate_strategy="baseline_median_all",
    )

    threshold_metrics, best_record = evaluate_xgb_trial(
        X_train=prepared.X_train,
        y_train=prepared.y_train,
        X_valid=prepared.X_valid,
        y_valid=prepared.y_valid,
        cfg=cfg,
        params={
            "n_estimators": 2,
            "learning_rate": 0.2,
            "max_depth": 2,
            "min_child_weight": 1,
            "subsample": 1.0,
            "colsample_bytree": 1.0,
            "gamma": 0,
            "reg_lambda": 1.0,
            "reg_alpha": 0.0,
            "scale_pos_weight": 1.0,
            "max_delta_step": 0,
        },
        candidate_strategy="baseline_median_all",
        trial_id="test_trial",
        search_stage="broad",
    )

    required_columns = {
        "candidate_strategy",
        "trial_id",
        "search_stage",
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
    }
    assert required_columns.issubset(threshold_metrics.columns)
    assert best_record["candidate_strategy"] == "baseline_median_all"
    assert best_record["search_stage"] == "broad"
