"""Day 17 histogram/bin-like prefix projection features.

These utilities only use anonymous field-name structure such as ``ag_000``.
They do not assign any physical meaning to a prefix or a bin.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

import numpy as np
import pandas as pd


BIN_PATTERN = re.compile(r"^([A-Za-z]+)_(\d+)$")
NEAR_ZERO_EPS = 1e-8


@dataclass(frozen=True)
class BinProjectionBuilder:
    """Rules fitted on fold_train/train_inner for bin projection."""

    group_columns: dict[str, list[str]]
    group_bin_indices: dict[str, list[int]]
    add_features: list[str]
    tail_bin_count: int
    keep_original_bin_columns: bool


def extract_bin_prefix_and_index(feature_name: str) -> tuple[str, int] | None:
    """Parse a feature name like ``ag_009`` into ``("ag", 9)``."""

    match = BIN_PATTERN.match(str(feature_name))
    if match is None:
        return None
    return match.group(1), int(match.group(2))


def get_bin_group_columns(
    feature_cols: list[str],
    candidate_prefix_groups: list[str],
) -> dict[str, list[str]]:
    """Find bin-like columns by prefix and sort them by parsed bin index."""

    candidate_set = set(candidate_prefix_groups)
    grouped: dict[str, list[tuple[int, str]]] = {}

    for col in feature_cols:
        parsed = extract_bin_prefix_and_index(col)
        if parsed is None:
            continue
        prefix, bin_index = parsed
        if prefix not in candidate_set:
            continue
        grouped.setdefault(prefix, []).append((bin_index, col))

    return {
        prefix: [col for _, col in sorted(items, key=lambda item: item[0])]
        for prefix, items in sorted(grouped.items())
        if len(items) >= 2
    }


def _bin_projection_config(config: dict[str, Any]) -> dict[str, Any]:
    """Read the bin projection config from either full cfg node or section node."""

    if "bin_projection" in config:
        return config["bin_projection"]
    return config


def fit_bin_projection_builder(
    train_df: pd.DataFrame,
    feature_cols: list[str],
    candidate_prefix_groups: list[str],
    config: dict[str, Any],
) -> BinProjectionBuilder:
    """Fit bin projection membership on fold_train/train_inner only."""

    bin_config = _bin_projection_config(config)
    group_columns = get_bin_group_columns(feature_cols, candidate_prefix_groups)
    group_bin_indices: dict[str, list[int]] = {}

    for prefix, cols in group_columns.items():
        indices: list[int] = []
        for col in cols:
            parsed = extract_bin_prefix_and_index(col)
            if parsed is None:
                continue
            indices.append(parsed[1])
        group_bin_indices[prefix] = indices

    return BinProjectionBuilder(
        group_columns=group_columns,
        group_bin_indices=group_bin_indices,
        add_features=list(
            bin_config.get(
                "add_features",
                [
                    "sum",
                    "mean",
                    "std",
                    "max",
                    "nonzero_count",
                    "zero_rate",
                    "weighted_mean_bin",
                    "tail_ratio",
                    "peak_bin_index",
                ],
            )
        ),
        tail_bin_count=int(bin_config.get("tail_bin_count", 3)),
        keep_original_bin_columns=bool(bin_config.get("keep_original_bin_columns", True)),
    )


def _safe_numeric_values(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Return numeric values for a fixed column list."""

    return df.loc[:, cols].apply(pd.to_numeric, errors="coerce")


def transform_bin_projection_features(
    df: pd.DataFrame,
    builder: BinProjectionBuilder,
) -> pd.DataFrame:
    """Generate row-level bin projection features using fitted prefix groups."""

    result = pd.DataFrame(index=df.index)

    for prefix, cols in builder.group_columns.items():
        values = _safe_numeric_values(df, cols)
        filled = values.fillna(0.0)
        add_features = set(builder.add_features)
        denom = filled.sum(axis=1)
        nonzero_count = (values.notna() & (values.abs() > NEAR_ZERO_EPS)).sum(axis=1)
        zero_count = (values.notna() & (values.abs() <= NEAR_ZERO_EPS)).sum(axis=1)

        if "sum" in add_features:
            result[f"bin_{prefix}_sum"] = denom
        if "mean" in add_features:
            result[f"bin_{prefix}_mean"] = values.mean(axis=1).fillna(0.0)
        if "std" in add_features:
            result[f"bin_{prefix}_std"] = values.std(axis=1, ddof=0).fillna(0.0)
        if "max" in add_features:
            result[f"bin_{prefix}_max"] = values.max(axis=1).fillna(0.0)
        if "nonzero_count" in add_features:
            result[f"bin_{prefix}_nonzero_count"] = nonzero_count
        if "zero_rate" in add_features:
            result[f"bin_{prefix}_zero_rate"] = zero_count / len(cols)

        bin_indices = np.array(builder.group_bin_indices[prefix], dtype=float)
        weighted_sum = filled.to_numpy(dtype=float) @ bin_indices
        denom_array = denom.to_numpy(dtype=float)
        safe_weighted_mean = np.divide(
            weighted_sum,
            denom_array,
            out=np.zeros_like(weighted_sum, dtype=float),
            where=np.abs(denom_array) > NEAR_ZERO_EPS,
        )

        if "weighted_mean_bin" in add_features:
            result[f"bin_{prefix}_weighted_mean_bin"] = safe_weighted_mean

        if "tail_ratio" in add_features:
            tail_n = min(max(builder.tail_bin_count, 1), len(cols))
            tail_sum = filled.iloc[:, -tail_n:].sum(axis=1).to_numpy(dtype=float)
            tail_ratio = np.divide(
                tail_sum,
                denom_array,
                out=np.zeros_like(tail_sum, dtype=float),
                where=np.abs(denom_array) > NEAR_ZERO_EPS,
            )
            result[f"bin_{prefix}_tail_ratio"] = tail_ratio

        if "peak_bin_index" in add_features:
            argmax_positions = filled.to_numpy(dtype=float).argmax(axis=1)
            peak_indices = bin_indices[argmax_positions]
            peak_indices = np.where(np.abs(denom_array) > NEAR_ZERO_EPS, peak_indices, 0.0)
            result[f"bin_{prefix}_peak_bin_index"] = peak_indices

    return result


def build_bin_projection_metadata(builder: BinProjectionBuilder) -> pd.DataFrame:
    """Build readable metadata for generated bin projection features."""

    rows: list[dict[str, Any]] = []
    for prefix, cols in builder.group_columns.items():
        generated_features = [
            f"bin_{prefix}_{feature_name}" for feature_name in builder.add_features
        ]
        rows.append(
            {
                "prefix": prefix,
                "source_columns": "|".join(cols),
                "n_bins": len(cols),
                "generated_features": "|".join(generated_features),
                "keep_original_bin_columns": builder.keep_original_bin_columns,
            }
        )
    return pd.DataFrame(rows)
