"""成本敏感评估函数测试。"""

from __future__ import annotations

from dataclasses import dataclass

from scania_aps.evaluation.cost_utils import calculate_aps_cost


@dataclass(frozen=True)
class DummyConfig:
    """测试用配置对象，只包含成本参数。"""

    false_positive_cost: int = 10
    false_negative_cost: int = 500


def test_calculate_aps_cost_uses_cfg_costs() -> None:
    """成本应来自 cfg，而不是函数内部写死。"""

    cfg = DummyConfig(false_positive_cost=7, false_negative_cost=300)
    result = calculate_aps_cost(
        y_true=[0, 0, 1, 1],
        y_pred=[0, 1, 0, 1],
        cfg=cfg,
    )

    assert result["tn"] == 1
    assert result["fp"] == 1
    assert result["fn"] == 1
    assert result["tp"] == 1
    assert result["false_positive_cost"] == 7
    assert result["false_negative_cost"] == 300
    assert result["total_cost"] == 307
