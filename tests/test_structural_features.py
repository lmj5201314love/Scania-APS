"""结构特征构造函数的轻量测试。"""

from __future__ import annotations

from types import SimpleNamespace

import pandas as pd

from scania_aps.features.structural_features import (
    build_prefix_zero_features,
    build_sample_missing_features,
    build_sample_zero_features,
    build_selected_missing_indicator_features,
    fit_structural_feature_builder,
    select_missing_indicator_columns,
    transform_structural_features,
)


def _mock_cfg() -> SimpleNamespace:
    return SimpleNamespace(label_column="class")


def _mock_structural_config() -> dict:
    return {
        "candidate_prefix_groups": {
            "high_priority": ["ag", "ay", "cn"],
            "medium_priority": ["az", "cs"],
            "low_priority": ["ba", "ee"],
        },
        "selected_missing_indicators": {
            "min_missing_rate": 0.10,
            "min_abs_pos_neg_missing_diff": 0.10,
            "max_selected_features": 2,
        },
    }


def _mock_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "class": ["neg", "pos", "neg", "pos"],
            "target": [0, 1, 0, 1],
            "ag_000": [0.0, 1.0, None, 2.0],
            "ag_001": [1.0, 0.0, 0.0, None],
            "ay_000": [0.0, 3.0, 0.0, 4.0],
            "cn_000": [5.0, 0.0, 6.0, 0.0],
            "br_000": [1.0, None, 2.0, None],
            "bq_000": [None, None, 3.0, None],
        }
    )


def test_sample_missing_rate_and_zero_rate_are_correct() -> None:
    df = _mock_df()
    feature_cols = ["ag_000", "ag_001"]

    missing_features = build_sample_missing_features(df, feature_cols)
    zero_features = build_sample_zero_features(df, feature_cols)

    assert missing_features["sample_missing_rate"].tolist() == [0.0, 0.0, 0.5, 0.5]
    assert zero_features["sample_zero_rate"].tolist() == [0.5, 0.5, 0.5, 0.0]


def test_prefix_zero_rate_is_based_on_prefix_members() -> None:
    df = _mock_df()
    prefix_features = build_prefix_zero_features(
        df,
        {"ag": ["ag_000", "ag_001"], "cn": ["cn_000"]},
    )

    assert prefix_features["prefix_ag_zero_rate"].tolist() == [0.5, 0.5, 0.5, 0.0]
    assert prefix_features["prefix_cn_zero_rate"].tolist() == [0.0, 1.0, 0.0, 1.0]


def test_selected_missing_indicators_only_fit_on_train_inner() -> None:
    df = _mock_df()
    selected = select_missing_indicator_columns(
        train_inner_df=df,
        cfg=_mock_cfg(),
        structural_config=_mock_structural_config(),
    )
    indicator_features = build_selected_missing_indicator_features(df, selected)

    assert len(selected) <= 2
    assert all(col.startswith("missing_") for col in indicator_features.columns)
    assert set(indicator_features.stack().unique()).issubset({0, 1})


def test_transform_structural_features_does_not_modify_source_df() -> None:
    df = _mock_df()
    original = df.copy(deep=True)
    builder = fit_structural_feature_builder(
        train_inner_df=df,
        cfg=_mock_cfg(),
        structural_config=_mock_structural_config(),
        feature_group="median_all_structural_core",
    )

    transformed = transform_structural_features(df, builder)

    pd.testing.assert_frame_equal(df, original)
    assert "sample_missing_rate" in transformed.columns
    assert "prefix_ag_zero_rate" in transformed.columns
    assert any(col.startswith("missing_") for col in transformed.columns)
