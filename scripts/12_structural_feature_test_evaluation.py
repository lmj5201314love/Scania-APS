"""运行 Day 14 结构特征候选方案 official test 最终观察。

本脚本固定使用 Day 13 valid 上选出的候选组和 threshold。official test 只
用于最终观察，不参与候选组、结构特征规则或阈值选择。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from scania_aps.config import get_config  # noqa: E402
from scania_aps.data.load_data import load_train_test_with_target  # noqa: E402
from scania_aps.data.split_data import split_train_valid  # noqa: E402
from scania_aps.features.structural_feature_design import (  # noqa: E402
    load_structural_feature_config,
)
from scania_aps.models.structural_feature_test_evaluation import (  # noqa: E402
    DEFAULT_DAY14_CANDIDATE_GROUPS,
    evaluate_structural_feature_candidates_on_test,
)


def main() -> None:
    """从项目根目录运行 Day 14 official test 观察。"""

    cfg = get_config(PROJECT_ROOT / "config" / "config.yaml")
    structural_config = load_structural_feature_config(
        PROJECT_ROOT / "config" / "structural_features.yaml"
    )
    valid_best_summary = pd.read_csv(
        cfg.metrics_dir / "day13_structural_feature_valid_best_summary.csv"
    )

    cfg.metrics_dir.mkdir(parents=True, exist_ok=True)
    cfg.predictions_dir.mkdir(parents=True, exist_ok=True)
    cfg.tables_dir.mkdir(parents=True, exist_ok=True)

    train_df, test_df = load_train_test_with_target(cfg)
    train_inner_df, valid_df = split_train_valid(train_df, cfg)

    results = evaluate_structural_feature_candidates_on_test(
        train_inner_df=train_inner_df,
        valid_df=valid_df,
        test_df=test_df,
        cfg=cfg,
        structural_config=structural_config,
        candidate_groups=DEFAULT_DAY14_CANDIDATE_GROUPS,
        valid_best_summary=valid_best_summary,
    )

    results["test_results"].to_csv(
        cfg.metrics_dir / "day14_structural_feature_test_results.csv",
        index=False,
    )
    results["test_compare_with_valid"].to_csv(
        cfg.metrics_dir / "day14_structural_feature_valid_test_compare.csv",
        index=False,
    )
    results["test_predictions"].to_csv(
        cfg.predictions_dir / "day14_structural_feature_test_predictions.csv",
        index=False,
    )
    results["metadata"].to_csv(
        cfg.tables_dir / "day14_structural_feature_test_metadata.csv",
        index=False,
    )

    display_cols = [
        "candidate_group",
        "threshold",
        "precision",
        "recall",
        "f2",
        "average_precision",
        "fp",
        "fn",
        "total_cost",
        "n_structural_features",
    ]
    print("Day 14 official test 观察完成。")
    print("注意：本轮未在 test 上重新选择候选组、结构特征或阈值。")
    print(results["test_results"][display_cols].to_string(index=False))


if __name__ == "__main__":
    main()
