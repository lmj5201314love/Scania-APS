"""生成 Day 3 MySQL 建表 SQL。

这是 Day 3 标准入口脚本，用于根据 cfg 中配置的训练集路径读取表头并生成
`sql/01_create_tables.sql`。

脚本只读取 CSV 表头，不读取完整原始数据，不修改原始数据文件。
实际生成逻辑复用 `generate_mysql_schema.py`，避免维护两套建表规则。
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))

from generate_mysql_schema import main as generate_schema
from scania_aps.config import get_config


def main() -> None:
    """基于 cfg 生成 `sql/01_create_tables.sql`。"""

    cfg = get_config(PROJECT_ROOT / "config" / "config.yaml")
    generate_schema(cfg)


if __name__ == "__main__":
    main()
