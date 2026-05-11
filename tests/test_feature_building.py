"""特征处理策略测试。"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from scania_aps.features.build_features import prepare_feature_ablation_data


@dataclass(frozen=True)
class DummyConfig:
    """测试用配置对象。"""

    label_column: str = "class"
    random_state: int = 42
    feature_ablation: dict = field(
        default_factory=lambda: {
            "missing_thresholds": {"drop_50": 0.5, "drop_80": 0.8},
            "variance_threshold": 0.0,
            "correlation_threshold": 0.95,
        }
    )


def _make_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """构造小型模拟数据。"""

    train = pd.DataFrame(
        {
            "class": ["neg", "pos", "neg", "pos"],
            "f_keep": [1.0, 2.0, 3.0, 4.0],
            "f_drop": [None, None, None, 1.0],
            "f_corr_a": [1.0, 2.0, 3.0, 4.0],
            "f_corr_b": [2.0, 4.0, 6.0, 8.0],
            "target": [0, 1, 0, 1],
        }
    )
    valid = pd.DataFrame(
        {
            "class": ["neg", "pos"],
            "f_keep": [5.0, None],
            "f_drop": [1.0, 2.0],
            "f_corr_a": [5.0, 6.0],
            "f_corr_b": [10.0, 12.0],
            "target": [0, 1],
        }
    )
    test = valid.copy()
    return train, valid, test


def test_drop_50_missing_median_uses_train_inner_missing_rate_only() -> None:
    """drop_50 应根据 train_inner 缺失率删除字段。"""

    train, valid, test = _make_frames()
    original = train.copy(deep=True)
    result = prepare_feature_ablation_data(
        train,
        valid,
        test,
        DummyConfig(),
        "drop_50_missing_median",
    )

    assert "f_drop" in result.dropped_features
    assert "f_drop" not in result.feature_names
    pd.testing.assert_frame_equal(train, original)


def test_median_with_indicator_adds_indicator_columns() -> None:
    """median_with_indicator 应增加缺失指示字段。"""

    train, valid, test = _make_frames()
    result = prepare_feature_ablation_data(
        train,
        valid,
        test,
        DummyConfig(),
        "median_with_indicator",
    )

    assert any(name.startswith("missing_indicator_") for name in result.feature_names)


def test_missing_indicator_only_outputs_binary_features() -> None:
    """missing_indicator_only 只输出 0/1 缺失指示变量。"""

    train, valid, test = _make_frames()
    result = prepare_feature_ablation_data(
        train,
        valid,
        test,
        DummyConfig(),
        "missing_indicator_only",
    )

    assert all(name.startswith("missing_indicator_") for name in result.feature_names)
    values = set(result.X_train_inner_processed.to_numpy().ravel())
    assert values <= {0, 1}


def test_high_correlation_filter_drops_redundant_feature() -> None:
    """high_correlation_filter 应删除 train_inner 中高度相关的冗余字段。"""

    train, valid, test = _make_frames()
    result = prepare_feature_ablation_data(
        train,
        valid,
        test,
        DummyConfig(),
        "high_correlation_filter",
    )

    assert "f_corr_b" in result.dropped_features
    assert "f_corr_b" not in result.feature_names
