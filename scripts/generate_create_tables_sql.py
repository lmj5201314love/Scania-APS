"""生成 Day 3 MySQL 建表 SQL。

这是 Day 3 标准入口脚本，用于根据
`data/raw/aps_failure_training_set.csv` 的表头生成
`sql/01_create_tables.sql`。

脚本只读取 CSV 表头，不读取完整原始数据，不修改 `data/raw/`。
实际生成逻辑复用 `generate_mysql_schema.py`，避免维护两套建表规则。
"""

from __future__ import annotations

from generate_mysql_schema import main


if __name__ == "__main__":
    main()
