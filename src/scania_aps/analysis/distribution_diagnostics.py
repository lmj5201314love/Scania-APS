"""字段级分布诊断工具。

本模块只做统计诊断，不训练模型、不生成新特征，也不修改输入 DataFrame。
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd


EPSILON = 1e-8


def get_numeric_feature_columns(
    df: pd.DataFrame,
    label_col: str,
    target_col: str = "target",
) -> list[str]:
    """返回数值特征列，排除标签列和 target 列。"""

    excluded = {label_col, target_col}
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    return [col for col in numeric_cols if col not in excluded]


def _safe_rate(count: int | float, total: int) -> float:
    """计算安全比例。"""

    return float(count) / total if total else np.nan


def _safe_ratio(numerator: float, denominator: float) -> float:
    """计算长尾比例，分母为 0 或缺失时返回 NaN。"""

    if pd.isna(numerator) or pd.isna(denominator) or abs(float(denominator)) <= EPSILON:
        return np.nan
    return abs(float(numerator)) / abs(float(denominator))


def _series_stats(series: pd.Series) -> dict[str, float | int]:
    """对单个字段计算缺失、零值、分位数和长尾统计。"""

    values = pd.to_numeric(series, errors="coerce")
    total_count = len(values)
    non_missing = values.dropna()
    non_missing_count = int(non_missing.shape[0])
    missing_count = int(total_count - non_missing_count)

    zero_count = int((non_missing == 0).sum())
    near_zero_count = int((non_missing.abs() <= EPSILON).sum())

    stats: dict[str, float | int] = {
        "non_missing_count": non_missing_count,
        "missing_count": missing_count,
        "missing_rate": _safe_rate(missing_count, total_count),
        "zero_count": zero_count,
        "zero_rate": _safe_rate(zero_count, total_count),
        "near_zero_count": near_zero_count,
        "near_zero_rate": _safe_rate(near_zero_count, total_count),
        "unique_count": int(non_missing.nunique(dropna=True)),
    }

    if non_missing_count == 0:
        stats.update(
            {
                "mean": np.nan,
                "std": np.nan,
                "min": np.nan,
                "p01": np.nan,
                "p05": np.nan,
                "median": np.nan,
                "p95": np.nan,
                "p99": np.nan,
                "max": np.nan,
                "skew": np.nan,
                "p99_to_median_ratio": np.nan,
                "max_to_p99_ratio": np.nan,
            }
        )
        return stats

    quantiles = non_missing.quantile([0.01, 0.05, 0.50, 0.95, 0.99])
    median = float(quantiles.loc[0.50])
    p99 = float(quantiles.loc[0.99])
    max_value = float(non_missing.max())

    stats.update(
        {
            "mean": float(non_missing.mean()),
            "std": float(non_missing.std(ddof=1)) if non_missing_count > 1 else 0.0,
            "min": float(non_missing.min()),
            "p01": float(quantiles.loc[0.01]),
            "p05": float(quantiles.loc[0.05]),
            "median": median,
            "p95": float(quantiles.loc[0.95]),
            "p99": p99,
            "max": max_value,
            "skew": float(non_missing.skew()) if non_missing_count >= 3 else np.nan,
            "p99_to_median_ratio": _safe_ratio(p99, median),
            "max_to_p99_ratio": _safe_ratio(max_value, p99),
        }
    )
    return stats


def build_feature_distribution_summary(
    df: pd.DataFrame,
    feature_cols: Iterable[str],
    dataset_name: str,
) -> pd.DataFrame:
    """构建字段级分布统计表。"""

    rows = []
    for feature in feature_cols:
        stats = _series_stats(df[feature])
        rows.append({"dataset": dataset_name, "feature_name": feature, **stats})
    return pd.DataFrame(rows)


def build_missing_zero_summary(
    df: pd.DataFrame,
    feature_cols: Iterable[str],
    dataset_name: str,
) -> pd.DataFrame:
    """构建字段级缺失率、零值率和近似零值率统计表。"""

    rows = []
    total_count = len(df)
    for feature in feature_cols:
        values = pd.to_numeric(df[feature], errors="coerce")
        non_missing = values.dropna()
        rows.append(
            {
                "dataset": dataset_name,
                "feature_name": feature,
                "missing_rate": _safe_rate(values.isna().sum(), total_count),
                "zero_rate": _safe_rate((non_missing == 0).sum(), total_count),
                "near_zero_rate": _safe_rate((non_missing.abs() <= EPSILON).sum(), total_count),
                "non_missing_count": int(non_missing.shape[0]),
            }
        )
    return pd.DataFrame(rows)


def _split_pos_neg(
    train_df: pd.DataFrame,
    label_col: str,
    target_col: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """按 target 或 class 标签拆分 neg/pos 样本。"""

    if target_col in train_df.columns:
        neg_df = train_df[train_df[target_col] == 0]
        pos_df = train_df[train_df[target_col] == 1]
    elif label_col in train_df.columns:
        neg_df = train_df[train_df[label_col] == "neg"]
        pos_df = train_df[train_df[label_col] == "pos"]
    else:
        raise ValueError(f"缺少标签列：{label_col} 或 {target_col}")

    if neg_df.empty or pos_df.empty:
        raise ValueError("pos/neg 任一类别为空，无法计算分布差异。")

    return neg_df, pos_df


def _group_feature_stats(df: pd.DataFrame, feature: str) -> dict[str, float]:
    """计算某个类别内单字段的核心分布统计。"""

    values = pd.to_numeric(df[feature], errors="coerce")
    total_count = len(values)
    non_missing = values.dropna()
    return {
        "missing_rate": _safe_rate(values.isna().sum(), total_count),
        "zero_rate": _safe_rate((non_missing == 0).sum(), total_count),
        "median": float(non_missing.median()) if not non_missing.empty else np.nan,
        "p95": float(non_missing.quantile(0.95)) if not non_missing.empty else np.nan,
        "p99": float(non_missing.quantile(0.99)) if not non_missing.empty else np.nan,
        "std": float(non_missing.std(ddof=1)) if non_missing.shape[0] > 1 else 0.0,
    }


def build_pos_neg_distribution_diff(
    train_df: pd.DataFrame,
    feature_cols: Iterable[str],
    label_col: str,
    target_col: str = "target",
) -> pd.DataFrame:
    """基于训练侧数据计算 pos/neg 的缺失、零值和分位数差异。"""

    neg_df, pos_df = _split_pos_neg(train_df, label_col, target_col)
    rows = []

    for feature in feature_cols:
        neg_stats = _group_feature_stats(neg_df, feature)
        pos_stats = _group_feature_stats(pos_df, feature)
        pooled_std = np.nanmean([neg_stats["std"], pos_stats["std"]])
        median_diff = abs(pos_stats["median"] - neg_stats["median"])
        standardized_median_diff = (
            median_diff / pooled_std if not pd.isna(pooled_std) and pooled_std > EPSILON else np.nan
        )

        rows.append(
            {
                "feature_name": feature,
                "neg_missing_rate": neg_stats["missing_rate"],
                "pos_missing_rate": pos_stats["missing_rate"],
                "missing_rate_diff_abs": abs(
                    pos_stats["missing_rate"] - neg_stats["missing_rate"]
                ),
                "neg_zero_rate": neg_stats["zero_rate"],
                "pos_zero_rate": pos_stats["zero_rate"],
                "zero_rate_diff_abs": abs(pos_stats["zero_rate"] - neg_stats["zero_rate"]),
                "neg_median": neg_stats["median"],
                "pos_median": pos_stats["median"],
                "median_diff_abs": median_diff,
                "neg_p95": neg_stats["p95"],
                "pos_p95": pos_stats["p95"],
                "p95_diff_abs": abs(pos_stats["p95"] - neg_stats["p95"]),
                "neg_p99": neg_stats["p99"],
                "pos_p99": pos_stats["p99"],
                "p99_diff_abs": abs(pos_stats["p99"] - neg_stats["p99"]),
                "standardized_median_diff": standardized_median_diff,
            }
        )

    return pd.DataFrame(rows)


def _distribution_snapshot(df: pd.DataFrame, feature: str) -> dict[str, float]:
    """计算漂移对比所需的单数据集快照。"""

    values = pd.to_numeric(df[feature], errors="coerce")
    non_missing = values.dropna()
    return {
        "missing_rate": _safe_rate(values.isna().sum(), len(values)),
        "median": float(non_missing.median()) if not non_missing.empty else np.nan,
        "p99": float(non_missing.quantile(0.99)) if not non_missing.empty else np.nan,
    }


def build_train_valid_test_drift_summary(
    train_inner_df: pd.DataFrame,
    valid_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_cols: Iterable[str],
) -> pd.DataFrame:
    """比较 train_inner、valid 和 official test 的分布差异。"""

    rows = []
    for feature in feature_cols:
        train_stats = _distribution_snapshot(train_inner_df, feature)
        valid_stats = _distribution_snapshot(valid_df, feature)
        test_stats = _distribution_snapshot(test_df, feature)

        rows.append(
            {
                "feature_name": feature,
                "train_inner_missing_rate": train_stats["missing_rate"],
                "valid_missing_rate": valid_stats["missing_rate"],
                "test_missing_rate": test_stats["missing_rate"],
                "train_valid_missing_diff_abs": abs(
                    train_stats["missing_rate"] - valid_stats["missing_rate"]
                ),
                "train_test_missing_diff_abs": abs(
                    train_stats["missing_rate"] - test_stats["missing_rate"]
                ),
                "train_inner_median": train_stats["median"],
                "valid_median": valid_stats["median"],
                "test_median": test_stats["median"],
                "train_valid_median_diff_abs": abs(
                    valid_stats["median"] - train_stats["median"]
                ),
                "train_test_median_diff_abs": abs(test_stats["median"] - train_stats["median"]),
                "train_inner_p99": train_stats["p99"],
                "valid_p99": valid_stats["p99"],
                "test_p99": test_stats["p99"],
                "train_valid_p99_diff_abs": abs(valid_stats["p99"] - train_stats["p99"]),
                "train_test_p99_diff_abs": abs(test_stats["p99"] - train_stats["p99"]),
            }
        )

    return pd.DataFrame(rows)


def _top_rows(
    df: pd.DataFrame,
    *,
    sort_col: str,
    diagnostic_type: str,
    top_n: int,
    notes: str,
    value_abs: bool = False,
) -> pd.DataFrame:
    """整理 Top N 诊断行。"""

    values = df.copy()
    values["metric_value"] = values[sort_col].abs() if value_abs else values[sort_col]
    values = values.replace([np.inf, -np.inf], np.nan).dropna(subset=["metric_value"])
    values = values.sort_values("metric_value", ascending=False).head(top_n)
    return pd.DataFrame(
        {
            "diagnostic_type": diagnostic_type,
            "rank": range(1, len(values) + 1),
            "feature_name": values["feature_name"].to_list(),
            "metric_value": values["metric_value"].to_list(),
            "notes": notes,
        }
    )


def _build_drift_score(drift_summary: pd.DataFrame) -> pd.DataFrame:
    """构建 train/test 漂移综合分数，避免单纯被字段量纲支配。"""

    drift = drift_summary.copy()
    median_scale = drift[["train_inner_median", "test_median"]].abs().max(axis=1).clip(lower=1.0)
    p99_scale = drift[["train_inner_p99", "test_p99"]].abs().max(axis=1).clip(lower=1.0)
    drift["train_test_drift_score"] = np.nanmax(
        np.vstack(
            [
                drift["train_test_missing_diff_abs"].to_numpy(),
                (drift["train_test_median_diff_abs"] / median_scale).to_numpy(),
                (drift["train_test_p99_diff_abs"] / p99_scale).to_numpy(),
            ]
        ),
        axis=0,
    )
    return drift


def build_top_feature_diagnostics(
    distribution_summary: pd.DataFrame,
    missing_zero_summary: pd.DataFrame,
    pos_neg_diff: pd.DataFrame,
    drift_summary: pd.DataFrame,
    top_n: int = 20,
    reference_dataset: str = "train_inner",
) -> pd.DataFrame:
    """综合输出高缺失、高零值、高偏态、类别差异和分布漂移 Top 特征。"""

    dist_ref = distribution_summary[distribution_summary["dataset"].eq(reference_dataset)]
    miss_ref = missing_zero_summary[missing_zero_summary["dataset"].eq(reference_dataset)]
    drift_scored = _build_drift_score(drift_summary)

    frames = [
        _top_rows(
            miss_ref,
            sort_col="missing_rate",
            diagnostic_type="top_missing_features",
            top_n=top_n,
            notes=f"基于 {reference_dataset} 缺失率排序",
        ),
        _top_rows(
            miss_ref,
            sort_col="zero_rate",
            diagnostic_type="top_zero_features",
            top_n=top_n,
            notes=f"基于 {reference_dataset} 零值率排序",
        ),
        _top_rows(
            dist_ref,
            sort_col="skew",
            diagnostic_type="top_skewed_features",
            top_n=top_n,
            notes=f"基于 {reference_dataset} 偏态绝对值排序",
            value_abs=True,
        ),
        _top_rows(
            pos_neg_diff,
            sort_col="missing_rate_diff_abs",
            diagnostic_type="top_pos_neg_missing_diff_features",
            top_n=top_n,
            notes="基于 train_inner 中 pos/neg 缺失率差异排序",
        ),
        _top_rows(
            pos_neg_diff,
            sort_col="zero_rate_diff_abs",
            diagnostic_type="top_pos_neg_zero_diff_features",
            top_n=top_n,
            notes="基于 train_inner 中 pos/neg 零值率差异排序",
        ),
        _top_rows(
            drift_scored,
            sort_col="train_test_drift_score",
            diagnostic_type="top_train_test_drift_features",
            top_n=top_n,
            notes="综合 train/test 缺失率、median 和 p99 相对差异排序，仅用于观察泛化风险",
        ),
    ]

    return pd.concat(frames, ignore_index=True)
