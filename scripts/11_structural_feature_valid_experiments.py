"""运行 Day 13 结构特征 valid-only 实验。

本脚本只使用 official train 内部划分出的 train_inner / valid。official test
本轮只读取但不参与评估和策略选择。
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
from scania_aps.features.structural_features import (  # noqa: E402
    MAIN_EXPERIMENT_GROUPS,
    build_selected_missing_indicator_summary,
)
from scania_aps.models.structural_feature_experiments import (  # noqa: E402
    run_structural_feature_valid_experiments,
)


def _feature_names_by_group(metadata_df: pd.DataFrame) -> pd.DataFrame:
    """展开每个实验组包含的结构特征名称。"""

    rows: list[dict[str, object]] = []
    for _, row in metadata_df.iterrows():
        names = [
            name
            for name in str(row.get("structural_feature_names", "")).split("|")
            if name
        ]
        if not names:
            rows.append(
                {
                    "experiment_group": row["experiment_group"],
                    "structural_feature_name": None,
                    "structural_feature_rank": None,
                }
            )
            continue
        for rank, name in enumerate(names, start=1):
            rows.append(
                {
                    "experiment_group": row["experiment_group"],
                    "structural_feature_name": name,
                    "structural_feature_rank": rank,
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    """从项目根目录运行 Day 13 valid 实验。"""

    cfg = get_config(PROJECT_ROOT / "config" / "config.yaml")
    structural_config = load_structural_feature_config(
        PROJECT_ROOT / "config" / "structural_features.yaml"
    )

    cfg.metrics_dir.mkdir(parents=True, exist_ok=True)
    cfg.tables_dir.mkdir(parents=True, exist_ok=True)

    train_df, _official_test_df = load_train_test_with_target(cfg)
    train_inner_df, valid_df = split_train_valid(train_df, cfg)

    results = run_structural_feature_valid_experiments(
        train_inner_df=train_inner_df,
        valid_df=valid_df,
        cfg=cfg,
        structural_config=structural_config,
        experiment_groups=MAIN_EXPERIMENT_GROUPS,
    )

    valid_threshold_metrics = results["valid_threshold_metrics"]
    valid_best_summary = results["valid_best_summary"]
    experiment_metadata = results["experiment_metadata"]

    valid_threshold_metrics.to_csv(
        cfg.metrics_dir / "day13_structural_feature_valid_threshold_metrics.csv",
        index=False,
    )
    valid_best_summary.to_csv(
        cfg.metrics_dir / "day13_structural_feature_valid_best_summary.csv",
        index=False,
    )
    experiment_metadata.to_csv(
        cfg.tables_dir / "day13_structural_feature_experiment_metadata.csv",
        index=False,
    )

    selected_missing_summary = build_selected_missing_indicator_summary(
        train_inner_df=train_inner_df,
        cfg=cfg,
        structural_config=structural_config,
    )
    selected_missing_summary.to_csv(
        cfg.tables_dir / "day13_selected_missing_indicator_columns.csv",
        index=False,
    )

    feature_names_by_group = _feature_names_by_group(experiment_metadata)
    feature_names_by_group.to_csv(
        cfg.tables_dir / "day13_structural_feature_names_by_group.csv",
        index=False,
    )

    display_cols = [
        "strategy",
        "best_threshold",
        "precision",
        "recall",
        "f2",
        "average_precision",
        "fp",
        "fn",
        "total_cost",
        "n_structural_features",
    ]
    print("Day 13 结构特征 valid-only 实验完成。")
    print("注意：本轮没有使用 official test 做评估或反选。")
    print(valid_best_summary[display_cols].to_string(index=False))


if __name__ == "__main__":
    main()
