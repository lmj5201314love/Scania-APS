from __future__ import annotations

import numpy as np
import pandas as pd

from scania_aps.interpretability.model_interpretability import (
    build_case_explanation_tables,
    categorize_feature,
    compute_xgb_feature_importance,
    summarize_feature_family_importance,
    summarize_shap_importance,
)


class _FakeBooster:
    def get_score(self, importance_type: str) -> dict[str, float]:
        scores = {
            "weight": {"aa_000": 3.0, "missing_br_000": 1.0},
            "gain": {"aa_000": 10.0, "missing_br_000": 4.0},
            "cover": {"aa_000": 8.0, "missing_br_000": 2.0},
        }
        return scores[importance_type]


class _FakeModel:
    def get_booster(self) -> _FakeBooster:
        return _FakeBooster()


def test_categorize_feature_families() -> None:
    assert categorize_feature("aa_000") == "raw_feature"
    assert categorize_feature("missing_br_000") == "missing_indicator"
    assert categorize_feature("sample_missing_rate") == "sample_structural_feature"
    assert categorize_feature("prefix_ag_zero_rate") == "prefix_zero_feature"


def test_xgb_feature_importance_schema() -> None:
    table = compute_xgb_feature_importance(
        _FakeModel(),
        ["aa_000", "missing_br_000", "sample_missing_rate"],
    )

    required = {
        "feature_name",
        "feature_family",
        "importance_gain",
        "rank_by_gain",
    }
    assert required.issubset(table.columns)
    assert table.iloc[0]["feature_name"] == "aa_000"


def test_feature_family_summary_aggregates() -> None:
    xgb_importance = compute_xgb_feature_importance(
        _FakeModel(),
        ["aa_000", "missing_br_000", "sample_missing_rate"],
    )
    shap_importance = pd.DataFrame(
        {
            "feature_name": ["aa_000", "missing_br_000", "sample_missing_rate"],
            "feature_family": ["raw_feature", "missing_indicator", "sample_structural_feature"],
            "mean_abs_shap": [1.0, 0.5, 0.25],
            "rank": [1, 2, 3],
        }
    )

    summary = summarize_feature_family_importance(xgb_importance, shap_importance)

    assert {"feature_family", "xgb_gain_total", "mean_abs_shap_total"}.issubset(
        summary.columns
    )
    raw = summary.loc[summary["feature_family"].eq("raw_feature")].iloc[0]
    assert raw["feature_count"] == 1
    assert raw["mean_abs_shap_total"] == 1.0


def test_shap_importance_schema() -> None:
    shap_values = np.array([[0.1, -0.2, 0.3], [0.2, -0.1, 0.1]])
    table = summarize_shap_importance(
        shap_values,
        ["aa_000", "missing_br_000", "sample_missing_rate"],
    )

    required = {"feature_name", "feature_family", "mean_abs_shap", "rank"}
    assert required.issubset(table.columns)
    assert table.iloc[0]["feature_name"] == "sample_missing_rate"


def test_case_explanation_table_schema() -> None:
    shap_values = np.array([[0.5, -0.2, 0.1], [0.3, -0.4, 0.2]])
    X_sample = pd.DataFrame(
        {
            "aa_000": [1.0, 2.0],
            "missing_br_000": [0, 1],
            "sample_missing_rate": [0.1, 0.2],
        }
    )
    sample_metadata = pd.DataFrame(
        {
            "sample_id": [10, 20],
            "y_true": [1, 0],
            "y_pred": [0, 1],
            "y_proba": [0.12, 0.95],
            "risk_level": ["Medium", "Critical"],
            "confusion_type": ["FN", "FP"],
        }
    )

    tables = build_case_explanation_tables(
        shap_values,
        X_sample,
        sample_metadata,
        ["aa_000", "missing_br_000", "sample_missing_rate"],
        top_n_features_per_sample=2,
    )

    required = {
        "sample_id",
        "y_true",
        "y_pred",
        "y_proba",
        "risk_level",
        "top_positive_shap_features",
        "top_negative_shap_features",
        "note",
    }
    assert required.issubset(tables["fn"].columns)
    assert tables["fn"].iloc[0]["sample_id"] == 10
    assert "aa_000" in tables["fn"].iloc[0]["top_positive_shap_features"]
