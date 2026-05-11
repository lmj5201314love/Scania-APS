"""匿名字段前缀组结构信号分析工具。

字段前缀只作为匿名结构分组线索，不代表任何具体物理含义。
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def extract_feature_prefix(feature_name: str) -> str:
    """从字段名中提取下划线前的匿名前缀。"""

    if "_" in feature_name:
        prefix = feature_name.split("_", 1)[0]
        return prefix if prefix else feature_name
    return feature_name[:2] if len(feature_name) > 2 else feature_name


def add_prefix_column(
    feature_df: pd.DataFrame,
    feature_col: str = "feature_name",
) -> pd.DataFrame:
    """给字段级统计表增加 prefix 列，不修改原始 DataFrame。"""

    if feature_col not in feature_df.columns:
        raise ValueError(f"缺少字段列：{feature_col}")

    result = feature_df.copy()
    result["prefix"] = result[feature_col].astype(str).map(extract_feature_prefix)
    return result


def _reference_distribution(
    distribution_summary: pd.DataFrame,
    reference_dataset: str,
) -> pd.DataFrame:
    """取 reference_dataset 的字段分布统计。"""

    if "dataset" not in distribution_summary.columns:
        raise ValueError("distribution_summary 缺少 dataset 列。")
    ref = distribution_summary[distribution_summary["dataset"].eq(reference_dataset)].copy()
    if ref.empty:
        raise ValueError(f"distribution_summary 中不存在数据集：{reference_dataset}")
    ref["abs_skew"] = ref["skew"].abs()
    return add_prefix_column(ref)


def _join_prefix_sources(
    distribution_summary: pd.DataFrame,
    missing_zero_summary: pd.DataFrame,
    pos_neg_diff: pd.DataFrame,
    drift_summary: pd.DataFrame,
    reference_dataset: str,
) -> pd.DataFrame:
    """合并字段级统计来源，准备 prefix 聚合。"""

    dist_ref = _reference_distribution(distribution_summary, reference_dataset)
    missing_ref = add_prefix_column(
        missing_zero_summary[missing_zero_summary["dataset"].eq(reference_dataset)].copy()
    )
    pos_neg = add_prefix_column(pos_neg_diff)
    drift = add_prefix_column(drift_summary)

    base = dist_ref[
        [
            "feature_name",
            "prefix",
            "abs_skew",
            "p99_to_median_ratio",
            "max_to_p99_ratio",
        ]
    ].merge(
        missing_ref[
            [
                "feature_name",
                "missing_rate",
                "zero_rate",
                "near_zero_rate",
            ]
        ],
        on="feature_name",
        how="left",
    )
    base = base.merge(
        pos_neg[
            [
                "feature_name",
                "missing_rate_diff_abs",
                "zero_rate_diff_abs",
            ]
        ],
        on="feature_name",
        how="left",
    )
    base = base.merge(
        drift[
            [
                "feature_name",
                "train_test_missing_diff_abs",
                "train_test_p99_diff_abs",
            ]
        ],
        on="feature_name",
        how="left",
    )
    return base


def _feature_names(features: pd.Series) -> str:
    """拼接组内字段名，方便人工阅读。"""

    return ",".join(sorted(features.astype(str).tolist()))


def build_prefix_group_summary(
    distribution_summary: pd.DataFrame,
    missing_zero_summary: pd.DataFrame,
    pos_neg_diff: pd.DataFrame,
    drift_summary: pd.DataFrame,
    reference_dataset: str = "train_inner",
) -> pd.DataFrame:
    """基于字段级 Day 10 结果构建 prefix 组统计表。"""

    merged = _join_prefix_sources(
        distribution_summary=distribution_summary,
        missing_zero_summary=missing_zero_summary,
        pos_neg_diff=pos_neg_diff,
        drift_summary=drift_summary,
        reference_dataset=reference_dataset,
    )

    grouped = (
        merged.groupby("prefix", as_index=False)
        .agg(
            feature_count=("feature_name", "size"),
            feature_names=("feature_name", _feature_names),
            avg_missing_rate=("missing_rate", "mean"),
            median_missing_rate=("missing_rate", "median"),
            max_missing_rate=("missing_rate", "max"),
            high_missing_feature_count_50=("missing_rate", lambda x: int((x >= 0.50).sum())),
            high_missing_feature_count_80=("missing_rate", lambda x: int((x >= 0.80).sum())),
            avg_zero_rate=("zero_rate", "mean"),
            median_zero_rate=("zero_rate", "median"),
            max_zero_rate=("zero_rate", "max"),
            high_zero_feature_count_50=("zero_rate", lambda x: int((x >= 0.50).sum())),
            high_zero_feature_count_90=("zero_rate", lambda x: int((x >= 0.90).sum())),
            avg_abs_pos_neg_missing_diff=("missing_rate_diff_abs", "mean"),
            max_abs_pos_neg_missing_diff=("missing_rate_diff_abs", "max"),
            avg_abs_pos_neg_zero_diff=("zero_rate_diff_abs", "mean"),
            max_abs_pos_neg_zero_diff=("zero_rate_diff_abs", "max"),
            avg_abs_skew=("abs_skew", "mean"),
            max_abs_skew=("abs_skew", "max"),
            avg_train_test_missing_diff=("train_test_missing_diff_abs", "mean"),
            max_train_test_missing_diff=("train_test_missing_diff_abs", "max"),
            avg_train_test_p99_diff=("train_test_p99_diff_abs", "mean"),
            max_train_test_p99_diff=("train_test_p99_diff_abs", "max"),
        )
        .sort_values(["feature_count", "prefix"], ascending=[False, True])
        .reset_index(drop=True)
    )
    return grouped


def _normalized(series: pd.Series, *, log_scale: bool = False) -> pd.Series:
    """将指标归一化到 0-1，便于构造综合分数。"""

    values = series.astype(float).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    if log_scale:
        values = np.log1p(values.clip(lower=0.0))
    max_value = values.max()
    if max_value <= 0:
        return pd.Series(0.0, index=series.index)
    return values / max_value


def _recommend(
    signal_score: float,
    drift_risk_score: float,
    feature_count: int,
    signal_high: float,
    drift_high: float,
) -> str:
    """根据 signal 和 drift 给出结构特征候选建议。"""

    if feature_count < 2:
        return "单字段前缀，不适合作为前缀聚合主线"
    if signal_score >= signal_high and drift_risk_score < drift_high:
        return "适合 Day 12 作为前缀聚合候选"
    if signal_score >= signal_high and drift_risk_score >= drift_high:
        return "信号较强但 drift 偏高，谨慎观察"
    return "组内信号一般，可作为前缀聚合备选"


def build_prefix_group_signal_ranking(prefix_group_summary: pd.DataFrame) -> pd.DataFrame:
    """对 prefix 组按结构信号强度排序，并给出建议。"""

    summary = prefix_group_summary.copy()
    signal_parts = pd.concat(
        [
            _normalized(summary["avg_abs_pos_neg_missing_diff"]),
            _normalized(summary["avg_abs_pos_neg_zero_diff"]),
            _normalized(summary["avg_missing_rate"]),
            _normalized(summary["avg_zero_rate"]),
            _normalized(summary["avg_abs_skew"], log_scale=True),
        ],
        axis=1,
    )
    drift_parts = pd.concat(
        [
            _normalized(summary["avg_train_test_missing_diff"]),
            _normalized(summary["avg_train_test_p99_diff"], log_scale=True),
        ],
        axis=1,
    )
    summary["signal_score"] = signal_parts.mean(axis=1)
    summary["drift_risk_score"] = drift_parts.mean(axis=1)

    signal_high = summary["signal_score"].quantile(0.75)
    drift_high = summary["drift_risk_score"].quantile(0.50)
    summary["recommendation"] = [
        _recommend(signal, drift, feature_count, signal_high, drift_high)
        for signal, drift, feature_count in zip(
            summary["signal_score"],
            summary["drift_risk_score"],
            summary["feature_count"],
        )
    ]

    cols = [
        "prefix",
        "feature_count",
        "signal_score",
        "drift_risk_score",
        "avg_missing_rate",
        "avg_zero_rate",
        "avg_abs_pos_neg_missing_diff",
        "avg_abs_pos_neg_zero_diff",
        "avg_abs_skew",
        "recommendation",
    ]
    return summary[cols].sort_values(
        ["signal_score", "drift_risk_score"],
        ascending=[False, True],
    ).reset_index(drop=True)


def build_prefix_feature_members(prefix_group_summary: pd.DataFrame) -> pd.DataFrame:
    """展开 prefix 与组内 feature_name 明细。"""

    rows = []
    required_cols = {"prefix", "feature_names", "feature_count"}
    missing = required_cols.difference(prefix_group_summary.columns)
    if missing:
        raise ValueError(f"prefix_group_summary 缺少必要列：{sorted(missing)}")

    for _, row in prefix_group_summary.iterrows():
        features = [feature for feature in str(row["feature_names"]).split(",") if feature]
        for feature in features:
            rows.append(
                {
                    "prefix": row["prefix"],
                    "feature_name": feature,
                    "group_feature_count": int(row["feature_count"]),
                }
            )
    return pd.DataFrame(rows)
