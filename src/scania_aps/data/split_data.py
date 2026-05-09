"""训练集内部 validation 划分工具。"""

from __future__ import annotations

import pandas as pd
from sklearn.model_selection import train_test_split

from scania_aps.config import ScaniaConfig


def split_train_valid(
    train_df: pd.DataFrame,
    cfg: ScaniaConfig,
    target_col: str = "target",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """从官方 training set 中划分 train_inner 和 validation set。

    划分只基于官方训练集，不触碰官方 test set。函数返回副本，避免修改原始 DataFrame。
    """

    if target_col not in train_df.columns:
        raise ValueError(f"缺少 target 列：{target_col}")

    stratify = train_df[target_col] if cfg.validation_stratify else None
    train_inner_df, valid_df = train_test_split(
        train_df,
        test_size=cfg.validation_valid_size,
        random_state=cfg.random_state,
        stratify=stratify,
    )

    return train_inner_df.copy(), valid_df.copy()


def save_split_indices(
    train_inner_df: pd.DataFrame,
    valid_df: pd.DataFrame,
    cfg: ScaniaConfig,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """保存 train_inner / valid 的原始行索引，便于复现实验划分。"""

    split_dir = cfg.interim_dir / "splits"
    split_dir.mkdir(parents=True, exist_ok=True)

    train_indices = pd.DataFrame({"original_index": train_inner_df.index})
    valid_indices = pd.DataFrame({"original_index": valid_df.index})

    train_indices.to_csv(split_dir / "train_inner_indices.csv", index=False)
    valid_indices.to_csv(split_dir / "valid_indices.csv", index=False)

    return train_indices, valid_indices
