"""生成 Day 12 结构特征设计表。"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from scania_aps.config import get_config  # noqa: E402
from scania_aps.features.structural_feature_design import (  # noqa: E402
    build_structural_feature_design_table,
    load_structural_feature_config,
    select_missing_indicator_candidates,
)


def main() -> None:
    """读取 Day 10/Day 11 输出，生成结构特征设计表。"""

    cfg = get_config(PROJECT_ROOT / "config" / "config.yaml")
    cfg.tables_dir.mkdir(parents=True, exist_ok=True)

    structural_config = load_structural_feature_config(
        cfg.project_root / "config" / "structural_features.yaml"
    )
    missing_zero_summary = pd.read_csv(cfg.metrics_dir / "day10_missing_zero_summary.csv")
    pos_neg_diff = pd.read_csv(cfg.metrics_dir / "day10_pos_neg_distribution_diff.csv")
    prefix_group_summary = pd.read_csv(cfg.metrics_dir / "day11_prefix_group_summary.csv")

    design_table = build_structural_feature_design_table(
        missing_zero_summary=missing_zero_summary,
        pos_neg_diff=pos_neg_diff,
        prefix_group_summary=prefix_group_summary,
        structural_config=structural_config,
    )
    missing_candidates = select_missing_indicator_candidates(
        missing_zero_summary,
        pos_neg_diff,
        structural_config,
    )

    output_path = cfg.tables_dir / "day12_structural_feature_design_table.csv"
    design_table.to_csv(output_path, index=False, encoding="utf-8-sig")

    high_priority_count = int(design_table["priority"].eq("high").sum())
    first_round_count = int(design_table["use_in_day13_first_round"].sum())

    print("Day 12 结构特征设计表已生成。")
    print(f"输出：{output_path}")
    print(f"设计行数：{len(design_table)}")
    print(f"高优先级设计行数：{high_priority_count}")
    print(f"Day 13 第一轮启用设计行数：{first_round_count}")
    print(f"selected missing indicators 候选数：{len(missing_candidates)}")

    print("\n设计表按 feature_family 汇总：")
    print(design_table["feature_family"].value_counts().to_string())

    print("\nselected missing indicators Top 10：")
    if missing_candidates.empty:
        print("无候选字段。")
    else:
        print(
            missing_candidates[
                ["feature_name", "missing_rate", "missing_rate_diff_abs"]
            ]
            .head(10)
            .to_string(index=False)
        )


if __name__ == "__main__":
    main()
