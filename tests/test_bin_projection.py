"""Bin projection feature tests for Day17."""

from __future__ import annotations

import pandas as pd

from scania_aps.features.bin_projection import (
    build_bin_projection_metadata,
    extract_bin_prefix_and_index,
    fit_bin_projection_builder,
    get_bin_group_columns,
    transform_bin_projection_features,
)


def test_extract_bin_prefix_and_index() -> None:
    assert extract_bin_prefix_and_index("ag_000") == ("ag", 0)
    assert extract_bin_prefix_and_index("ag_009") == ("ag", 9)
    assert extract_bin_prefix_and_index("cn_003") == ("cn", 3)
    assert extract_bin_prefix_and_index("bad_name") is None


def test_get_bin_group_columns_sorts_by_index() -> None:
    columns = ["ag_002", "ag_000", "ag_001", "cn_003", "cn_001", "aa_000"]

    grouped = get_bin_group_columns(columns, ["ag", "cn"])

    assert grouped["ag"] == ["ag_000", "ag_001", "ag_002"]
    assert grouped["cn"] == ["cn_001", "cn_003"]


def test_transform_bin_projection_features_handles_nan_and_zero_rows() -> None:
    df = pd.DataFrame(
        {
            "ag_000": [1.0, 0.0, None],
            "ag_001": [2.0, 0.0, None],
            "ag_002": [3.0, 0.0, None],
            "cn_000": [0.0, 5.0, None],
            "cn_001": [0.0, 0.0, None],
        }
    )
    original = df.copy(deep=True)
    builder = fit_bin_projection_builder(
        train_df=df,
        feature_cols=df.columns.tolist(),
        candidate_prefix_groups=["ag", "cn"],
        config={
            "add_features": [
                "sum",
                "nonzero_count",
                "weighted_mean_bin",
                "tail_ratio",
                "peak_bin_index",
            ],
            "tail_bin_count": 2,
            "keep_original_bin_columns": True,
        },
    )

    transformed = transform_bin_projection_features(df, builder)
    metadata = build_bin_projection_metadata(builder)

    pd.testing.assert_frame_equal(df, original)
    assert transformed.loc[0, "bin_ag_sum"] == 6.0
    assert transformed.loc[0, "bin_ag_nonzero_count"] == 3
    assert transformed.loc[0, "bin_ag_weighted_mean_bin"] == (0 * 1 + 1 * 2 + 2 * 3) / 6
    assert transformed.loc[1, "bin_ag_weighted_mean_bin"] == 0.0
    assert transformed.loc[2, "bin_ag_tail_ratio"] == 0.0
    assert transformed.loc[0, "bin_ag_peak_bin_index"] == 2.0
    assert set(metadata["prefix"]) == {"ag", "cn"}
