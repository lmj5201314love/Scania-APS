"""统一风险政策公共接口测试。"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pandas as pd
import pytest

from scania_aps.evaluation.risk_utils import (
    ACTION_MAPPING,
    assign_risk_level,
    assign_suggested_action,
    build_maintenance_priority_table,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMITTED_SQL_EXPORT = (
    PROJECT_ROOT / "outputs" / "sql_exports" / "model_prediction_results.csv"
)


def test_risk_levels_map_to_frozen_action_codes() -> None:
    """四档风险和未知等级应映射到冻结的业务动作 code。"""

    levels = pd.Series(["Critical", "High", "Medium", "Low", "Unknown"])

    actions = assign_suggested_action(levels)

    assert actions.tolist() == [
        "immediate_aps_inspection",
        "priority_aps_inspection",
        "aps_recheck_or_additional_diagnosis",
        "continue_non_aps_diagnosis",
        "manual_review",
    ]
    assert set(ACTION_MAPPING) == {"Critical", "High", "Medium", "Low"}
    assert set(ACTION_MAPPING.values()) == set(actions.iloc[:4])


def test_risk_scores_use_release_threshold_boundaries() -> None:
    """0.18 和 0.05 边界应分别进入 High 与 Medium。"""

    scores = pd.Series([0.80, 0.799999, 0.18, 0.179999, 0.05, 0.049999, 0.0])

    levels = assign_risk_level(scores, best_threshold=0.18)

    assert levels.tolist() == [
        "Critical",
        "High",
        "High",
        "Medium",
        "Medium",
        "Low",
        "Low",
    ]


def test_risk_level_rejects_non_numeric_decision_threshold() -> None:
    """调用方传入非数值阈值时应返回可定位的配置错误。"""

    with pytest.raises(ValueError, match="decision_threshold"):
        assign_risk_level([0.18], best_threshold=None)


@pytest.mark.parametrize("invalid_threshold", [0.049999, 0.05, 0.80, float("nan"), True])
def test_risk_level_rejects_thresholds_that_break_tier_order(
    invalid_threshold: object,
) -> None:
    """阈值必须位于 Medium 下界与 Critical 下界之间。"""

    with pytest.raises(ValueError, match="decision_threshold"):
        assign_risk_level([0.18], best_threshold=invalid_threshold)


def test_maintenance_priority_table_uses_one_consistent_risk_policy() -> None:
    """风险、预测、混淆类型和动作应由同一阈值政策生成。"""

    predictions = pd.DataFrame(
        {
            "sample_id": range(1, 8),
            "y_true": [1, 0, 1, 1, 0, 0, 1],
            "y_proba": [0.80, 0.799999, 0.18, 0.179999, 0.05, 0.049999, 0.0],
            "model_name": ["candidate"] * 7,
            "strategy": ["frozen_strategy"] * 7,
        }
    )
    original = deepcopy(predictions)

    result = build_maintenance_priority_table(
        predictions,
        best_threshold=0.18,
        model_name="candidate",
        strategy="frozen_strategy",
    ).sort_values("sample_id")

    pd.testing.assert_frame_equal(predictions, original)
    assert result["risk_level"].tolist() == [
        "Critical",
        "High",
        "High",
        "Medium",
        "Medium",
        "Low",
        "Low",
    ]
    assert result["y_pred"].tolist() == [1, 1, 1, 0, 0, 0, 0]
    assert result["prediction_type"].tolist() == [
        "TP",
        "FP",
        "TP",
        "FN",
        "TN",
        "TN",
        "FN",
    ]
    assert not result.loc[result["risk_level"].isin(["Medium", "Low"]), "y_pred"].any()


def test_committed_risk_scores_reclassify_to_frozen_tier_counts() -> None:
    """已提交风险分数应只读重分层为冻结的 16,000 行业务口径。"""

    predictions = pd.read_csv(COMMITTED_SQL_EXPORT)
    levels = assign_risk_level(predictions["y_proba"], best_threshold=0.18)
    counts = levels.value_counts()

    assert len(predictions) == 16000
    assert counts.to_dict() == {
        "Critical": 404,
        "High": 357,
        "Medium": 378,
        "Low": 14861,
    }
    assert counts["Critical"] + counts["High"] == 761
    assert not predictions.loc[levels.isin(["Medium", "Low"]), "y_pred"].any()
