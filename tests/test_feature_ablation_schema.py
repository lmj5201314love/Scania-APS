"""特征消融结果 schema 测试。"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from scania_aps.models.feature_ablation import run_feature_ablation_experiments


@dataclass(frozen=True)
class DummyConfig:
    """测试用配置对象。"""

    label_column: str = "class"
    random_state: int = 42
    default_threshold: float = 0.5
    false_positive_cost: int = 10
    false_negative_cost: int = 500
    feature_ablation: dict = field(
        default_factory=lambda: {
            "missing_thresholds": {"drop_50": 0.5, "drop_80": 0.8},
            "variance_threshold": 0.0,
            "correlation_threshold": 0.95,
        }
    )


def test_feature_ablation_result_contains_required_columns() -> None:
    """消融实验结果表应包含必要字段。"""

    train = pd.DataFrame(
        {
            "class": ["neg", "pos", "neg", "pos", "neg", "pos"],
            "f1": [0.0, 1.0, 0.1, 1.1, 0.2, 1.2],
            "f2": [None, 1.0, 0.1, None, 0.2, 1.2],
            "target": [0, 1, 0, 1, 0, 1],
        }
    )
    valid = train.copy()
    test = train.copy()

    result = run_feature_ablation_experiments(
        train_inner_df=train,
        valid_df=valid,
        test_df=test,
        cfg=DummyConfig(),
        strategies=["median_all"],
        model_names=["logistic_regression_balanced"],
    )

    required_metric_columns = {
        "model_name",
        "strategy",
        "threshold",
        "precision",
        "recall",
        "f2",
        "fp",
        "fn",
        "total_cost",
    }
    assert required_metric_columns <= set(result["valid_threshold_metrics"].columns)
    assert required_metric_columns <= set(result["final_test_results"].columns)
    assert {"model_name", "strategy", "n_features", "n_dropped_features"} <= set(
        result["strategy_metadata"].columns
    )
