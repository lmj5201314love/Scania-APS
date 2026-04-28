"""Scania APS 原始数据读取工具。

本模块只提供基础读取和标签映射函数，不做缺失值填充、字段删除、
特征工程或模型训练，避免在数据理解阶段引入额外处理规则。
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_raw_data(
    train_path: str | Path,
    test_path: str | Path,
    na_values: str = "na",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """读取 Scania APS 原始训练集和测试集。

    参数不写死绝对路径，调用方负责传入项目内的原始数据路径。
    原始 CSV 中的字符串 ``"na"`` 会被识别为缺失值。
    """

    train_df = pd.read_csv(train_path, na_values=na_values)
    test_df = pd.read_csv(test_path, na_values=na_values)
    return train_df, test_df


def map_target(df: pd.DataFrame, label_col: str = "class") -> pd.DataFrame:
    """将标签列映射为 target 列。

    映射规则为 ``pos -> 1``、``neg -> 0``。函数返回副本，不修改传入的
    DataFrame，也不改变原始数据文件。
    """

    target_mapping = {"neg": 0, "pos": 1}
    result = df.copy()
    result["target"] = result[label_col].map(target_mapping)
    return result
