"""准备 Day 3 SQL 辅助统计表导入文件。

本脚本将 Day 2 的本地分析产物整理成更适合导入 MySQL 辅助表的 CSV：

- `dataset_overview_for_mysql.csv`
- `label_distribution_for_mysql.csv`
- `feature_missing_summary_for_mysql.csv`

脚本不修改 `data/raw/`，不做缺失值填充、字段删除、特征工程或建模。
其中整体缺失率优先复用 Day 2 输出表；pos/neg 分组缺失率需要读取
训练集原始数据进行统计，用于支持 `feature_missing_summary` 的
`summary_scope = 'by_class'` 场景。
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_TRAIN_PATH = PROJECT_ROOT / "data" / "raw" / "aps_failure_training_set.csv"
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
SQL_SUPPORT_DIR = TABLES_DIR / "sql_support"
LABEL_COL = "class"


def prepare_dataset_overview() -> pd.DataFrame:
    """整理 dataset_overview 辅助表导入文件。"""

    source = pd.read_csv(TABLES_DIR / "dataset_overview.csv")
    result = source.rename(
        columns={
            "rows": "total_rows",
            "columns": "total_columns",
            "has_label_column": "label_column_exists",
        }
    )[
        [
            "dataset",
            "total_rows",
            "total_columns",
            "feature_count",
            "label_column_exists",
        ]
    ].copy()
    result["label_column_exists"] = result["label_column_exists"].astype(int)
    return result


def prepare_label_distribution() -> pd.DataFrame:
    """整理 label_distribution 辅助表导入文件。"""

    source = pd.read_csv(TABLES_DIR / "label_distribution.csv")
    return source.rename(
        columns={
            "count": "sample_count",
            "ratio": "sample_ratio",
        }
    )[["dataset", "class", "sample_count", "sample_ratio"]]


def prepare_overall_missing_summary() -> pd.DataFrame:
    """整理 train/test 整体缺失率统计。"""

    parts = []
    for dataset in ["train", "test"]:
        source = pd.read_csv(TABLES_DIR / f"missing_summary_{dataset}.csv")
        source = source[source["feature_name"] != LABEL_COL].copy()
        source.insert(1, "summary_scope", "overall")
        source.insert(2, "class_label", "all")
        parts.append(
            source[
                [
                    "dataset",
                    "summary_scope",
                    "class_label",
                    "feature_name",
                    "missing_count",
                    "total_count",
                    "missing_rate",
                ]
            ]
        )
    return pd.concat(parts, ignore_index=True)


def prepare_class_missing_summary() -> pd.DataFrame:
    """计算训练集 pos/neg 分组缺失率统计。"""

    train_df = pd.read_csv(RAW_TRAIN_PATH, na_values="na")
    feature_cols = [col for col in train_df.columns if col != LABEL_COL]
    rows = []
    for class_label, class_df in train_df.groupby(LABEL_COL):
        total_count = len(class_df)
        missing_count = class_df[feature_cols].isna().sum()
        for feature_name in feature_cols:
            count = int(missing_count[feature_name])
            rows.append(
                {
                    "dataset": "train",
                    "summary_scope": "by_class",
                    "class_label": class_label,
                    "feature_name": feature_name,
                    "missing_count": count,
                    "total_count": total_count,
                    "missing_rate": count / total_count,
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    """生成 SQL 辅助表导入 CSV。"""

    SQL_SUPPORT_DIR.mkdir(parents=True, exist_ok=True)

    dataset_overview = prepare_dataset_overview()
    dataset_overview.to_csv(
        SQL_SUPPORT_DIR / "dataset_overview_for_mysql.csv",
        index=False,
        encoding="utf-8-sig",
    )

    label_distribution = prepare_label_distribution()
    label_distribution.to_csv(
        SQL_SUPPORT_DIR / "label_distribution_for_mysql.csv",
        index=False,
        encoding="utf-8-sig",
    )

    feature_missing_summary = pd.concat(
        [prepare_overall_missing_summary(), prepare_class_missing_summary()],
        ignore_index=True,
    )
    feature_missing_summary.to_csv(
        SQL_SUPPORT_DIR / "feature_missing_summary_for_mysql.csv",
        index=False,
        encoding="utf-8-sig",
    )

    print(f"已生成 SQL 辅助表导入文件：{SQL_SUPPORT_DIR}")


if __name__ == "__main__":
    main()
