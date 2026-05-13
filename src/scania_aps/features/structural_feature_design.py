"""结构特征方案设计表生成工具。

本模块只生成结构特征设计说明，不生成特征矩阵，也不训练模型。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml


DESIGN_COLUMNS = [
    "feature_family",
    "feature_name",
    "source_columns_or_prefix",
    "calculation_method",
    "fit_data",
    "transform_data",
    "selection_rule",
    "priority",
    "expected_signal",
    "risk_or_limitation",
    "use_in_day13_first_round",
]


def load_structural_feature_config(config_path: str | Path) -> dict[str, Any]:
    """读取结构特征设计配置。"""

    with Path(config_path).open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    if not config or "structural_features" not in config:
        raise ValueError("structural_features.yaml 缺少 structural_features 配置段。")
    return config["structural_features"]


def _priority_for_prefix(prefix: str, structural_config: dict[str, Any]) -> str:
    """根据配置返回 prefix 优先级。"""

    groups = structural_config["candidate_prefix_groups"]
    if prefix in groups.get("high_priority", []):
        return "high"
    if prefix in groups.get("medium_priority", []):
        return "medium"
    if prefix in groups.get("low_priority", []):
        return "low"
    return "low"


def _candidate_prefixes(structural_config: dict[str, Any]) -> list[str]:
    """按优先级合并候选 prefix。"""

    groups = structural_config["candidate_prefix_groups"]
    return (
        list(groups.get("high_priority", []))
        + list(groups.get("medium_priority", []))
        + list(groups.get("low_priority", []))
    )


def _add_row(rows: list[dict[str, Any]], **kwargs: Any) -> None:
    """按固定列追加一行设计。"""

    row = {column: kwargs.get(column) for column in DESIGN_COLUMNS}
    rows.append(row)


def select_missing_indicator_candidates(
    missing_zero_summary: pd.DataFrame,
    pos_neg_diff: pd.DataFrame,
    structural_config: dict[str, Any],
    reference_dataset: str = "train_inner",
) -> pd.DataFrame:
    """基于 train_inner 规则筛选 missing indicator 候选字段。"""

    settings = structural_config["selected_missing_indicators"]
    missing_ref = missing_zero_summary[missing_zero_summary["dataset"].eq(reference_dataset)]
    merged = missing_ref[["feature_name", "missing_rate"]].merge(
        pos_neg_diff[["feature_name", "missing_rate_diff_abs"]],
        on="feature_name",
        how="inner",
    )
    candidates = merged[
        (merged["missing_rate"] >= settings["min_missing_rate"])
        & (merged["missing_rate_diff_abs"] >= settings["min_abs_pos_neg_missing_diff"])
    ].copy()
    candidates = candidates.sort_values(
        ["missing_rate_diff_abs", "missing_rate"],
        ascending=[False, False],
    )
    return candidates.head(int(settings["max_selected_features"])).reset_index(drop=True)


def _add_sample_missing_rows(rows: list[dict[str, Any]]) -> None:
    """添加样本级缺失统计设计。"""

    definitions = [
        ("sample_missing_count", "count missing values per row"),
        ("sample_missing_rate", "missing count / numeric feature count"),
        ("sample_non_missing_count", "numeric feature count - missing count"),
    ]
    for feature_name, method in definitions:
        _add_row(
            rows,
            feature_family="sample_missing_summary",
            feature_name=feature_name,
            source_columns_or_prefix="all numeric features",
            calculation_method=method,
            fit_data="train_inner only for numeric feature list",
            transform_data="train_inner/valid/official_test with same feature list",
            selection_rule="no supervised selection",
            priority="high",
            expected_signal="sample-level data completeness",
            risk_or_limitation="may reflect general data quality rather than APS-specific signal",
            use_in_day13_first_round=True,
        )


def _add_sample_zero_rows(rows: list[dict[str, Any]]) -> None:
    """添加样本级零值统计设计。"""

    definitions = [
        ("sample_zero_count", "count zero values per row"),
        ("sample_zero_rate", "zero count / numeric feature count"),
        ("sample_non_zero_count", "numeric feature count - zero count"),
    ]
    for feature_name, method in definitions:
        _add_row(
            rows,
            feature_family="sample_zero_summary",
            feature_name=feature_name,
            source_columns_or_prefix="all numeric features",
            calculation_method=method,
            fit_data="train_inner only for numeric feature list",
            transform_data="train_inner/valid/official_test with same feature list",
            selection_rule="no supervised selection",
            priority="high",
            expected_signal="sample-level zero pattern",
            risk_or_limitation="zero may represent normal inactive state or anonymized encoding",
            use_in_day13_first_round=True,
        )


def _add_prefix_missing_rows(
    rows: list[dict[str, Any]],
    prefix_group_summary: pd.DataFrame,
    structural_config: dict[str, Any],
) -> None:
    """添加前缀组缺失聚合设计。"""

    for prefix in _candidate_prefixes(structural_config):
        matched = prefix_group_summary[prefix_group_summary["prefix"].eq(prefix)]
        source = matched["feature_names"].iloc[0] if not matched.empty else f"{prefix}_*"
        priority = _priority_for_prefix(prefix, structural_config)
        for suffix, method in [
            ("missing_count", f"count missing values within {prefix} group"),
            ("missing_rate", f"missing count / {prefix} group feature count"),
        ]:
            _add_row(
                rows,
                feature_family="prefix_missing_summary",
                feature_name=f"prefix_{prefix}_{suffix}",
                source_columns_or_prefix=source,
                calculation_method=method,
                fit_data="prefix membership from train_inner schema",
                transform_data="train_inner/valid/official_test with same prefix members",
                selection_rule="prefix selected from Day11 multi-feature prefix analysis",
                priority=priority,
                expected_signal=f"{prefix} group missing structure",
                risk_or_limitation="anonymous prefix, no physical meaning",
                use_in_day13_first_round=True,
            )


def _add_prefix_zero_rows(
    rows: list[dict[str, Any]],
    prefix_group_summary: pd.DataFrame,
    structural_config: dict[str, Any],
) -> None:
    """添加前缀组零值聚合设计。"""

    groups = structural_config["candidate_prefix_groups"]
    prefixes = list(groups.get("high_priority", [])) + list(groups.get("medium_priority", []))
    for prefix in prefixes:
        matched = prefix_group_summary[prefix_group_summary["prefix"].eq(prefix)]
        source = matched["feature_names"].iloc[0] if not matched.empty else f"{prefix}_*"
        priority = _priority_for_prefix(prefix, structural_config)
        for suffix, method in [
            ("zero_count", f"count zero values within {prefix} group"),
            ("zero_rate", f"zero count / {prefix} group feature count"),
        ]:
            _add_row(
                rows,
                feature_family="prefix_zero_summary",
                feature_name=f"prefix_{prefix}_{suffix}",
                source_columns_or_prefix=source,
                calculation_method=method,
                fit_data="prefix membership from train_inner schema",
                transform_data="train_inner/valid/official_test with same prefix members",
                selection_rule="prefix selected from Day11 zero-structure signal",
                priority=priority,
                expected_signal=f"{prefix} group zero structure",
                risk_or_limitation="anonymous prefix, no physical meaning",
                use_in_day13_first_round=True,
            )


def _add_selected_missing_indicator_rows(
    rows: list[dict[str, Any]],
    missing_indicator_candidates: pd.DataFrame,
    structural_config: dict[str, Any],
) -> None:
    """添加筛选后的 missing indicator 设计。"""

    settings = structural_config["selected_missing_indicators"]
    rule = (
        f"missing_rate >= {settings['min_missing_rate']} and "
        f"abs(pos_missing_rate - neg_missing_rate) >= "
        f"{settings['min_abs_pos_neg_missing_diff']}"
    )
    for _, row in missing_indicator_candidates.iterrows():
        source = row["feature_name"]
        _add_row(
            rows,
            feature_family="selected_missing_indicators",
            feature_name=f"missing_{source}",
            source_columns_or_prefix=source,
            calculation_method=f"is_missing({source})",
            fit_data="train_inner missing rate and pos/neg missing difference",
            transform_data="train_inner/valid/official_test using same selected fields",
            selection_rule=rule,
            priority="high",
            expected_signal="strong pos/neg missing difference",
            risk_or_limitation="single-field indicator may overfit and needs validation",
            use_in_day13_first_round=True,
        )


def _add_optional_outlier_rows(rows: list[dict[str, Any]], structural_config: dict[str, Any]) -> None:
    """添加可选异常/长尾统计设计，默认不进入第一轮。"""

    settings = structural_config["outlier_features"]
    high_q = settings["quantile_high"]
    optional_rows = [
        (
            "sample_outlier_count_p99",
            "all numeric features",
            f"count values above train_inner q{high_q}",
        ),
        (
            "sample_outlier_rate_p99",
            "all numeric features",
            f"outlier count / numeric feature count using train_inner q{high_q}",
        ),
        (
            "prefix_az_outlier_count",
            "az_*",
            f"count az group values above train_inner q{high_q}",
        ),
        (
            "prefix_cs_outlier_count",
            "cs_*",
            f"count cs group values above train_inner q{high_q}",
        ),
    ]
    for feature_name, source, method in optional_rows:
        _add_row(
            rows,
            feature_family="optional_outlier_summary",
            feature_name=feature_name,
            source_columns_or_prefix=source,
            calculation_method=method,
            fit_data="outlier thresholds fit on train_inner quantiles only",
            transform_data="train_inner/valid/official_test with same thresholds",
            selection_rule="optional second-round design, disabled in first round",
            priority="low",
            expected_signal="long-tail and extreme-value structure",
            risk_or_limitation="may be noisy; not included in Day13 first round",
            use_in_day13_first_round=False,
        )


def build_structural_feature_design_table(
    missing_zero_summary: pd.DataFrame,
    pos_neg_diff: pd.DataFrame,
    prefix_group_summary: pd.DataFrame,
    structural_config: dict[str, Any],
) -> pd.DataFrame:
    """基于 Day 10/Day 11 结果生成结构特征设计表。"""

    rows: list[dict[str, Any]] = []
    if structural_config["sample_level_features"]["enable_missing_summary"]:
        _add_sample_missing_rows(rows)
    if structural_config["sample_level_features"]["enable_zero_summary"]:
        _add_sample_zero_rows(rows)
    if structural_config["prefix_level_features"]["enable_prefix_missing_summary"]:
        _add_prefix_missing_rows(rows, prefix_group_summary, structural_config)
    if structural_config["prefix_level_features"]["enable_prefix_zero_summary"]:
        _add_prefix_zero_rows(rows, prefix_group_summary, structural_config)

    missing_candidates = select_missing_indicator_candidates(
        missing_zero_summary,
        pos_neg_diff,
        structural_config,
    )
    _add_selected_missing_indicator_rows(rows, missing_candidates, structural_config)
    _add_optional_outlier_rows(rows, structural_config)

    return pd.DataFrame(rows, columns=DESIGN_COLUMNS)
