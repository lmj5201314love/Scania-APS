# MySQL 导入说明

本文档用于 Day 3：SQL 数据质量分析支持。目标是在本地 MySQL 中导入 Scania APS 原始 train/test 数据，并运行 `sql/` 下的检查脚本复核 Day 2 的核心发现。

## 1. 创建数据库

先执行：

```sql
source sql/00_init_database.sql;
```

该脚本会创建并切换到 `scania_aps_project` 数据库，字符集使用 `utf8mb4`。

## 2. 创建表

执行：

```sql
source sql/01_create_tables.sql;
```

该脚本创建：

- `raw_aps_train`
- `raw_aps_test`
- `dataset_overview`
- `label_distribution`
- `feature_missing_summary`
- `model_prediction_result`

其中 `model_prediction_result` 只是为后续模型结果回写预留，Day 3 不写入真实预测数据。

## 3. 使用 MySQL Workbench 导入 CSV

原始文件位于：

- `data/raw/aps_failure_training_set.csv`
- `data/raw/aps_failure_test_set.csv`

导入时建议：

1. 目标表分别选择 `raw_aps_train` 和 `raw_aps_test`。
2. CSV 第一行为字段名。
3. 不导入 `sample_id`，让数据库自增生成。
4. `class` 保留为字符串字段。
5. 170 个匿名特征字段导入为 `DOUBLE NULL`。

## 4. 处理原始 CSV 中的 `"na"`

原始 CSV 使用字符串 `"na"` 表示缺失值。导入 MySQL 时必须将 `"na"` 识别为 `NULL`，否则数值字段导入可能失败或产生错误值。

可选方式：

- 如果 MySQL Workbench 导入向导支持空值映射，将 `"na"` 设置为 NULL。
- 如果导入工具不支持该映射，可以先导入到全 VARCHAR 的临时表，再用 `NULLIF(col, 'na')` 转入正式宽表。
- 不要修改或覆盖 `data/raw/` 下的原始 CSV。需要临时转换时，应写入 `data/interim/` 或数据库临时表。

## 5. 导入后运行检查 SQL

建议按顺序执行：

```sql
source sql/02_import_check.sql;
source sql/03_data_quality_analysis.sql;
source sql/generated_missing_rate_analysis.sql;
source sql/04_label_and_missing_analysis.sql;
```

其中 `generated_missing_rate_analysis.sql` 用于逐字段计算宽表缺失率。若希望使用 `04_label_and_missing_analysis.sql` 中基于 `feature_missing_summary` 的查询，需要先将缺失率结果插入或导入该统计表。

## 6. Git 与安全注意事项

- 不提交原始 CSV、大型导出结果、真实 `.env` 或数据库密码。
- `.env.example` 只保留字段模板，不写真实密码。
- `outputs/` 下的 CSV 和 PNG 是本地运行产物，默认不提交 GitHub。

## 7. Day 3 边界

Day 3 只做 SQL 数据质量分析支持，不做缺失值填充、字段删除、模型训练、阈值优化或风险分层建模。
