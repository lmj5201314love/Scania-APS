"""validation 划分工具测试。"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from scania_aps.data.split_data import split_train_valid


@dataclass(frozen=True)
class DummyConfig:
    """测试用配置对象，只包含划分所需字段。"""

    validation_valid_size: float = 0.2
    validation_stratify: bool = True
    random_state: int = 42


def test_split_train_valid_keeps_total_rows_and_does_not_modify_input() -> None:
    """train_inner 和 valid 行数之和应等于原始训练集，且不修改输入数据。"""

    df = pd.DataFrame(
        {
            "feature": range(100),
            "target": [1] * 10 + [0] * 90,
        }
    )
    original = df.copy(deep=True)

    train_inner_df, valid_df = split_train_valid(df, DummyConfig())

    assert len(train_inner_df) + len(valid_df) == len(df)
    assert len(valid_df) == 20
    pd.testing.assert_frame_equal(df, original)


def test_split_train_valid_stratify_keeps_positive_rate_close() -> None:
    """分层抽样后，valid 正类比例应接近原始训练集。"""

    df = pd.DataFrame(
        {
            "feature": range(100),
            "target": [1] * 10 + [0] * 90,
        }
    )

    _, valid_df = split_train_valid(df, DummyConfig())

    assert valid_df["target"].mean() == 0.1
