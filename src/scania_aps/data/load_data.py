"""Scania APS 原始数据读取工具。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from scania_aps.config import ScaniaConfig


def load_raw_data(
    train_path: str | Path,
    test_path: str | Path,
    na_values: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """读取 Scania APS 原始训练集和测试集。"""

    train_df = pd.read_csv(train_path, na_values=na_values)
    test_df = pd.read_csv(test_path, na_values=na_values)
    return train_df, test_df


def load_raw_data_from_config(
    cfg: ScaniaConfig,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """基于项目配置读取原始 train/test 数据。"""

    return load_raw_data(
        train_path=cfg.train_raw,
        test_path=cfg.test_raw,
        na_values=cfg.missing_value_token,
    )


def map_target(
    df: pd.DataFrame,
    label_col: str,
    target_mapping: dict[str, int],
    target_col: str = "target",
) -> pd.DataFrame:
    """将标签列映射为 target 列。"""

    result = df.copy()
    result[target_col] = result[label_col].map(target_mapping)
    return result


def map_target_from_config(
    df: pd.DataFrame,
    cfg: ScaniaConfig,
    target_col: str = "target",
) -> pd.DataFrame:
    """基于项目配置映射标签列。"""

    return map_target(
        df=df,
        label_col=cfg.label_column,
        target_mapping=cfg.target_mapping,
        target_col=target_col,
    )