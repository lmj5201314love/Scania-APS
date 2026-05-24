# MySQL 导入说明

本文档用于 Day 3：SQL 数据质量分析支持。目标是在本地 MySQL 中导入 Scania APS 原始 train/test 数据，并运行 `sql/` 下的检查与复核脚本，验证 Day 2 的核心数据质量发现。

Day 3 的 SQL 只用于数据导入检查、数据质量复核和缺失值结构分析，不做缺失值填充、字段删除、模型训练、阈值优化或风险分层建模。

## 1. 创建数据库

先执行：

```sql
source sql/00_init_database.sql;
````

该脚本会创建并切换到 `scania_aps_project` 数据库，字符集使用 `utf8mb4`。

## 2. 创建表

执行：

```sql
source sql/01_create_tables.sql;
```

该脚本创建两类表。

原始数据表：

* `raw_aps_train`
* `raw_aps_test`

Day 3 数据质量复核辅助表：

* `dataset_overview`
* `label_distribution`
* `feature_missing_summary`

后续建模阶段预留表：

* `model_prediction_result`

其中 `model_prediction_result` 只是为 Day 6 之后的模型预测结果回写预留，Day 3 不写入真实预测数据。

`sql/01_create_tables.sql` 是根据原始 CSV 表头生成的建表脚本。由于 Scania APS 数据集包含 170 个匿名数值特征，raw 宽表字段较多是正常现象，不建议手动维护字段列表。

## 3. 使用 MySQL Workbench 导入 CSV

原始文件位于：

* `data/raw/aps_failure_training_set.csv`
* `data/raw/aps_failure_test_set.csv`

导入时建议：

1. 目标表分别选择 `raw_aps_train` 和 `raw_aps_test`。
2. CSV 第一行为字段名。
3. 不导入 `sample_id`，让数据库自增生成。
4. `class` 保留为字符串字段。
5. 170 个匿名特征字段导入为 `DOUBLE NULL`。

## 4. 处理原始 CSV 中的 `"na"`

原始 CSV 使用字符串 `"na"` 表示缺失值。导入 MySQL 时必须将 `"na"` 识别为 `NULL`，否则数值字段导入可能失败或产生错误值。

可选方式：

* 如果 MySQL Workbench 导入向导支持空值映射，将 `"na"` 设置为 `NULL`。
* 如果导入工具不支持该映射，可以先导入到全 `VARCHAR` 的临时表，再用 `NULLIF(col, 'na')` 转入正式宽表。
* 不要修改或覆盖 `data/raw/` 下的原始 CSV。需要临时转换时，应写入 `data/interim/` 或数据库临时表。

完成导入后，可以通过 `02_import_check.sql` 和后续缺失率统计结果确认 `"na"` 是否被正确转换为 `NULL`。

## 5. 导入后运行检查 SQL

Day 3 推荐使用“导入检查 + 汇总复核”的方式执行 SQL，不把自动生成的逐字段宽表 SQL 作为主线流程。

### 5.1 主线执行流程

先检查原始 CSV 是否成功导入 MySQL：

```sql
source sql/02_import_check.sql;
```

该脚本用于确认：

* train/test 行数是否符合预期；
* `class` 是否只有 `pos` / `neg`；
* `class` 是否存在 `NULL`；
* `sample_id` 是否唯一。

然后执行基础数据质量复核：

```sql
source sql/03_data_quality_analysis.sql;
```

该脚本用于复核：

* 数据集规模；
* 标签分布；
* `target` 映射规则；
* 基础完整性检查。

### 5.2 导入缺失值汇总表

`sql/04_label_and_missing_analysis.sql` 依赖 `feature_missing_summary` 表。

推荐做法是先在 Python / notebook 中生成缺失值汇总结果，再导入 MySQL 的 `feature_missing_summary` 表。该表用于保存：

* train/test 每个字段的整体缺失率；
* 训练集中 pos/neg 分组后的字段缺失率；
* 每个字段的 `missing_count`、`total_count` 和 `missing_rate`。

导入 `feature_missing_summary` 后，再执行：

```sql
source sql/04_label_and_missing_analysis.sql;
```

该脚本用于复核：

* 缺失率分层；
* 高缺失字段；
* train/test 缺失率差异；
* pos/neg 缺失率差异。

### 5.3 可选：完全使用 SQL 重新计算逐字段缺失率

如果希望完全在 MySQL 中重新计算 170 个匿名特征的逐字段缺失率，可以运行：

```bash
python scripts/generate_sql_missing_analysis.py
```

该脚本会生成逐字段缺失率 SQL。

由于生成文件较长，属于机器生成的复核脚本，不建议作为主线 SQL 文件手动维护。推荐将生成结果放在：

```text
sql/generated/generated_missing_rate_analysis.sql
```

如需执行，可运行：

```sql
source sql/generated/generated_missing_rate_analysis.sql;
```

注意：该文件只用于 SQL-only 场景下复核缺失率。日常项目展示和报告中，建议优先使用 `feature_missing_summary` 辅助表和 `04_label_and_missing_analysis.sql`。

## 6. 推荐 SQL 执行顺序

Day 3 主线推荐顺序如下：

```sql
source sql/00_init_database.sql;
source sql/01_create_tables.sql;

-- 手动或通过 MySQL Workbench 导入 raw CSV 后执行：
source sql/02_import_check.sql;
source sql/03_data_quality_analysis.sql;

-- 导入 feature_missing_summary 后执行：
source sql/04_label_and_missing_analysis.sql;
```

如果已经将文件名调整为更清晰的版本，例如：

* `03_data_quality_summary.sql`
* `04_missing_summary_analysis.sql`

则对应执行顺序可以改为：

```sql
source sql/00_init_database.sql;
source sql/01_create_tables.sql;

-- 手动或通过 MySQL Workbench 导入 raw CSV 后执行：
source sql/02_import_check.sql;
source sql/03_data_quality_summary.sql;

-- 导入 feature_missing_summary 后执行：
source sql/04_missing_summary_analysis.sql;
```

## 7. Git 与安全注意事项

* 不提交原始 CSV、大型导出结果、真实 `.env` 或数据库密码。
* `.env.example` 只保留字段模板，不写真实密码。
* `outputs/` 下的 CSV 和 PNG 是本地运行产物，默认不提交 GitHub。
* 自动生成的长 SQL 文件建议放在 `sql/generated/`，或加入 `.gitignore`，避免主线 SQL 目录过重。

如果选择不提交自动生成 SQL，可以在 `.gitignore` 中加入：

```gitignore
sql/generated/
sql/generated_missing_rate_analysis.sql
```

## 8. Day 3 边界

Day 3 只做 SQL 数据质量分析支持，具体包括：

* 创建本地 MySQL 数据库；
* 创建 raw 数据表和数据质量复核辅助表；
* 导入原始 train/test CSV；
* 检查导入后的行数、标签取值、`class` 空值和 `sample_id` 完整性；
* 复核数据规模、标签分布和 `target` 映射；
* 基于 `feature_missing_summary` 复核缺失率分层、高缺失字段、train/test 缺失差异和 pos/neg 缺失差异。

Day 3 不做：

* 缺失值填充；
* 字段删除；
* 特征工程；
* 模型训练；
* 模型调参；
* 阈值优化；
* 风险分层建模。

逐字段缺失率 SQL 可以由脚本自动生成，但该生成文件只作为可选复核工具，不作为主线 SQL 文件手动维护。

## 9. Day 19 业务分析表导入说明

Day 19 新增了一组面向业务交付的 MySQL 导入表，用于在 MySQL Workbench 中复核最终候选方案的维修容量、风险等级、错误类型、成本对比和阈值敏感性。

本轮需要先运行建表 SQL：

```sql
source sql/00_create_business_analysis_tables.sql;
```

然后导入以下 CSV：

| CSV | 目标 MySQL 表 | 说明 |
|---|---|---|
| `outputs/sql_exports/model_prediction_results.csv` | `model_prediction_results` | Day14 `median_all_structural_all` final candidate 的 official test 样本级预测结果。 |
| `outputs/sql_exports/model_policy_comparison.csv` | `model_policy_comparison` | naive baseline、Day14、Day16 和 Day18 OOF 的策略级成本对比。 |
| `outputs/sql_exports/threshold_sensitivity_results.csv` | `threshold_sensitivity_results` | 基于最终候选概率的阈值敏感性分析表。 |

建议检查 SQL：

```sql
SELECT COUNT(*) FROM model_prediction_results;
SELECT COUNT(*) FROM model_policy_comparison;
SELECT COUNT(*) FROM threshold_sensitivity_results;

SELECT * FROM model_prediction_results LIMIT 5;

SELECT
    confusion_type,
    COUNT(*) AS sample_count
FROM model_prediction_results
GROUP BY confusion_type;
```

注意事项：

* `sample_id` 是匿名样本编号，不是真实车辆 ID。
* SQL 中如使用 `@fp_cost = 10`、`@fn_cost = 500`，需要人工保持与 `config/config.yaml` 一致。
* `day18_oof_ensemble_best` 是 OOF train 内部结果，不要与 official test 结果直接横向比较。
* `threshold_sensitivity_results` 只用于策略敏感性分析，不用于反向修改最终方案。当前最终候选仍保留 Day14 `median_all_structural_all` 和 threshold `0.18`。
