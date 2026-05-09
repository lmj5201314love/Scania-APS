"""阈值成本分析工具测试。"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from scania_aps.evaluation.threshold_utils import (
    build_threshold_summary,
    evaluate_threshold_grid,
    find_best_threshold,
)


@dataclass(frozen=True)
class DummyConfig:
    """测试用配置对象，只包含成本参数。"""

    false_positive_cost: int = 10
    false_negative_cost: int = 500


def test_evaluate_threshold_grid_returns_cost_columns() -> None:
    """阈值网格结果应包含核心指标和业务成本。"""

    cfg = DummyConfig()
    result = evaluate_threshold_grid(
        y_true=[0, 1, 1],
        y_proba=[0.1, 0.4, 0.9],
        cfg=cfg,
        model_name="demo_model",
        strategy="demo_strategy",
        thresholds=[0.5],
    )

    row = result.iloc[0]
    assert row["model_name"] == "demo_model"
    assert row["strategy"] == "demo_strategy"
    assert row["threshold"] == 0.5
    assert row["fp"] == 0
    assert row["fn"] == 1
    assert row["total_cost"] == 500


def test_find_best_threshold_breaks_ties_by_recall_and_f2() -> None:
    """成本相同时，应优先选择 recall 和 F2 更高的阈值。"""

    threshold_df = pd.DataFrame(
        [
            {"threshold": 0.3, "total_cost": 100, "recall": 0.8, "f2": 0.7},
            {"threshold": 0.2, "total_cost": 100, "recall": 0.9, "f2": 0.6},
            {"threshold": 0.4, "total_cost": 120, "recall": 1.0, "f2": 0.9},
        ]
    )

    best = find_best_threshold(threshold_df)
    assert best["threshold"] == 0.2


def test_build_threshold_summary_selects_one_row_per_model_strategy() -> None:
    """汇总表应为每个模型和策略保留一条低成本阈值记录。"""

    all_results = pd.DataFrame(
        [
            {
                "model_name": "model_a",
                "strategy": "median",
                "threshold": 0.5,
                "precision": 0.5,
                "recall": 0.8,
                "f1": 0.6,
                "f2": 0.7,
                "fp": 10,
                "fn": 2,
                "total_cost": 1100,
                "average_precision": 0.9,
            },
            {
                "model_name": "model_a",
                "strategy": "median",
                "threshold": 0.2,
                "precision": 0.4,
                "recall": 0.9,
                "f1": 0.55,
                "f2": 0.75,
                "fp": 20,
                "fn": 1,
                "total_cost": 700,
                "average_precision": 0.9,
            },
        ]
    )

    summary = build_threshold_summary(all_results)
    assert len(summary) == 1
    assert summary.iloc[0]["best_threshold"] == 0.2
