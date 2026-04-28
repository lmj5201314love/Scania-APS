"""根据 Scania APS 原始 CSV 表头生成 MySQL 建表 SQL。

脚本只读取 `data/raw/aps_failure_training_set.csv` 的表头，不读取完整数据，
不修改原始数据。生成结果写入 `sql/01_create_tables.sql`，用于 Day 3
SQL 数据质量分析支持。
"""

from __future__ import annotations

import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRAIN_CSV = PROJECT_ROOT / "data" / "raw" / "aps_failure_training_set.csv"
OUTPUT_SQL = PROJECT_ROOT / "sql" / "01_create_tables.sql"
LABEL_COL = "class"


def quote_identifier(name: str) -> str:
    """用反引号包裹 MySQL 字段名，避免关键字或特殊字符冲突。"""

    return f"`{name.replace('`', '``')}`"


def read_header(csv_path: Path) -> list[str]:
    """只读取 CSV 表头，不扫描数据内容。"""

    with csv_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file)
        return next(reader)


def build_raw_table_sql(table_name: str, columns: list[str]) -> str:
    """生成 raw_aps_train / raw_aps_test 宽表建表语句。"""

    feature_columns = [col for col in columns if col != LABEL_COL]
    column_lines = [
        "  `sample_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '导入后的行号主键',",
        "  `class` VARCHAR(10) NULL COMMENT '原始标签：pos 表示 APS 相关故障，neg 表示非 APS 相关故障',",
    ]
    column_lines.extend(
        f"  {quote_identifier(col)} DOUBLE NULL COMMENT '匿名数值特征'," for col in feature_columns
    )
    column_lines.append("  PRIMARY KEY (`sample_id`),")
    column_lines.append("  KEY `idx_class` (`class`)")

    return f"""CREATE TABLE IF NOT EXISTS `{table_name}` (
{chr(10).join(column_lines)}
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Scania APS 原始宽表：{table_name}';
"""


def build_sql(columns: list[str]) -> str:
    """拼接 Day 3 所需的宽表和辅助统计表 SQL。"""

    feature_count = len([col for col in columns if col != LABEL_COL])
    return f"""-- Day 3：Scania APS MySQL 建表脚本
-- 本文件由 scripts/generate_mysql_schema.py 根据原始 CSV 表头生成。
-- 只定义表结构，不导入数据，不做缺失值填充、字段删除或建模。
-- 原始数据共有 {feature_count} 个匿名数值特征，标签字段为 class。

USE scania_aps_project;

-- 为避免误删已导入的数据，本脚本只使用 CREATE TABLE IF NOT EXISTS。
-- 如果确实需要重建表，请先手动备份并在本地确认后再执行删表操作。

{build_raw_table_sql("raw_aps_train", columns)}

{build_raw_table_sql("raw_aps_test", columns)}

CREATE TABLE IF NOT EXISTS `dataset_overview` (
  `dataset` VARCHAR(20) NOT NULL COMMENT 'train 或 test',
  `total_rows` BIGINT NOT NULL,
  `total_columns` INT NOT NULL,
  `feature_count` INT NOT NULL,
  `label_column_exists` TINYINT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`dataset`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据集规模概览，可由 SQL 查询结果写入';

CREATE TABLE IF NOT EXISTS `label_distribution` (
  `dataset` VARCHAR(20) NOT NULL COMMENT 'train 或 test',
  `class` VARCHAR(10) NOT NULL COMMENT 'pos 或 neg',
  `sample_count` BIGINT NOT NULL,
  `sample_ratio` DOUBLE NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`dataset`, `class`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='标签分布统计，可由 SQL 查询结果写入';

CREATE TABLE IF NOT EXISTS `feature_missing_summary` (
  `dataset` VARCHAR(20) NOT NULL COMMENT 'train 或 test',
  `summary_scope` VARCHAR(20) NOT NULL DEFAULT 'overall' COMMENT 'overall 或 by_class',
  `class_label` VARCHAR(10) NOT NULL DEFAULT 'all' COMMENT 'overall 使用 all，分类统计使用 pos/neg',
  `feature_name` VARCHAR(64) NOT NULL,
  `missing_count` BIGINT NOT NULL,
  `total_count` BIGINT NOT NULL,
  `missing_rate` DOUBLE NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`dataset`, `summary_scope`, `class_label`, `feature_name`),
  KEY `idx_feature_missing_rate` (`feature_name`, `missing_rate`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='字段缺失率统计，可导入 Day 2 产物或由生成 SQL 得到';

CREATE TABLE IF NOT EXISTS `model_prediction_result` (
  `prediction_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `dataset` VARCHAR(20) NOT NULL COMMENT '后续通常为 test 或 validation',
  `sample_id` BIGINT UNSIGNED NOT NULL,
  `true_class` VARCHAR(10) NULL,
  `true_target` TINYINT NULL,
  `predicted_probability` DOUBLE NULL,
  `predicted_target` TINYINT NULL,
  `threshold` DOUBLE NULL,
  `risk_level` VARCHAR(20) NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`prediction_id`),
  KEY `idx_prediction_dataset_sample` (`dataset`, `sample_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='后续模型预测结果回写预留表，Day 3 不写入真实数据';
"""


def main() -> None:
    """生成 `sql/01_create_tables.sql`。"""

    columns = read_header(TRAIN_CSV)
    OUTPUT_SQL.write_text(build_sql(columns), encoding="utf-8")
    print(f"已生成 {OUTPUT_SQL}")


if __name__ == "__main__":
    main()
