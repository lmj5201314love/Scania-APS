"""Baseline 建模所需的基础数据准备工具。"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.impute import SimpleImputer

from scania_aps.config import ScaniaConfig


@dataclass(frozen=True)
class BaselineData:
    """baseline 建模使用的数据准备结果。"""

    X_train_processed: pd.DataFrame
    X_test_processed: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    feature_names: list[str]
    dropped_features: list[str]
    strategy: str
    imputer: SimpleImputer


def split_features_target(
    df: pd.DataFrame,
    label_col: str,
    target_col: str = "target",
) -> tuple[pd.DataFrame, pd.Series]:
    """拆分特征和目标列。"""

    missing_columns = [col for col in [label_col, target_col] if col not in df.columns]
    if missing_columns:
        raise ValueError(f"缺少必要列：{missing_columns}")

    X = df.drop(columns=[label_col, target_col])
    y = df[target_col]
    return X, y


def get_high_missing_features(X_train: pd.DataFrame, threshold: float) -> list[str]:
    """只基于训练集识别高缺失率字段。"""

    if not 0 <= threshold <= 1:
        raise ValueError("threshold 必须位于 0 到 1 之间。")

    missing_rate = X_train.isna().mean()
    return missing_rate[missing_rate >= threshold].index.tolist()


def _get_imputed_feature_names(imputer: SimpleImputer, base_features: list[str]) -> list[str]:
    """生成 SimpleImputer 处理后的字段名。"""

    feature_names = list(base_features)

    if getattr(imputer, "add_indicator", False) and hasattr(imputer, "indicator_"):
        indicator_indices = getattr(imputer.indicator_, "features_", [])
        indicator_features = [
            f"missing_indicator_{base_features[index]}" for index in indicator_indices
        ]
        feature_names.extend(indicator_features)

    return feature_names


def prepare_baseline_data(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    cfg: ScaniaConfig,
    strategy: str,
) -> BaselineData:
    """按指定策略准备 baseline 模型输入数据。

    所有缺失率筛选和中位数填充规则都只在训练集上拟合，然后应用到测试集。
    """

    X_train, y_train = split_features_target(train_df, cfg.label_column)
    X_test, y_test = split_features_target(test_df, cfg.label_column)

    dropped_features: list[str] = []
    add_indicator = False

    if strategy == "median_all":
        pass
    elif strategy == "drop_high_missing_median":
        dropped_features = get_high_missing_features(
            X_train=X_train,
            threshold=cfg.high_missing_threshold,
        )
        X_train = X_train.drop(columns=dropped_features)
        X_test = X_test.drop(columns=dropped_features)
    elif strategy == "median_with_indicator":
        add_indicator = True
    else:
        raise ValueError(
            "strategy 仅支持 median_all、drop_high_missing_median、median_with_indicator。"
        )

    imputer = SimpleImputer(strategy="median", add_indicator=add_indicator)
    X_train_array = imputer.fit_transform(X_train)
    X_test_array = imputer.transform(X_test)

    feature_names = _get_imputed_feature_names(imputer, X_train.columns.tolist())
    X_train_processed = pd.DataFrame(
        X_train_array,
        columns=feature_names,
        index=X_train.index,
    )
    X_test_processed = pd.DataFrame(
        X_test_array,
        columns=feature_names,
        index=X_test.index,
    )

    return BaselineData(
        X_train_processed=X_train_processed,
        X_test_processed=X_test_processed,
        y_train=y_train,
        y_test=y_test,
        feature_names=feature_names,
        dropped_features=dropped_features,
        strategy=strategy,
        imputer=imputer,
    )
