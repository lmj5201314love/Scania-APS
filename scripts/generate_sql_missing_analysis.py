"""生成 Scania APS 宽表缺失率 SQL。

脚本只读取训练集 CSV 表头，不读取完整数据，不修改原始数据。
生成的 `sql/generated_missing_rate_analysis.sql` 可在 MySQL 导入宽表后执行，
用于复核 Day 2 的缺失率和 pos/neg 缺失模式差异。
"""

from __future__ import annotations

import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRAIN_CSV = PROJECT_ROOT / "data" / "raw" / "aps_failure_training_set.csv"
OUTPUT_SQL = PROJECT_ROOT / "sql" / "generated_missing_rate_analysis.sql"
LABEL_COL = "class"


def quote_identifier(name: str) -> str:
    """用反引号包裹 MySQL 字段名。"""

    return f"`{name.replace('`', '``')}`"


def read_feature_names(csv_path: Path) -> list[str]:
    """只读取 CSV 表头，并排除标签列 class。"""

    with csv_path.open("r", encoding="utf-8", newline="") as file:
        header = next(csv.reader(file))
    return [col for col in header if col != LABEL_COL]


def build_overall_select(table_name: str, dataset: str, feature_name: str) -> str:
    """生成某个字段的整体缺失率 SELECT。"""

    col = quote_identifier(feature_name)
    return f"""SELECT
  '{dataset}' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  '{feature_name}' AS feature_name,
  SUM(CASE WHEN {col} IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN {col} IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `{table_name}`"""


def build_class_select(feature_name: str) -> str:
    """生成训练集中某个字段按 class 分组的缺失率 SELECT。"""

    col = quote_identifier(feature_name)
    return f"""SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  '{feature_name}' AS feature_name,
  SUM(CASE WHEN {col} IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN {col} IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`"""


def build_sql(feature_names: list[str]) -> str:
    """拼接整体缺失率和正负样本缺失率 SQL。"""

    overall_parts = []
    for feature in feature_names:
        overall_parts.append(build_overall_select("raw_aps_train", "train", feature))
        overall_parts.append(build_overall_select("raw_aps_test", "test", feature))

    class_parts = [build_class_select(feature) for feature in feature_names]

    return f"""-- Day 3：自动生成的宽表缺失率 SQL
-- 本文件由 scripts/generate_sql_missing_analysis.py 生成。
-- 只用于 MySQL 导入 raw_aps_train/raw_aps_test 后复核缺失率，不做填充、删列或建模。

USE scania_aps_project;

-- 1. train/test 每个字段整体缺失率。
-- 可直接查询，也可以将结果 INSERT INTO feature_missing_summary。
WITH overall_missing AS (
{(chr(10) + "UNION ALL" + chr(10)).join(overall_parts)}
)
SELECT *
FROM overall_missing
ORDER BY dataset, missing_rate DESC, feature_name;

-- 2. 训练集 pos/neg 样本每个字段缺失率。
WITH class_missing AS (
{(chr(10) + "UNION ALL" + chr(10)).join(class_parts)}
)
SELECT *
FROM class_missing
ORDER BY feature_name, class_label;
"""


def main() -> None:
    """生成 `sql/generated_missing_rate_analysis.sql`。"""

    feature_names = read_feature_names(TRAIN_CSV)
    OUTPUT_SQL.write_text(build_sql(feature_names), encoding="utf-8")
    print(f"已生成 {OUTPUT_SQL}")


if __name__ == "__main__":
    main()
