"""Day 13 结构特征实验结果 schema 测试。"""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pandas as pd

from scania_aps.models.structural_feature_experiments import (
    run_structural_feature_valid_experiments,
)


def _mock_cfg() -> SimpleNamespace:
    return SimpleNamespace(
        label_column="class",
        random_state=42,
        default_threshold=0.5,
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


def _mock_dataset(n_rows: int = 36) -> pd.DataFrame:
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


def test_structural_feature_experiment_outputs_required_columns() -> None:
    df = _mock_dataset()
    train_inner_df = df.iloc[:24].copy()
    valid_df = df.iloc[24:].copy()

    results = run_structural_feature_valid_experiments(
        train_inner_df=train_inner_df,
        valid_df=valid_df,
        cfg=_mock_cfg(),
        structural_config=_mock_structural_config(),
        experiment_groups=[
            "baseline_median_all",
            "median_all_sample_missing_rate",
        ],
    )

    valid_best = results["valid_best_summary"]
    metadata = results["experiment_metadata"]

    required_best_columns = {
        "model_name",
        "strategy",
        "best_threshold",
        "recall",
        "f2",
        "average_precision",
        "fp",
        "fn",
        "total_cost",
        "n_structural_features",
    }
    required_metadata_columns = {
        "experiment_group",
        "n_original_features",
        "n_structural_features",
        "structural_feature_names",
    }

    assert required_best_columns.issubset(valid_best.columns)
    assert required_metadata_columns.issubset(metadata.columns)
    assert set(metadata["experiment_group"]) == {
        "baseline_median_all",
        "median_all_sample_missing_rate",
    }
