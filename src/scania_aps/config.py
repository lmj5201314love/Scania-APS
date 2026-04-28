"""项目配置读取工具。

统一从 config/config.yaml 读取路径、标签、缺失值 token、业务成本和评估指标。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


def find_project_root(start: Path | None = None) -> Path:
    """向上查找包含 config/config.yaml 的项目根目录。"""

    current = (start or Path.cwd()).resolve()

    for path in [current, *current.parents]:
        if (path / "config" / "config.yaml").exists():
            return path

    raise FileNotFoundError("未找到 config/config.yaml，请确认当前路径在项目目录内。")


def load_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """读取 YAML 配置文件，返回原始 dict。"""

    if config_path is None:
        project_root = find_project_root()
        config_path = project_root / "config" / "config.yaml"
    else:
        config_path = Path(config_path).resolve()
        project_root = config_path.parents[1]

    with Path(config_path).open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    config["_project_root"] = project_root
    return config


@dataclass(frozen=True)
class ScaniaConfig:
    """项目常用配置对象。"""

    project_root: Path
    train_raw: Path
    test_raw: Path
    label_column: str
    missing_value_token: str
    positive_label: str
    negative_label: str
    target_mapping: dict[str, int]
    false_positive_cost: int
    false_negative_cost: int
    primary_metrics: list[str]


def get_config(config_path: str | Path | None = None) -> ScaniaConfig:
    """读取并整理项目配置。"""

    raw_config = load_config(config_path)
    project_root = raw_config["_project_root"]

    return ScaniaConfig(
        project_root=project_root,
        train_raw=project_root / raw_config["paths"]["train_raw"],
        test_raw=project_root / raw_config["paths"]["test_raw"],
        label_column=raw_config["data"]["label_column"],
        missing_value_token=raw_config["data"]["missing_value_token"],
        positive_label=raw_config["data"]["positive_label"],
        negative_label=raw_config["data"]["negative_label"],
        target_mapping=raw_config["data"]["target_mapping"],
        false_positive_cost=raw_config["business_cost"]["false_positive"],
        false_negative_cost=raw_config["business_cost"]["false_negative"],
        primary_metrics=raw_config["evaluation"]["primary_metrics"],
    )