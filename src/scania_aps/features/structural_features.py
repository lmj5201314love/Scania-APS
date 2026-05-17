"""Day 13 结构特征构造工具。

本模块只负责在 train_inner 上确定结构规则，并把同一套规则应用到
train_inner / valid。不要在这里训练模型，也不要使用 official test
反向选择结构特征。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from scania_aps.config import ScaniaConfig


NEAR_ZERO_EPS = 1e-8


MAIN_EXPERIMENT_GROUPS = [
    "baseline_median_all",
    "median_all_sample_missing_rate",
    "median_all_selected_missing_indicators_top30",
    "median_all_prefix_zero_rate",
    "median_all_structural_core",
    "median_all_structural_all",
]


@dataclass(frozen=True)
class StructuralFeatureBuilder:
    """结构特征构造规则。

    所有字段选择和前缀成员关系都在 train_inner 上确定，transform 阶段只
    应用这些规则，不再重新选择字段。
    """

    feature_group: str
    feature_cols: list[str]
    prefix_missing_members: dict[str, list[str]]
    prefix_zero_members: dict[str, list[str]]
    selected_missing_indicator_columns: list[str]
    include_sample_missing_rate: bool = False
    include_sample_missing_count: bool = False
    include_sample_non_missing_count: bool = False
    include_sample_zero_rate: bool = False
    include_sample_zero_count: bool = False
    include_sample_non_zero_count: bool = False
    include_prefix_missing_rate: bool = False
    include_prefix_missing_count: bool = False
    include_prefix_zero_rate: bool = False
    include_prefix_zero_count: bool = False
    metadata: dict[str, Any] | None = None


def _structural_section(structural_config: dict[str, Any]) -> dict[str, Any]:
    """兼容读取 structural_features.yaml 的根节点。"""

    return structural_config.get("structural_features", structural_config)


def _candidate_prefixes(
    structural_config: dict[str, Any],
    *,
    include_low_priority: bool,
) -> list[str]:
    """读取候选前缀组，不赋予任何物理含义。"""

    section = _structural_section(structural_config)
    groups = section["candidate_prefix_groups"]
    prefixes = list(groups.get("high_priority", [])) + list(groups.get("medium_priority", []))
    if include_low_priority:
        prefixes.extend(groups.get("low_priority", []))
    return prefixes


def _extract_prefix(feature_name: str) -> str:
    """从匿名字段名中提取前缀。"""

    if "_" in feature_name:
        return feature_name.split("_", 1)[0]
    return feature_name[:2] if len(feature_name) >= 2 else feature_name


def _numeric_feature_columns(
    df: pd.DataFrame,
    cfg: ScaniaConfig,
    target_col: str = "target",
) -> list[str]:
    """返回原始数值特征列，排除 class 和 target。"""

    excluded = {cfg.label_column, target_col}
    return [col for col in df.columns if col not in excluded]


def _build_prefix_members(feature_cols: list[str], prefixes: list[str]) -> dict[str, list[str]]:
    """根据 train_inner schema 固定 prefix -> columns 成员关系。"""

    members: dict[str, list[str]] = {}
    for prefix in prefixes:
        cols = [col for col in feature_cols if _extract_prefix(col) == prefix]
        if cols:
            members[prefix] = cols
    return members


def build_sample_missing_features(
    df: pd.DataFrame,
    feature_cols: list[str],
    *,
    include_count: bool = False,
    include_non_missing_count: bool = False,
) -> pd.DataFrame:
    """构造样本级缺失统计特征。"""

    missing_count = df[feature_cols].isna().sum(axis=1)
    features = pd.DataFrame(index=df.index)
    if include_count:
        features["sample_missing_count"] = missing_count
    features["sample_missing_rate"] = missing_count / len(feature_cols)
    if include_non_missing_count:
        features["sample_non_missing_count"] = len(feature_cols) - missing_count
    return features


def build_sample_zero_features(
    df: pd.DataFrame,
    feature_cols: list[str],
    *,
    include_count: bool = False,
    include_non_zero_count: bool = False,
) -> pd.DataFrame:
    """构造样本级零值统计特征。"""

    values = df[feature_cols]
    zero_mask = values.notna() & (values.abs() <= NEAR_ZERO_EPS)
    zero_count = zero_mask.sum(axis=1)
    features = pd.DataFrame(index=df.index)
    if include_count:
        features["sample_zero_count"] = zero_count
    features["sample_zero_rate"] = zero_count / len(feature_cols)
    if include_non_zero_count:
        non_zero_count = values.notna().sum(axis=1) - zero_count
        features["sample_non_zero_count"] = non_zero_count
    return features


def build_prefix_missing_features(
    df: pd.DataFrame,
    prefix_members: dict[str, list[str]],
    *,
    include_count: bool = False,
    include_rate: bool = True,
) -> pd.DataFrame:
    """构造前缀组缺失聚合特征。"""

    features = pd.DataFrame(index=df.index)
    for prefix, cols in prefix_members.items():
        missing_count = df[cols].isna().sum(axis=1)
        if include_count:
            features[f"prefix_{prefix}_missing_count"] = missing_count
        if include_rate:
            features[f"prefix_{prefix}_missing_rate"] = missing_count / len(cols)
    return features


def build_prefix_zero_features(
    df: pd.DataFrame,
    prefix_members: dict[str, list[str]],
    *,
    include_count: bool = False,
    include_rate: bool = True,
) -> pd.DataFrame:
    """构造前缀组零值聚合特征。"""

    features = pd.DataFrame(index=df.index)
    for prefix, cols in prefix_members.items():
        values = df[cols]
        zero_count = (values.notna() & (values.abs() <= NEAR_ZERO_EPS)).sum(axis=1)
        if include_count:
            features[f"prefix_{prefix}_zero_count"] = zero_count
        if include_rate:
            features[f"prefix_{prefix}_zero_rate"] = zero_count / len(cols)
    return features


def build_selected_missing_indicator_features(
    df: pd.DataFrame,
    selected_columns: list[str],
) -> pd.DataFrame:
    """构造筛选后的 missing indicator 特征。"""

    features = pd.DataFrame(index=df.index)
    for col in selected_columns:
        features[f"missing_{col}"] = df[col].isna().astype(int)
    return features


def build_selected_missing_indicator_summary(
    train_inner_df: pd.DataFrame,
    cfg: ScaniaConfig,
    structural_config: dict[str, Any],
    target_col: str = "target",
) -> pd.DataFrame:
    """只基于 train_inner 汇总 missing indicator 候选字段。"""

    section = _structural_section(structural_config)
    indicator_cfg = section["selected_missing_indicators"]
    min_missing_rate = float(indicator_cfg["min_missing_rate"])
    min_diff = float(indicator_cfg["min_abs_pos_neg_missing_diff"])
    max_features = int(indicator_cfg["max_selected_features"])

    feature_cols = _numeric_feature_columns(train_inner_df, cfg, target_col=target_col)
    pos_mask = train_inner_df[target_col].eq(1)
    neg_mask = train_inner_df[target_col].eq(0)
    rows: list[dict[str, Any]] = []

    for col in feature_cols:
        missing = train_inner_df[col].isna()
        missing_rate = float(missing.mean())
        pos_missing_rate = float(missing[pos_mask].mean()) if pos_mask.any() else np.nan
        neg_missing_rate = float(missing[neg_mask].mean()) if neg_mask.any() else np.nan
        diff = abs(pos_missing_rate - neg_missing_rate)
        if missing_rate >= min_missing_rate and diff >= min_diff:
            rows.append(
                {
                    "feature_name": col,
                    "missing_rate": missing_rate,
                    "pos_missing_rate": pos_missing_rate,
                    "neg_missing_rate": neg_missing_rate,
                    "missing_rate_diff_abs": diff,
                    "selection_rule": (
                        f"missing_rate >= {min_missing_rate} and "
                        f"abs(pos-neg missing rate) >= {min_diff}"
                    ),
                }
            )

    summary = pd.DataFrame(rows)
    if summary.empty:
        return pd.DataFrame(
            columns=[
                "selection_rank",
                "feature_name",
                "missing_rate",
                "pos_missing_rate",
                "neg_missing_rate",
                "missing_rate_diff_abs",
                "selection_rule",
            ]
        )

    summary = summary.sort_values(
        ["missing_rate_diff_abs", "missing_rate"],
        ascending=[False, False],
    ).head(max_features)
    summary.insert(0, "selection_rank", range(1, len(summary) + 1))
    return summary.reset_index(drop=True)


def select_missing_indicator_columns(
    train_inner_df: pd.DataFrame,
    cfg: ScaniaConfig,
    structural_config: dict[str, Any],
    target_col: str = "target",
) -> list[str]:
    """只基于 train_inner 选择 missing indicator 字段。"""

    summary = build_selected_missing_indicator_summary(
        train_inner_df=train_inner_df,
        cfg=cfg,
        structural_config=structural_config,
        target_col=target_col,
    )
    return summary["feature_name"].tolist()


def fit_structural_feature_builder(
    train_inner_df: pd.DataFrame,
    cfg: ScaniaConfig,
    structural_config: dict[str, Any],
    feature_group: str,
    target_col: str = "target",
) -> StructuralFeatureBuilder:
    """在 train_inner 上拟合结构特征规则。"""

    if target_col not in train_inner_df.columns:
        raise ValueError(f"缺少 target 列：{target_col}")

    feature_cols = _numeric_feature_columns(train_inner_df, cfg, target_col=target_col)
    prefix_all = _build_prefix_members(
        feature_cols,
        _candidate_prefixes(structural_config, include_low_priority=True),
    )
    prefix_core = _build_prefix_members(
        feature_cols,
        _candidate_prefixes(structural_config, include_low_priority=False),
    )

    use_selected_indicators = feature_group in {
        "median_all_selected_missing_indicators_top30",
        "median_all_structural_core",
        "median_all_structural_all",
    }
    selected_columns = (
        select_missing_indicator_columns(train_inner_df, cfg, structural_config, target_col)
        if use_selected_indicators
        else []
    )

    kwargs: dict[str, Any] = {
        "feature_group": feature_group,
        "feature_cols": feature_cols,
        "prefix_missing_members": {},
        "prefix_zero_members": {},
        "selected_missing_indicator_columns": selected_columns,
        "metadata": {
            "fit_dataset": "train_inner",
            "uses_official_test_for_selection": False,
            "n_original_features": len(feature_cols),
            "n_selected_missing_indicators": len(selected_columns),
        },
    }

    if feature_group == "baseline_median_all":
        pass
    elif feature_group == "median_all_sample_missing_rate":
        kwargs["include_sample_missing_rate"] = True
    elif feature_group == "median_all_sample_zero_rate":
        kwargs["include_sample_zero_rate"] = True
    elif feature_group == "median_all_selected_missing_indicators_top30":
        pass
    elif feature_group == "median_all_prefix_zero_rate":
        kwargs["prefix_zero_members"] = prefix_core
        kwargs["include_prefix_zero_rate"] = True
    elif feature_group == "median_all_prefix_missing_rate":
        kwargs["prefix_missing_members"] = prefix_all
        kwargs["include_prefix_missing_rate"] = True
    elif feature_group == "median_all_structural_core":
        kwargs["include_sample_missing_rate"] = True
        kwargs["prefix_zero_members"] = prefix_core
        kwargs["include_prefix_zero_rate"] = True
    elif feature_group == "median_all_structural_all":
        kwargs.update(
            {
                "include_sample_missing_rate": True,
                "include_sample_missing_count": True,
                "include_sample_non_missing_count": True,
                "include_sample_zero_rate": True,
                "include_sample_zero_count": True,
                "include_sample_non_zero_count": True,
                "prefix_missing_members": prefix_all,
                "prefix_zero_members": prefix_core,
                "include_prefix_missing_rate": True,
                "include_prefix_missing_count": True,
                "include_prefix_zero_rate": True,
                "include_prefix_zero_count": True,
            }
        )
    else:
        raise ValueError(f"不支持的结构特征实验组：{feature_group}")

    return StructuralFeatureBuilder(**kwargs)


def transform_structural_features(
    df: pd.DataFrame,
    builder: StructuralFeatureBuilder,
    feature_group: str | None = None,
) -> pd.DataFrame:
    """按 train_inner 拟合出的 builder 生成结构特征。"""

    if feature_group is not None and feature_group != builder.feature_group:
        raise ValueError(
            f"feature_group 与 builder 不一致：{feature_group} != {builder.feature_group}"
        )

    source = df.copy(deep=False)
    frames: list[pd.DataFrame] = []

    if builder.include_sample_missing_rate:
        frames.append(
            build_sample_missing_features(
                source,
                builder.feature_cols,
                include_count=builder.include_sample_missing_count,
                include_non_missing_count=builder.include_sample_non_missing_count,
            )
        )

    if builder.include_sample_zero_rate:
        frames.append(
            build_sample_zero_features(
                source,
                builder.feature_cols,
                include_count=builder.include_sample_zero_count,
                include_non_zero_count=builder.include_sample_non_zero_count,
            )
        )

    if builder.include_prefix_missing_rate or builder.include_prefix_missing_count:
        frames.append(
            build_prefix_missing_features(
                source,
                builder.prefix_missing_members,
                include_count=builder.include_prefix_missing_count,
                include_rate=builder.include_prefix_missing_rate,
            )
        )

    if builder.include_prefix_zero_rate or builder.include_prefix_zero_count:
        frames.append(
            build_prefix_zero_features(
                source,
                builder.prefix_zero_members,
                include_count=builder.include_prefix_zero_count,
                include_rate=builder.include_prefix_zero_rate,
            )
        )

    if builder.selected_missing_indicator_columns:
        frames.append(
            build_selected_missing_indicator_features(
                source,
                builder.selected_missing_indicator_columns,
            )
        )

    if not frames:
        return pd.DataFrame(index=df.index)

    return pd.concat(frames, axis=1)
