"""缺失值处理和基础特征工程策略。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.feature_selection import VarianceThreshold
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from scania_aps.config import ScaniaConfig
from scania_aps.data.clean_data import split_features_target


@dataclass(frozen=True)
class FeatureData:
    """特征处理后的 train_inner / valid / test 数据。"""

    X_train_inner_processed: pd.DataFrame
    X_valid_processed: pd.DataFrame
    X_test_processed: pd.DataFrame
    y_train_inner: pd.Series
    y_valid: pd.Series
    y_test: pd.Series
    feature_names: list[str]
    dropped_features: list[str]
    strategy: str
    strategy_metadata: dict[str, Any]


def _imputed_feature_names(imputer: SimpleImputer, base_features: list[str]) -> list[str]:
    """生成 SimpleImputer 处理后的字段名。"""

    feature_names = list(base_features)
    if getattr(imputer, "add_indicator", False) and hasattr(imputer, "indicator_"):
        indicator_indices = getattr(imputer.indicator_, "features_", [])
        feature_names.extend(
            [f"missing_indicator_{base_features[index]}" for index in indicator_indices]
        )
    return feature_names


def _median_impute(
    X_train: pd.DataFrame,
    X_valid: pd.DataFrame,
    X_test: pd.DataFrame,
    *,
    add_indicator: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[str], SimpleImputer]:
    """只在 train_inner 上拟合 median imputer，再应用到 valid/test。"""

    imputer = SimpleImputer(strategy="median", add_indicator=add_indicator)
    X_train_array = imputer.fit_transform(X_train)
    X_valid_array = imputer.transform(X_valid)
    X_test_array = imputer.transform(X_test)
    feature_names = _imputed_feature_names(imputer, X_train.columns.tolist())

    return (
        pd.DataFrame(X_train_array, columns=feature_names, index=X_train.index),
        pd.DataFrame(X_valid_array, columns=feature_names, index=X_valid.index),
        pd.DataFrame(X_test_array, columns=feature_names, index=X_test.index),
        feature_names,
        imputer,
    )


def _drop_missing_features(X_train: pd.DataFrame, threshold: float) -> list[str]:
    """只基于 train_inner 缺失率识别需要删除的字段。"""

    missing_rate = X_train.isna().mean()
    return missing_rate[missing_rate >= threshold].index.tolist()


def _build_missing_indicator_only(
    X_train: pd.DataFrame,
    X_valid: pd.DataFrame,
    X_test: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[str]]:
    """将每个原始特征是否缺失转换为 0/1 特征。"""

    feature_names = [f"missing_indicator_{col}" for col in X_train.columns]
    return (
        pd.DataFrame(X_train.isna().astype(int).to_numpy(), columns=feature_names, index=X_train.index),
        pd.DataFrame(X_valid.isna().astype(int).to_numpy(), columns=feature_names, index=X_valid.index),
        pd.DataFrame(X_test.isna().astype(int).to_numpy(), columns=feature_names, index=X_test.index),
        feature_names,
    )


def _apply_low_variance_filter(
    X_train: pd.DataFrame,
    X_valid: pd.DataFrame,
    X_test: pd.DataFrame,
    cfg: ScaniaConfig,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[str], list[str], dict[str, Any]]:
    """median 填充后，只在 train_inner 上拟合低方差过滤器。"""

    X_train_imp, X_valid_imp, X_test_imp, feature_names, _ = _median_impute(
        X_train,
        X_valid,
        X_test,
    )
    threshold = cfg.feature_ablation["variance_threshold"]
    selector = VarianceThreshold(threshold=threshold)
    X_train_array = selector.fit_transform(X_train_imp)
    X_valid_array = selector.transform(X_valid_imp)
    X_test_array = selector.transform(X_test_imp)

    keep_mask = selector.get_support()
    kept_features = [name for name, keep in zip(feature_names, keep_mask) if keep]
    dropped_features = [name for name, keep in zip(feature_names, keep_mask) if not keep]
    metadata = {
        "imputation_method": "median",
        "feature_filter": "variance_threshold",
        "variance_threshold": threshold,
        "has_missing_indicator": False,
    }

    return (
        pd.DataFrame(X_train_array, columns=kept_features, index=X_train.index),
        pd.DataFrame(X_valid_array, columns=kept_features, index=X_valid.index),
        pd.DataFrame(X_test_array, columns=kept_features, index=X_test.index),
        kept_features,
        dropped_features,
        metadata,
    )


def _find_high_correlation_features(X_train_imputed: pd.DataFrame, threshold: float) -> list[str]:
    """只基于 train_inner 的特征间相关性识别冗余字段。"""

    corr = X_train_imputed.corr().abs()
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    return [column for column in upper.columns if any(upper[column] >= threshold)]


def _apply_high_correlation_filter(
    X_train: pd.DataFrame,
    X_valid: pd.DataFrame,
    X_test: pd.DataFrame,
    cfg: ScaniaConfig,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[str], list[str], dict[str, Any]]:
    """median 填充后，只基于 train_inner 删除高相关冗余字段。"""

    X_train_imp, X_valid_imp, X_test_imp, feature_names, _ = _median_impute(
        X_train,
        X_valid,
        X_test,
    )
    threshold = cfg.feature_ablation["correlation_threshold"]
    dropped_features = _find_high_correlation_features(X_train_imp, threshold)
    kept_features = [feature for feature in feature_names if feature not in dropped_features]
    metadata = {
        "imputation_method": "median",
        "feature_filter": "high_correlation_filter",
        "correlation_threshold": threshold,
        "has_missing_indicator": False,
    }

    return (
        X_train_imp[kept_features].copy(),
        X_valid_imp[kept_features].copy(),
        X_test_imp[kept_features].copy(),
        kept_features,
        dropped_features,
        metadata,
    )


def _apply_l1_feature_selection(
    X_train: pd.DataFrame,
    X_valid: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    cfg: ScaniaConfig,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[str], list[str], dict[str, Any]]:
    """median 填充后，用 L1 Logistic 只在 train_inner 上选择字段。"""

    X_train_imp, X_valid_imp, X_test_imp, feature_names, _ = _median_impute(
        X_train,
        X_valid,
        X_test,
    )
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_imp)
    selector_model = LogisticRegression(
        penalty="l1",
        solver="liblinear",
        class_weight="balanced",
        max_iter=1000,
        random_state=cfg.random_state,
    )
    selector_model.fit(X_train_scaled, y_train)

    coef = np.abs(selector_model.coef_[0])
    keep_mask = coef > 1e-8
    if not keep_mask.any():
        keep_mask[np.argmax(coef)] = True

    kept_features = [name for name, keep in zip(feature_names, keep_mask) if keep]
    dropped_features = [name for name, keep in zip(feature_names, keep_mask) if not keep]
    metadata = {
        "imputation_method": "median",
        "feature_filter": "l1_feature_selection",
        "selector_model": "LogisticRegression_l1_liblinear",
        "has_missing_indicator": False,
    }

    return (
        X_train_imp[kept_features].copy(),
        X_valid_imp[kept_features].copy(),
        X_test_imp[kept_features].copy(),
        kept_features,
        dropped_features,
        metadata,
    )


def prepare_feature_ablation_data(
    train_inner_df: pd.DataFrame,
    valid_df: pd.DataFrame,
    test_df: pd.DataFrame,
    cfg: ScaniaConfig,
    strategy: str,
) -> FeatureData:
    """按指定消融策略准备 train_inner / valid / test 特征。

    所有筛选、填充和选择规则只在 train_inner 上拟合，再应用到 valid/test。
    """

    original_train = train_inner_df.copy(deep=True)
    X_train, y_train = split_features_target(train_inner_df, cfg.label_column)
    X_valid, y_valid = split_features_target(valid_df, cfg.label_column)
    X_test, y_test = split_features_target(test_df, cfg.label_column)
    dropped_features: list[str] = []

    if strategy == "median_all":
        X_train_p, X_valid_p, X_test_p, feature_names, _ = _median_impute(
            X_train,
            X_valid,
            X_test,
        )
        metadata = {"imputation_method": "median", "has_missing_indicator": False}

    elif strategy == "drop_80_missing_median":
        threshold = cfg.feature_ablation["missing_thresholds"]["drop_80"]
        dropped_features = _drop_missing_features(X_train, threshold)
        X_train_p, X_valid_p, X_test_p, feature_names, _ = _median_impute(
            X_train.drop(columns=dropped_features),
            X_valid.drop(columns=dropped_features),
            X_test.drop(columns=dropped_features),
        )
        metadata = {
            "imputation_method": "median",
            "missing_drop_threshold": threshold,
            "has_missing_indicator": False,
        }

    elif strategy == "drop_50_missing_median":
        threshold = cfg.feature_ablation["missing_thresholds"]["drop_50"]
        dropped_features = _drop_missing_features(X_train, threshold)
        X_train_p, X_valid_p, X_test_p, feature_names, _ = _median_impute(
            X_train.drop(columns=dropped_features),
            X_valid.drop(columns=dropped_features),
            X_test.drop(columns=dropped_features),
        )
        metadata = {
            "imputation_method": "median",
            "missing_drop_threshold": threshold,
            "has_missing_indicator": False,
        }

    elif strategy == "median_with_indicator":
        X_train_p, X_valid_p, X_test_p, feature_names, _ = _median_impute(
            X_train,
            X_valid,
            X_test,
            add_indicator=True,
        )
        metadata = {"imputation_method": "median", "has_missing_indicator": True}

    elif strategy == "xgb_native_missing":
        X_train_p = X_train.copy()
        X_valid_p = X_valid.copy()
        X_test_p = X_test.copy()
        feature_names = X_train.columns.tolist()
        metadata = {"imputation_method": "xgboost_native_missing", "has_missing_indicator": False}

    elif strategy == "low_variance_filter":
        X_train_p, X_valid_p, X_test_p, feature_names, dropped_features, metadata = (
            _apply_low_variance_filter(X_train, X_valid, X_test, cfg)
        )

    elif strategy == "high_correlation_filter":
        X_train_p, X_valid_p, X_test_p, feature_names, dropped_features, metadata = (
            _apply_high_correlation_filter(X_train, X_valid, X_test, cfg)
        )

    elif strategy == "l1_feature_selection":
        X_train_p, X_valid_p, X_test_p, feature_names, dropped_features, metadata = (
            _apply_l1_feature_selection(X_train, X_valid, X_test, y_train, cfg)
        )

    elif strategy == "missing_indicator_only":
        X_train_p, X_valid_p, X_test_p, feature_names = _build_missing_indicator_only(
            X_train,
            X_valid,
            X_test,
        )
        metadata = {
            "imputation_method": "none",
            "feature_filter": "missing_indicator_only",
            "has_missing_indicator": True,
            "uses_raw_numeric_values": False,
        }

    else:
        raise ValueError(f"不支持的特征处理策略：{strategy}")

    pd.testing.assert_frame_equal(train_inner_df, original_train)
    metadata = {
        "strategy": strategy,
        "n_features": len(feature_names),
        "n_dropped_features": len(dropped_features),
        **metadata,
    }

    return FeatureData(
        X_train_inner_processed=X_train_p,
        X_valid_processed=X_valid_p,
        X_test_processed=X_test_p,
        y_train_inner=y_train.copy(),
        y_valid=y_valid.copy(),
        y_test=y_test.copy(),
        feature_names=feature_names,
        dropped_features=dropped_features,
        strategy=strategy,
        strategy_metadata=metadata,
    )
