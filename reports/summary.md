# Day 1 业务理解总结

## 项目一句话说明

本项目使用 Scania APS 重卡空气压力系统故障数据，预测车辆是否存在 APS 系统相关故障，并结合误报和漏报成本，支持维修优先级和风险分层决策。

## 业务背景

在重卡运营和制造业售后场景中，空气压力系统故障可能影响车辆制动、辅助系统和整体运行可靠性。真实业务中，维修团队通常需要在有限检修资源下判断哪些车辆应优先检查，哪些车辆可以延后处理。

Scania APS 数据集适合用来模拟这种工业预测性维护问题，因为它具有真实工业数据常见特征：字段数量多、特征被匿名化、缺失值明显、正负样本极不平衡，并且误报和漏报的业务成本差异很大。

## APS 系统故障预测的业务意义

APS 系统相关故障如果被提前识别，可以帮助维修团队更早安排检查，降低车辆 breakdown 风险和后续维修成本。模型输出不应该只停留在“是否故障”的分类结果，而应进一步转化为风险等级和维修优先级，帮助业务人员做决策。

## 标签含义

- `pos`：正类，表示与 APS 系统相关的故障样本，后续建模时映射为 `1`。
- `neg`：负类，表示非 APS 系统相关的样本，后续建模时映射为 `0`。

Day 1 不对标签分布下具体结论，后续会在数据理解阶段读取原始训练集后进行统计。

## FP 和 FN 的业务含义

- FP，False Positive，误报：模型预测为 APS 故障，但实际不是 APS 故障。业务影响是不必要的检查和维修资源占用，成本设定为 `10`。
- FN，False Negative，漏报：模型预测为非 APS 故障，但实际是 APS 故障。业务影响是故障车辆未被及时识别，可能导致 breakdown、停机和更高维修成本，成本设定为 `500`。

## 为什么 FN 成本远高于 FP

在预测性维护场景中，多检查一辆正常车辆通常只带来人工、时间和机会成本；但漏掉一辆真实 APS 故障车辆，可能导致车辆在运营中发生更严重故障，带来停机、救援、延迟交付和更高维修费用。因此 FN 的业务损失远高于 FP。

## 为什么不能只看 accuracy

该项目是典型的类别不平衡问题。如果负类样本占绝大多数，模型即使大量预测为 `neg`，也可能得到看似较高的 accuracy，但这类模型可能漏掉关键的 `pos` 故障样本。对业务来说，漏报真实 APS 故障比整体准确率下降更重要。

因此后续评估应重点关注：

- `precision`：预测为故障的样本中有多少是真的故障；
- `recall`：真实故障中有多少被识别出来；
- `F1` 和 `F2`：综合 precision 与 recall，其中 F2 更偏向 recall；
- `PR-AUC`：适合类别不平衡场景下观察模型排序能力；
- `total_cost = FP * 10 + FN * 500`：最终业务成本。

## 后续要回答的核心问题

1. 原始训练集和测试集的字段规模、缺失情况和标签分布如何？
2. 哪些字段缺失严重，是否需要删除、保留或特殊处理？
3. 在类别极不平衡情况下，baseline 模型能达到怎样的 recall 和成本水平？
4. XGBoost 等模型是否能降低 FN 数量和总业务成本？
5. 哪个预测阈值能在误报成本和漏报成本之间取得更合理的业务权衡？
6. 如何把预测概率转化为高、中、低风险分层和维修优先级建议？

# Day 2 基础数据质量与缺失值分析总结

## 数据规模

Day 2 读取了官方提供的原始训练集和测试集，读取方式为 `pd.read_csv(path, na_values="na")`，没有修改原始数据。

- 训练集：60,000 行，171 列，其中 170 个特征字段和 1 个标签字段。
- 测试集：16,000 行，171 列，其中 170 个特征字段和 1 个标签字段。
- train/test 字段完全一致，均包含 `class` 标签列。
- 除 `class` 外，未发现非数值字段；训练集为 1 个 object 字段和 170 个数值字段。

## 标签分布和类别不平衡

训练集中 `neg` 为 59,000 条，占 98.33%；`pos` 为 1,000 条，占 1.67%。测试集中 `neg` 为 15,625 条，占 97.66%；`pos` 为 375 条，占 2.34%。

这说明 Scania APS 是明显的类别极不平衡问题。后续建模不能把 accuracy 作为核心目标，否则模型可能通过大量预测 `neg` 获得看似较高的准确率，却漏掉真正重要的 APS 故障样本。后续应重点关注 recall、F2、PR-AUC 和 `total_cost = FP * 10 + FN * 500`。

## 缺失值整体情况

训练集整体单元格缺失率为 8.28%，测试集整体单元格缺失率为 8.36%。两份数据均有 169 列存在缺失，说明缺失值是该工业数据集的核心数据质量问题之一。

按缺失率分层统计，train/test 分布完全一致：

- 0% 缺失：2 列
- 0-5% 缺失：127 列
- 5-20% 缺失：18 列
- 20-50% 缺失：16 列
- 50-80% 缺失：6 列
- 80-100% 缺失：2 列

## 高缺失字段情况

训练集和测试集中，缺失率大于等于 50% 的字段均为 8 个；缺失率大于等于 80% 的字段均为 2 个；没有发现缺失率等于 100% 的字段。

高缺失字段主要包括：`br_000`、`bq_000`、`bp_000`、`bo_000`、`ab_000`、`cr_000`、`bn_000`、`bm_000`。
Day 2只识别这些字段，不做删除或填充。后续需要结合模型表现、业务解释和数据泄漏风险再决定处理策略。

## train/test 缺失模式对比

train/test 缺失率差异整体很小。差异最大的字段为 `cl_000` 和 `ed_000`，缺失率绝对差异约为 0.55 个百分点。没有字段的 train/test 缺失率差异达到 5 个百分点，也没有字段达到 10 个百分点。

这说明从缺失模式看，官方 train/test 划分整体较一致，暂未观察到明显的数据分布断层。

## pos/neg 缺失模式对比

在训练集中，pos 和 neg 样本的缺失模式存在明显差异。差异最大的字段为 `br_000`，neg 缺失率为 83.35%，pos 缺失率为 9.00%，绝对差异约为 74.35 个百分点。

此外，有 64 个字段的 pos/neg 缺失率差异达到 10 个百分点以上，62 个字段达到 20 个百分点以上。这个现象说明正负样本在数据采集或系统状态上可能存在不同缺失模式。当前阶段只做观察，不能直接断言“缺失本身一定可以作为特征”，后续可以进一步评估缺失指示变量或模型对缺失模式的利用方式。

## 重复值情况

训练集和测试集均未发现完全重复行：

- 训练集重复行：0
- 测试集重复行：0

## Day 3 建议

Day 3 建议进入 SQL 数据质量分析支持阶段：基于 Day 2 的发现，编写 SQL 脚本复核数据规模、标签分布、缺失字段统计、高缺失字段清单和基础质量检查
SQL阶段仍不做建模、不做填充、不做阈值优化，重点是让数据质量分析可以被数据库查询复现。

# Day 3 SQL 数据质量分析支持总结

## Day 3 目标

Day 3 的目标是让 Day 2 的核心数据质量分析可以被 MySQL / SQL 查询复现，体现 SQL 在制造业数据分析项目中的作用。本阶段只准备 SQL 脚本、建表结构、导入后检查和缺失率复核查询，不进行模型训练、缺失值填充、字段删除或阈值优化。

## SQL 文件完成情况

已完善以下 SQL 文件：

- `sql/00_init_database.sql`：创建并切换到 `scania_aps_project` 数据库，字符集使用 `utf8mb4`。
- `sql/01_create_tables.sql`：根据原始 CSV 表头自动生成 raw 宽表，并创建
  `dataset_overview`、`label_distribution`、`feature_missing_summary` 和后续预留的
  `model_prediction_result` 表。
- `sql/02_import_check.sql`：提供导入后行数、标签取值、标签分布、`class` 空值和 `sample_id` 唯一性检查。
- `sql/03_data_quality_analysis.sql`：提供数据集概览、标签分布、`class` 空值、target 映射和主键完整性检查。
- `sql/04_label_and_missing_analysis.sql`：提供标签分布、缺失率分层、高缺失字段、train/test 缺失率差异和 pos/neg 缺失率差异分析查询。
- `sql/generated_missing_rate_analysis.sql`：由脚本自动生成逐字段缺失率 SQL，覆盖 train/test 整体缺失率和训练集 pos/neg 分组缺失率。

## 可用 SQL 复核的 Day 2 发现

Day 3 SQL 可以复核以下 Day 2 发现：

1. 训练集 60,000 行、测试集 16,000 行。
2. train/test 均包含 170 个匿名数值特征和 `class` 标签列。
3. `pos` 样本占比很低，属于类别极不平衡问题。
4. `br_000`、`bq_000`、`bp_000`、`bo_000`、`ab_000`、`cr_000`、`bn_000`、`bm_000` 等字段属于高缺失字段。
5. train/test 缺失模式整体接近。
6. pos/neg 缺失模式差异明显，后续可以进一步评估缺失模式是否对建模有帮助。
7. `sample_id` 可作为导入后的行级主键，用于基础完整性检查和后续预测结果回写。

## 当前 SQL 执行状态

当前尚未真实连接本地 MySQL 执行这些 SQL。SQL 脚本已准备，待本地 MySQL 导入原始 CSV 后执行。项目报告中不能写成“SQL 已运行并得到结果”，只能表述为“SQL 复核脚本已准备完成”。

## 新增支持文件

新增 `scripts/generate_create_tables_sql.py`，用于根据原始训练集表头自动生成 `sql/01_create_tables.sql`，避免手写 170 个字段出错。

新增 `scripts/generate_sql_missing_analysis.py`，用于生成 `sql/generated_missing_rate_analysis.sql`，复核宽表逐字段缺失率和 pos/neg 缺失模式差异。

新增 `scripts/prepare_sql_support_tables.py`，用于将 Day 2 的输出表整理成适合导入 MySQL 辅助表的 CSV，包括
`dataset_overview`、`label_distribution` 和 `feature_missing_summary`。

新增 `docs/mysql_import_guide.md`，说明如何创建数据库、创建表、导入 CSV、处理 `"na"` 缺失值，以及导入后应该运行哪些 SQL 检查脚本。

新增 `reports/missing_value_strategy.md`，记录缺失值处理原则、高缺失字段关注清单和后续建模阶段可比较的处理方案。该文档只制定策略，不执行填充、删列或建模。

## Day 4 建议

Day 4 建议进入 baseline 建模准备阶段：在不使用测试集拟合任何规则的前提下，设计训练集内部验证方案，建立简单 baseline，并用 recall、F2、PR-AUC
和业务成本意识来评估模型方向。Day 4 开始前仍应避免直接删除高缺失字段或做未经验证的复杂特征工程。

# Day 4 baseline 建模总结

## Day 4 目标

Day 4 的目标是跑通第一版 baseline 建模闭环：统一使用 `config/config.yaml` 读取路径、标签映射、缺失值 token、业务成本和默认模型参数；在不修改原始数据、不重新切分 train/test、不使用测试集拟合处理规则的前提下，完成基础缺失处理、baseline 训练、成本敏感指标计算和预测结果输出。

## 使用的缺失处理策略

本阶段只比较两种基础策略：

- `median_all`：保留全部 170 个特征，只使用训练集拟合中位数填充器，再应用到测试集。
- `drop_high_missing_median`：只基于训练集缺失率识别缺失率大于等于 80% 的字段，删除 2 个高缺失字段后，再使用训练集拟合中位数填充器并应用到测试集。

Day 4 没有进行复杂特征工程，也没有使用测试集决定缺失处理规则。

## 使用的 baseline 模型

本阶段运行了两类 baseline：

- `dummy_prior`：只学习训练集标签先验分布，用作类别不平衡问题的最低参照。
- `logistic_regression_balanced`：使用 `class_weight="balanced"` 的 Logistic Regression，并在模型流程中加入标准化处理。

## 默认阈值下的主要结果

以下结果来自 `outputs/metrics/day4_baseline_metrics.csv`，默认阈值为 `0.5`，业务成本为 `FP=10`、`FN=500`。

| model_name | strategy | precision | recall | F2 | PR-AUC | FP | FN | total_cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| dummy_prior | median_all | 0.0000 | 0.0000 | 0.0000 | 0.0234 | 0 | 375 | 187500 |
| logistic_regression_balanced | median_all | 0.4819 | 0.9227 | 0.7800 | 0.7982 | 372 | 29 | 18220 |
| dummy_prior | drop_high_missing_median | 0.0000 | 0.0000 | 0.0000 | 0.0234 | 0 | 375 | 187500 |
| logistic_regression_balanced | drop_high_missing_median | 0.4860 | 0.9280 | 0.7852 | 0.7994 | 368 | 27 | 17180 |

结果说明：Dummy baseline 在默认阈值下没有识别出任何正类样本，漏报全部 375 个 APS 故障样本，总成本达到 187,500。这再次说明该项目不能以 accuracy 作为核心指标，因为多数类预测在业务上会造成严重漏报。

Logistic Regression baseline 明显降低了漏报数量和总业务成本。其中 `drop_high_missing_median` 策略在当前 baseline 下略优于
`median_all`，FN 从 29 降到 27，total cost 从 18,220 降到 17,180。这个结果只代表第一版 baseline，不代表最终最优方案。

## Day 5 建议

Day 5 建议在当前 cfg、数据准备和评估函数的基础上训练提升模型，例如 Random Forest 或 XGBoost 的第一版模型，并继续使用 recall、F2、PR-AUC 和
total cost 作为核心评估指标。Day 5 可以比较不同模型与当前 Logistic Regression baseline 的差异，但仍应避免复杂 GridSearch
和阈值优化；阈值成本曲线更适合放到 Day 6 单独处理。

# Day 5 提升模型对比总结

## Day 5 目标

Day 5 的目标是在 Day 4 baseline 基础上训练第一版提升模型，比较 Random Forest / XGBoost 与 Logistic Regression
baseline 的差异。本阶段继续统一使用 `config/config.yaml` 读取路径、标签映射、缺失值 token、默认阈值、模型参数和业务成本；不修改原始数据，不合并
train/test 重新划分，不在测试集上拟合任何处理规则。

## 使用的模型和缺失处理策略

本阶段训练了两类提升模型：

- `random_forest_balanced`：使用 `class_weight="balanced"` 处理类别不平衡。
- `xgboost_scale_pos_weight`：使用 `scale_pos_weight = neg_count / pos_count` 处理类别不平衡。

比较的缺失处理策略包括：

- `median_all`：保留全部 170 个特征，使用训练集中位数填充。
- `drop_high_missing_median`：只基于训练集缺失率删除 2 个缺失率大于等于 80% 的字段，再使用训练集中位数填充。
- `median_with_indicator`：保留全部字段，并加入缺失指示变量后再做中位数填充。该策略本阶段用于 Random Forest。

XGBoost 原生处理缺失值的策略暂未启用，避免 Day 5 范围过大；可以在后续模型优化阶段单独比较。

## Day 5 主要结果

以下结果来自 `outputs/metrics/day5_model_compare_metrics.csv`，默认阈值为 `0.5`，业务成本仍来自 cfg。

| model_name | strategy | precision | recall | F2 | PR-AUC | FP | FN | total_cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| random_forest_balanced | median_all | 0.9367 | 0.5920 | 0.6390 | 0.8842 | 15 | 153 | 76650 |
| xgboost_scale_pos_weight | median_all | 0.6357 | 0.9120 | 0.8391 | 0.9113 | 196 | 33 | 18460 |
| random_forest_balanced | drop_high_missing_median | 0.9383 | 0.5680 | 0.6167 | 0.8830 | 14 | 162 | 81140 |
| xgboost_scale_pos_weight | drop_high_missing_median | 0.6277 | 0.9173 | 0.8398 | 0.9091 | 204 | 31 | 17540 |
| random_forest_balanced | median_with_indicator | 0.9485 | 0.5893 | 0.6376 | 0.8910 | 12 | 154 | 77120 |

与 Day 4 最优 Logistic baseline 相比，XGBoost 的 PR-AUC 和 F2 更高，但在默认阈值 `0.5` 下 total cost 仍略高。Day 4 最优
Logistic + `drop_high_missing_median` 的 total cost 为 17,180；Day 5 最低 total cost 为 XGBoost +
`drop_high_missing_median` 的 17,540。

仅在 Day 5 提升模型内部比较：

- recall 最高：XGBoost + `drop_high_missing_median`，recall 为 0.9173。
- F2 最高：XGBoost + `drop_high_missing_median`，F2 为 0.8398。
- PR-AUC 最高：XGBoost + `median_all`，PR-AUC 为 0.9113。
- total cost 最低：XGBoost + `drop_high_missing_median`，total cost 为 17,540。

如果把 Day 4 Logistic baseline 一起纳入比较，Logistic + `drop_high_missing_median` 在默认阈值下的 recall 为
0.9280、total cost 为 17,180，仍然略优于当前 XGBoost 的默认阈值结果；但 XGBoost 的 F2 和 PR-AUC 更高，说明它的概率排序能力更值得进入
Day 6 阈值成本分析。Random Forest 的 precision 很高，但 recall 明显低于 Logistic 和 XGBoost，因此在 FN 成本远高于 FP
的业务设定下，默认阈值下的总成本较高。当前还不能写成最终最优模型。

## Day 6 建议

Day 6 建议基于 Day 4 Logistic baseline 和 Day 5 XGBoost 模型做阈值成本分析：在不重新训练模型的前提下，对预测概率使用不同阈值，计算
FP、FN、recall、precision、F2 和 total cost 的变化，寻找业务成本更低且召回可接受的阈值。Day 6 的重点是阈值决策和成本曲线，不是继续做大规模模型调参。

# 配置化重构小结

本次小范围 refactor 已将 Day 1-Day 3 的主要 notebook 和 SQL 辅助脚本开始统一迁移到 `config/config.yaml` 与
`get_config()`。原始 train/test 路径、缺失值 token、标签列、target 映射、输出表目录和图表目录优先从 cfg 读取，减少了在早期分析代码中重复手写
`data/raw`、`outputs/tables`、`outputs/figures` 等路径。

本次重构不改变 Day 1-Day 3 的分析逻辑和结论，不重新训练模型，不做阈值遍历，也不修改 `data/raw/`
原始数据。`notebooks/03_sql_analysis_support.ipynb` 原本为空文件，本次补成轻量 SQL 支撑检查 notebook，仅用于查看 SQL 文件和 SQL
辅助表产物位置，不新增建模内容。

下一步 Day 6 可以在当前统一配置入口的基础上，读取 Day 4 / Day 5 已生成的预测概率文件，进行阈值成本分析。

# Day 6 阈值成本敏感性分析总结

## Day 6 目标

Day 6 的目标是在不重新训练模型的前提下，读取 Day 4 / Day 5 已生成的预测概率文件，对不同分类阈值下的 precision、recall、F1、F2、FP、FN 和
total cost 做成本敏感性分析。使用的输入文件包括：

- `outputs/predictions/day4_baseline_predictions.csv`
- `outputs/predictions/day5_model_compare_predictions.csv`

本阶段不做 GridSearch、不做新的特征工程、不修改原始数据，也不做最终风险分层。

## 参与阈值分析的模型/策略

Day 6 对所有带有 `y_proba` 的 model_name + strategy 组合执行了 0.01 到 0.99 的阈值网格分析，共生成 891 行阈值结果。重点解释的候选组合包括：

- Logistic Regression + `drop_high_missing_median`
- XGBoost + `median_all`
- XGBoost + `drop_high_missing_median`

Dummy baseline 仍作为对照，但不作为后续业务建议的候选模型。

## 默认阈值 0.5 回顾

默认阈值 0.5 下，Day 4 / Day 5 的关键结果为：

- Logistic + `drop_high_missing_median`：recall = 0.9280，FN = 27，FP = 368，total cost = 17,180。
- XGBoost + `median_all`：recall = 0.9120，FN = 33，FP = 196，total cost = 18,460。
- XGBoost + `drop_high_missing_median`：recall = 0.9173，FN = 31，FP = 204，total cost = 17,540。

这些结果说明默认 0.5 阈值不一定匹配 APS 的成本结构。由于 FN 成本远高于 FP，适当降低阈值可能通过减少漏报来降低总成本。

## 低成本阈值结果

以下结果来自 `outputs/metrics/day6_best_threshold_summary.csv`，属于当前测试集回溯敏感性分析：

| model_name | strategy | best_threshold | precision | recall | F2 | FP | FN | total_cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| xgboost_scale_pos_weight | median_all | 0.20 | 0.4692 | 0.9760 | 0.8026 | 414 | 9 | 8640 |
| random_forest_balanced | median_all | 0.03 | 0.3936 | 0.9813 | 0.7556 | 567 | 7 | 9170 |
| random_forest_balanced | drop_high_missing_median | 0.02 | 0.3404 | 0.9893 | 0.7162 | 719 | 4 | 9190 |
| xgboost_scale_pos_weight | drop_high_missing_median | 0.08 | 0.3583 | 0.9840 | 0.7292 | 661 | 6 | 9610 |
| logistic_regression_balanced | drop_high_missing_median | 0.30 | 0.3958 | 0.9520 | 0.7431 | 545 | 18 | 14450 |

当前最低 total cost 出现在 XGBoost + `median_all`，阈值为 0.20，总成本为 8,640。相比该模型默认阈值 0.5 的结果，FN 从 33 降到 9，FP
从 196 增加到 414；由于漏报成本远高于误报成本，总成本从 18,460 降到 8,640。

## 指标权衡

阈值降低后，模型会预测更多样本为正类，通常表现为 recall 上升、FN 下降，同时 precision 下降、FP 上升。在 APS 业务成本设定下，较高 recall
往往更重要，但不能只看 recall 或 F2，还必须看 total cost。

XGBoost + `median_all` 在 Day 5 中已经有较高 PR-AUC，说明排序能力较好；Day 6 进一步显示，它在较低阈值下可以把 FN
明显压低，并取得当前最低成本。因此该组合值得进入 Day 7 的风险分层和维修优先级建议准备。

## 分析限制

当前阈值是在测试集预测概率上做的回溯敏感性分析，不能写成生产环境最终阈值。正式生产流程中，更严谨的做法是使用验证集选择阈值，再在测试集上进行一次最终评估。当前结果适合作为学习项目中的业务解释和 Day 7 风险分层设计依据。

## Day 7 建议

Day 7 建议基于 XGBoost + `median_all` 的预测概率和 Day 6 得到的低成本阈值，设计高、中、低风险分层和维修优先级建议。同时要保留说明：风险分层是当前项目阶段的业务解释方案，不是生产系统最终策略。

# Day 7 风险分层与项目交付总结

## 最终候选方案

Day 7 基于 Day 6 的测试集回溯阈值分析，选择以下组合作为当前项目阶段的风险分层候选方案：

```text
XGBoost + median_all + threshold 0.20
```

该方案的核心结果为：precision = 0.4692，recall = 0.9760，F2 = 0.8026，FP = 414，FN = 9，total cost = 8,640。

注意：该阈值来自测试集回溯敏感性分析，不是生产环境最终阈值。

## 风险分层规则

风险等级基于预测概率和 Day 6 低成本阈值划分：

- Critical：`y_proba >= 0.80`，建议立即检修。
- High：`0.20 <= y_proba < 0.80`，建议优先检修。
- Medium：`0.05 <= y_proba < 0.20`，建议观察复查。
- Low：`y_proba < 0.05`，建议暂不处理。

## 维修优先级和风险等级汇总

Day 7 已生成 `outputs/tables/day7_maintenance_priority_list.csv`，包含 16,000 条测试集样本的风险等级和维修动作建议。

风险等级汇总如下：

| risk_level | sample_count | actual_pos_count | tp | fp | fn | tn | suggested_action |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Critical | 411 | 324 | 324 | 87 | 0 | 0 | 立即检修 |
| High | 369 | 42 | 42 | 327 | 0 | 0 | 优先检修 |
| Medium | 415 | 6 | 0 | 0 | 6 | 409 | 观察复查 |
| Low | 14805 | 3 | 0 | 0 | 3 | 14802 | 暂不处理 |

Critical 和 High 合计覆盖 366 个实际 APS 故障样本，Medium 和 Low 中仍有 9 个 FN。该结果说明风险分层能有效帮助维修团队优先处理高风险车辆，但仍需保留人工复核和生产验证机制。

## 成本下降结果

Naive baseline 全部预测为 `neg` 时，测试集 375 个正类全部漏报，total cost = 187,500。

当前候选方案 total cost = 8,640，成本下降：

```text
cost_reduction = 178,860
cost_reduction_rate = 95.39%
```

该下降来自 FN 从 375 降到 9。虽然 FP 增加到 414，但在 FN 成本远高于 FP 的设定下，总成本显著降低。

## Day 7 交付物

已完成以下交付文件：

- `outputs/tables/day7_maintenance_priority_list.csv`
- `outputs/tables/day7_risk_level_summary.csv`
- `outputs/tables/day7_business_result_summary.csv`
- `notebooks/07_risk_level_and_business_summary.ipynb`
- `sql/07_risk_level_analysis.sql`
- `reports/project_report.md`
- `reports/resume_bullets.md`
- `reports/interview_qa.md`

README 已更新为更适合简历和面试展示的项目说明，包含核心结果、成本对比、阈值优化、风险分层、Key Findings、项目局限和运行方式。

## 项目当前完成度

当前项目已经完成从数据理解、SQL 复核、建模、阈值成本分析到风险分层交付的完整闭环。项目仍是学习和作品集项目，不应表述为可直接上线的生产系统。

## 后续可选增强方向

1. 使用验证集选择阈值，再在测试集上评估，避免测试集回溯选择阈值。
2. 引入时间戳和车辆 ID，构建真实提前预警任务。
3. 结合维修资源容量设计 Top-K 检修策略。
4. 增加模型解释，分析关键匿名特征和缺失模式。
5. 将 Day 7 风险分层表导入 MySQL，构建可复核的数据分析视图。

# Cleanup 项目结构清理总结

## 清理目标

当前项目已经完成 Day 1-7 的完整闭环，文件数量和阶段性产物较多。本次清理的目标不是新增模型，而是减少空文件和命名歧义，让项目结构更适合后续增强、简历展示和面试讲解。

## 已完成事项

- 已确认 `05_feature_engineering.ipynb` 重命名为 `05_model_improvement.ipynb`。
- 已确认 `05_export_predictions_to_mysql.py` 重命名为 `05_build_risk_tables.py`。
- 删除空的 `scripts/01_prepare_data.py`，因为当前数据读取和建模准备已经由 `src/scania_aps/data/` 与训练脚本承担。
- 删除空的 `tests/conftest.py`，因为当前测试不需要额外 pytest 配置。
- 补充 `tests/test_cost_utils.py` 和 `tests/test_threshold_utils.py`，覆盖成本函数和阈值工具的核心行为。
- 补充 `docs/project_structure.md`，说明目录职责、核心脚本入口和预留模块用途。
- 补充 `docs/data_dictionary.md`，说明 Scania APS 特征匿名化限制，避免虚构字段物理含义。
- 为后续可能使用的空模块补充中文说明，包括 database、features、predict 和 visualization 相关模块。
- 补全 `sql/05_business_cost_analysis.sql` 和 `sql/06_model_result_analysis.sql`，避免 SQL 目录存在空文件。
- 整理 `sql/07_risk_level_analysis.sql`，将成本参数改为 SQL 会话变量，并说明需要与 `config/config.yaml` 保持一致。
- 整理 README 和本 summary 的物理换行，提高 Markdown 可读性。

## 保留的空文件说明

`src/scania_aps/**/__init__.py` 继续保留为空文件。这些文件是 Python 包结构标记，不属于无用文件。

`outputs/`、`models/` 和 `data/` 下的 `.gitkeep` 继续保留，用于在 Git 中保留空目录结构。

## 后续建议

下一轮增强前，建议先基于 `docs/project_structure.md` 检查新增文件是否有明确职责。后续优先做验证集机制，再进入缺失值和特征工程消融实验。

# Enhancement 1 Validation-based Model Selection 总结

## 增强目标

Day 6 / Day 7 的低成本阈值来自 official test 上的回溯敏感性分析。该结果适合解释阈值和业务成本之间的关系，但方法论上偏乐观，因为 test 同时参与了阈值选择和结果评估。

本轮增强引入 validation set 机制：从官方 training set 中划分 `train_inner` 和 `valid`，在 `train_inner` 上训练候选模型，在 `valid` 上选择模型、缺失处理策略和阈值，最后在 official test 上只做一次最终评估。

## 数据划分

使用 `config/config.yaml` 中的 validation 配置：

- `valid_size = 0.2`
- `stratify = true`
- `random_state = 42`

划分结果如下：

| dataset | row_count | pos_count | neg_count | pos_rate |
|---|---:|---:|---:|---:|
| official_train | 60000 | 1000 | 59000 | 0.0167 |
| train_inner | 48000 | 800 | 47200 | 0.0167 |
| valid | 12000 | 200 | 11800 | 0.0167 |

划分索引已保存到：

- `data/interim/splits/train_inner_indices.csv`
- `data/interim/splits/valid_indices.csv`

## valid 上的模型和阈值选择

本轮只比较受控候选项，不做 GridSearch 和新特征工程：

- 模型：`logistic_regression_balanced`、`xgboost_scale_pos_weight`
- 缺失策略：`median_all`、`drop_high_missing_median`

valid 上按 total cost 选择出的最佳组合为：

```text
XGBoost + drop_high_missing_median + threshold 0.14
```

valid 结果：

- precision = 0.3316
- recall = 0.9750
- F2 = 0.7025
- FP = 393
- FN = 5
- total_cost = 6,430

## official test 最终评估

使用 valid 选择出的模型、策略和阈值，在 official test 上评估一次，结果为：

- model = `xgboost_scale_pos_weight`
- strategy = `drop_high_missing_median`
- threshold = 0.14
- precision = 0.4370
- recall = 0.9707
- F2 = 0.7801
- FP = 469
- FN = 11
- total_cost = 10,190

## 与 Day 6 test 回溯最优对比

| 方案 | 模型 | 策略 | 阈值 | Precision | Recall | F2 | FP | FN | Total Cost |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| valid 选择后 test 评估 | XGBoost | drop_high_missing_median | 0.14 | 0.4370 | 0.9707 | 0.7801 | 469 | 11 | 10190 |
| Day 6 test 回溯最优 | XGBoost | median_all | 0.20 | 0.4692 | 0.9760 | 0.8026 | 414 | 9 | 8640 |
| 差异 | - | - | - | -0.0323 | -0.0053 | -0.0225 | +55 | +2 | +1550 |

结论：Day 6 的 test 回溯最优结果确实存在一定乐观偏差。validation-based 流程下，official test total cost 上升 1,550，FN 增加 2，FP 增加 55。但整体仍保持高 recall 和明显低于 naive baseline 的 total cost，说明 XGBoost 方向是稳定的。

## 本轮输出文件

- `outputs/metrics/validation_threshold_metrics.csv`
- `outputs/metrics/validation_best_threshold_summary.csv`
- `outputs/metrics/final_test_evaluation_from_valid_selection.csv`
- `outputs/metrics/validation_vs_day6_backtest_compare.csv`
- `outputs/predictions/validation_predictions.csv`
- `outputs/predictions/final_test_predictions_from_valid_selection.csv`
- `outputs/tables/validation_split_summary.csv`
- `data/interim/splits/train_inner_indices.csv`
- `data/interim/splits/valid_indices.csv`

## 下一步建议

下一轮建议进入缺失值和特征工程消融实验，但继续沿用 validation-based 流程：所有策略、模型和阈值选择都在 valid 上完成，official test 只用于最终评估。

# Enhancement 2 缺失值与特征工程消融实验总结

## 增强目标

本轮在 validation-based 流程下系统比较缺失值处理和基础特征工程策略，重点回答三个问题：

1. 缺失模式本身是否携带预测信号。
2. `drop_50_missing_median`、`drop_80_missing_median` 和 `median_all` 哪个更稳。
3. `xgb_native_missing`、低方差过滤、高相关过滤和 L1 特征选择是否值得进入后续主线。

所有模型、策略和阈值仍然只在 `valid` 上选择，official test 只用于最终评估。本轮没有修改 `data/raw/`，没有做 GridSearch、SHAP、公开 baseline 对比或风险分层重做。

## 实验范围

本轮比较的策略包括：

- `median_all`
- `drop_80_missing_median`
- `drop_50_missing_median`
- `median_with_indicator`
- `xgb_native_missing`
- `missing_indicator_only`
- `low_variance_filter`
- `high_correlation_filter`
- `l1_feature_selection`

模型控制在 `logistic_regression_balanced` 和 `xgboost_scale_pos_weight`，避免把本轮变成大规模模型堆叠或调参实验。

## valid 上的主要结果

按 valid total cost 选择，最低成本组合为：

```text
XGBoost + drop_50_missing_median + threshold 0.14
```

valid 结果：

- precision = 0.3403
- recall = 0.9800
- F2 = 0.7122
- FP = 380
- FN = 4
- total_cost = 5,800

这说明更激进地删除缺失率大于等于 50% 的字段，在 valid 上可以降低成本，但是否稳定还需要看 official test。

## official test 最终评估观察

official test 上的关键结果如下：

| 策略 | 模型 | valid best threshold | official test total cost | Recall | F2 | FP | FN |
|---|---|---:|---:|---:|---:|---:|---:|
| median_with_indicator | XGBoost | 0.10 | 10060 | 0.9760 | 0.7556 | 556 | 9 |
| drop_80_missing_median | XGBoost | 0.14 | 10190 | 0.9707 | 0.7801 | 469 | 11 |
| low_variance_filter | XGBoost | 0.12 | 10510 | 0.9707 | 0.7696 | 501 | 11 |
| drop_50_missing_median | XGBoost | 0.14 | 10820 | 0.9680 | 0.7740 | 482 | 12 |
| median_all | XGBoost | 0.16 | 10820 | 0.9653 | 0.7890 | 432 | 13 |
| xgb_native_missing | XGBoost | 0.18 | 11180 | 0.9600 | 0.8079 | 368 | 15 |
| high_correlation_filter | XGBoost | 0.13 | 12410 | 0.9600 | 0.7656 | 491 | 15 |
| l1_feature_selection | Logistic | 0.35 | 16780 | 0.9360 | 0.7535 | 478 | 24 |

注意：official test 结果只用于最终评估和稳定性观察，不能反过来作为策略选择依据。因此，虽然 `median_with_indicator` 在 official test 上观察到最低 total cost，但不能直接写成最终最优方案，只能说明缺失指示变量值得后续继续验证。

## 缺失模式是否有信息

`missing_indicator_only` 只使用“字段是否缺失”的 0/1 指示变量，不使用任何原始数值特征。

结果显示：

- XGBoost + `missing_indicator_only` 在 valid 上 average_precision = 0.4616，而 valid 正类基准率约为 0.0167。
- 在 official test 上 average_precision = 0.4713，而 test 正类基准率约为 0.0234。
- official test 上 recall = 0.8987，FN = 38，total cost = 27,570。

结论：缺失模式本身确实携带预测信号，但单独使用缺失指示变量会产生较多 FP，不能替代原始数值特征。更合理的方向是把缺失指示作为原始数值特征的补充。

## 策略判断

- `drop_80_missing_median`：test 表现更稳，是当前 validation 基准方案。
- `drop_50_missing_median`：valid 成本最低，但 test 上不如 drop_80 稳定，说明高缺失字段不能只凭缺失率机械删除。
- `median_all`：保留全部字段表现稳定，F2 较高，但 total cost 不最低。
- `median_with_indicator`：验证了缺失指示方向有价值，建议进入下一轮 validation 或轻量调参继续观察。
- `xgb_native_missing`：F2 和 precision 较好，但 FN 增加导致 total cost 不占优。
- `low_variance_filter`：只删除 `cd_000`，轻量可保留，但不是主导提升来源。
- `high_correlation_filter`：删除 25 个相关字段后成本变高，当前不建议作为主线。
- `l1_feature_selection`：对线性模型解释有辅助价值，但不是当前性能最优方向。

## 本轮输出文件

- `outputs/metrics/feature_ablation_valid_threshold_metrics.csv`
- `outputs/metrics/feature_ablation_valid_best_summary.csv`
- `outputs/metrics/feature_ablation_final_test_results.csv`
- `outputs/tables/feature_ablation_strategy_metadata.csv`
- `outputs/tables/missing_indicator_signal_summary.csv`
- `notebooks/09_feature_ablation_experiments.ipynb`

## 下一步建议

下一步可以进入轻量级调参或模型解释性分析。更推荐先做小范围 XGBoost 参数实验，并继续坚持：参数、策略和阈值只在 validation 上选择，official test 只做最终评估。如果进入模型解释，应使用特征重要性或 SHAP 解释匿名特征的相对贡献，但不能虚构传感器物理含义。

# Day 10 字段级分布诊断与结构信号分析准备

## Day 10 目标

Day 10 不建模、不调参、不做新的特征工程实验，只做字段级分布诊断。目标是系统观察 170 个匿名数值字段的缺失率、零值率、近似零值率、偏态、长尾、pos/neg 分布差异和 train/valid/test 分布漂移，为后续结构特征设计提供依据。

## 输出文件

本轮已生成以下诊断表：

- `outputs/metrics/day10_feature_distribution_summary.csv`
- `outputs/metrics/day10_missing_zero_summary.csv`
- `outputs/metrics/day10_pos_neg_distribution_diff.csv`
- `outputs/metrics/day10_train_valid_test_drift_summary.csv`
- `outputs/metrics/day10_top_feature_diagnostics.csv`

并生成以下图表：

- `outputs/figures/day10_top_skewed_features.png`
- `outputs/figures/day10_pos_neg_missing_diff_top20.png`
- `outputs/figures/day10_train_test_drift_top20.png`
- `outputs/figures/day10_zero_rate_top20.png`

## 高缺失现象

train_inner 中高缺失字段集中在：

| feature_name | missing_rate |
|---|---:|
| br_000 | 0.8216 |
| bq_000 | 0.8130 |
| bp_000 | 0.7968 |
| bo_000 | 0.7739 |
| ab_000 | 0.7715 |
| cr_000 | 0.7715 |
| bn_000 | 0.7354 |
| bm_000 | 0.6614 |

缺失率大于等于 50% 的字段有 8 个，缺失率大于等于 80% 的字段有 2 个。这说明缺失不是零散噪声，而是结构性数据问题。

## 高零值现象

train_inner 中高零值字段集中在：

| feature_name | zero_rate |
|---|---:|
| as_000 | 0.9889 |
| au_000 | 0.9883 |
| ag_000 | 0.9858 |
| ay_009 | 0.9800 |
| ay_000 | 0.9796 |
| ag_001 | 0.9767 |
| ay_001 | 0.9701 |
| ay_002 | 0.9696 |
| ay_003 | 0.9681 |
| az_009 | 0.9584 |

零值率大于等于 90% 的字段有 29 个，零值率大于等于 50% 的字段有 53 个。后续可以考虑样本级 zero-count、zero-rate，以及按字段前缀聚合的零值结构特征。

## 高偏态和长尾现象

train_inner 中偏态绝对值最高的字段包括：

| feature_name | skew | p99_to_median_ratio | max_to_p99_ratio |
|---|---:|---:|---:|
| cs_009 | 217.8466 | NaN | 7483832.29 |
| cf_000 | 190.0789 | 207.0000 | 20735023.93 |
| co_000 | 190.0789 | 694.0975 | 1545946.42 |
| ad_000 | 190.0789 | 32.6938 | 2083861.36 |
| dh_000 | 181.7330 | NaN | 11619.00 |

这些字段显示出明显右偏和极端长尾。该现象支持继续使用中位数填充、树模型，以及后续尝试稳健缩放或截尾对照实验。对线性模型而言，这类长尾字段需要谨慎处理。

## pos/neg 分布差异

pos/neg 缺失率差异最大的字段包括：

| feature_name | missing_rate_diff_abs |
|---|---:|
| br_000 | 0.7415 |
| bq_000 | 0.7365 |
| bp_000 | 0.7251 |
| bo_000 | 0.7069 |
| bn_000 | 0.6704 |

这与前面缺失模式存在预测信号的结论一致。高缺失字段不能只按缺失率机械删除，需要结合缺失指示、模型表现和成本结果评估。

pos/neg 数值分布差异明显的字段包括 `ah_000`、`bg_000`、`ci_000`、`bu_000`、`cq_000`、`bv_000`、`bb_000`、`an_000` 等。这些字段只能解释为匿名特征上的统计差异，不能虚构具体传感器或部件含义。

## train/test 分布漂移

train_inner 与 official test 的缺失率差异整体较小，最大缺失率差异约为 0.5 个百分点，Top 字段包括 `ec_00`、`cl_000`、`ed_000`、`bl_000`、`bk_000`。这说明缺失模式在 train/test 之间总体较稳定。

但部分长尾字段的 p99 差异较大，例如 `eb_000`、`du_000`、`bu_000`、`bv_000`、`cq_000`、`bb_000`。这提示后续结构特征或稳健处理要关注长尾泛化风险。

## 对后续结构特征设计的启发

Day 10 结果支持后续进入结构特征设计，但不应直接跳到复杂模型。建议 Day 11 / Day 12 优先考虑：

1. 样本级缺失计数、缺失率、零值计数、零值率。
2. 按匿名字段前缀构建组内缺失率、零值率和分位数统计。
3. 对高偏态字段尝试稳健变换或截尾对照。
4. 对 pos/neg 缺失差异明显字段保留 missing indicator 方向。
5. 对 train/test 漂移较明显字段保持谨慎，不能使用 official test 反向决定策略。

所有后续结构特征仍应在 validation 流程中选择，official test 只用于最终评估。

# Day 11 前缀组结构信号分析

## Day 11 目标

Day 11 基于 Day 10 的字段级分布诊断结果，按匿名字段前缀进行结构分组分析。前缀只作为匿名结构分组线索，不能解释为具体传感器或部件含义。本阶段不建模、不调参、不做新的结构特征实验，也不使用 official test 反向决定策略。

## 输出文件

本轮已生成以下结果表：

- `outputs/metrics/day11_prefix_group_summary.csv`
- `outputs/metrics/day11_prefix_group_signal_ranking.csv`
- `outputs/tables/day11_prefix_feature_members.csv`

并生成以下图表：

- `outputs/figures/day11_prefix_avg_missing_rate_top20.png`
- `outputs/figures/day11_prefix_avg_zero_rate_top20.png`
- `outputs/figures/day11_prefix_pos_neg_missing_diff_top20.png`
- `outputs/figures/day11_prefix_signal_score_top20.png`
- `outputs/figures/day11_prefix_drift_risk_top20.png`

## 前缀组数量

Day 11 共识别出 107 个字段前缀组。其中：

- 100 个前缀组只包含 1 个字段；
- 7 个前缀组包含 10 个字段，分别是 `ag`、`ay`、`az`、`ba`、`cn`、`cs`、`ee`。

这个结果很重要：大多数前缀实际上不是“组”，不适合做前缀聚合主线；真正适合 Day 12 设计组聚合特征的是少数多字段前缀。

## 高缺失前缀组

平均缺失率最高的前缀组主要是单字段前缀：

| prefix | feature_count | avg_missing_rate | max_missing_rate |
|---|---:|---:|---:|
| br | 1 | 0.8216 | 0.8216 |
| bq | 1 | 0.8130 | 0.8130 |
| bp | 1 | 0.7968 | 0.7968 |
| bo | 1 | 0.7739 | 0.7739 |
| cr | 1 | 0.7715 | 0.7715 |

这些字段缺失信号强，但因为都是单字段前缀，不适合作为前缀聚合主线。它们更适合在单字段缺失指示或稳健处理时观察。

## 高零值前缀组

平均零值率最高的前缀组也多为单字段前缀：

| prefix | feature_count | avg_zero_rate | max_zero_rate |
|---|---:|---:|---:|
| as | 1 | 0.9889 | 0.9889 |
| au | 1 | 0.9883 | 0.9883 |
| ef | 1 | 0.9505 | 0.9505 |
| dz | 1 | 0.9499 | 0.9499 |
| eg | 1 | 0.9468 | 0.9468 |

多字段前缀中，`ay` 平均零值率最高，为 0.6809；`ag` 平均零值率为 0.5117；`cn` 平均零值率为 0.3277。这些结果支持 Day 12 尝试组内 zero-count、zero-rate 和非零值统计。

## pos/neg 差异明显的前缀组

pos/neg 缺失率差异最高的前缀仍然集中在单字段高缺失字段：

- `br`
- `bq`
- `bp`
- `bo`
- `bn`

pos/neg 零值率差异较明显的单字段前缀包括 `ai`、`al`、`am`、`ar`、`df`。多字段前缀中，`ag` 和 `cn` 的平均 pos/neg 零值差异相对更明显，分别为 0.2266 和 0.2049。

## train/test drift 风险

drift 风险较高的前缀包括 `cl`、`du`、`ec`、`dq`、`ed`，多数是单字段前缀。多字段前缀整体 drift 风险处于中等水平：

| prefix | drift_risk_score | signal_score |
|---|---:|---:|
| ay | 0.5083 | 0.3207 |
| ee | 0.5020 | 0.1501 |
| az | 0.4959 | 0.2450 |
| cs | 0.4828 | 0.2067 |
| ag | 0.4826 | 0.3255 |
| cn | 0.4814 | 0.2653 |
| ba | 0.4784 | 0.1749 |

这说明前缀组结构特征可以尝试，但仍需在 validation 上验证泛化稳定性。

## Day 12 候选方向

建议进入 Day 12 的前缀组结构特征候选为：

1. `ag`：组内零值率较高，pos/neg 零值差异相对明显。
2. `ay`：组内平均零值率最高，偏态明显。
3. `cn`：零值率和 pos/neg 零值差异较明显。
4. `az`、`cs`：偏态较高，可作为长尾结构候选。
5. `ba`、`ee`：信号较弱，作为低优先级备选。

Day 12 可以围绕这些前缀设计组内缺失计数、零值计数、零值率、非零值分位数和组内长尾统计。但所有设计仍必须通过 train_inner / valid 流程评估，official test 只用于最终评估。

# Day 12 结构特征方案设计

## Day 12 目标

Day 12 只做结构特征方案设计，不训练模型、不调参、不做阈值分析、不做 SHAP、不生成 processed 特征矩阵。目标是把 Day 10 字段级分布诊断和 Day 11 前缀组结构信号分析整理成可执行的 Day 13 实验方案。

## 新增交付物

本轮新增：

- `docs/structural_feature_design.md`
- `config/structural_features.yaml`
- `scripts/10_build_structural_feature_design.py`
- `notebooks/12_structural_feature_design.ipynb`
- `outputs/tables/day12_structural_feature_design_table.csv`

设计表共 64 行，其中 60 行进入 Day 13 第一轮，4 行异常/长尾统计作为第二轮备选。高优先级设计行数为 48 行。

## 设计的结构特征家族

Day 12 设计了 6 类结构特征家族：

1. 样本级缺失统计：
   - `sample_missing_count`
   - `sample_missing_rate`
   - `sample_non_missing_count`

2. 样本级零值统计：
   - `sample_zero_count`
   - `sample_zero_rate`
   - `sample_non_zero_count`

3. 前缀组缺失聚合：
   - `prefix_ag_missing_count`
   - `prefix_ag_missing_rate`
   - `prefix_ay_missing_count`
   - `prefix_ay_missing_rate`
   - 其他候选前缀类似。

4. 前缀组零值聚合：
   - `prefix_ag_zero_count`
   - `prefix_ag_zero_rate`
   - `prefix_ay_zero_count`
   - `prefix_ay_zero_rate`
   - `prefix_cn_zero_count`
   - `prefix_cn_zero_rate`

5. 筛选后的 missing indicators：
   - 候选字段只基于 train_inner 的缺失率和 pos/neg 缺失率差异筛选。
   - 当前阈值为 `missing_rate >= 0.01` 且 `abs(pos_missing_rate - neg_missing_rate) >= 0.10`。
   - 当前最多选择 30 个字段。
   - Top 候选包括 `br_000`、`bq_000`、`bp_000`、`bo_000`、`bn_000`、`bm_000`、`di_000`、`dh_000`、`dj_000`、`dk_000`。

6. 可选异常 / 长尾统计：
   - `sample_outlier_count_p99`
   - `sample_outlier_rate_p99`
   - `prefix_az_outlier_count`
   - `prefix_cs_outlier_count`
   - 暂不进入 Day 13 第一轮。

## Day 13 第一轮实验矩阵建议

第一轮建议只做以下受控对照：

- `median_all`
- `median_all_sample_missing`
- `median_all_sample_zero`
- `median_all_prefix_missing`
- `median_all_prefix_zero`
- `median_all_selected_missing_indicators`
- `median_all_structural_all`

这些实验的目标不是堆模型，而是验证结构信号是否能在 validation-based 流程下改善 recall、F2、PR-AUC 和 total cost。

## 暂时不做的内容

Day 13 第一轮暂不做：

- PCA
- SVM
- 大规模 GridSearch
- SHAP
- official test 反向筛选
- 长尾 outlier 特征作为主线
- 任何基于 test 结果的特征保留决策

## 必须遵守的边界

所有规则都必须只在 `train_inner` 上 fit，包括：

- 数值字段列表；
- prefix membership；
- selected missing indicators；
- outlier 分位数阈值；
- 任何字段筛选规则。

`valid` 用于选择结构特征方案和阈值，`official test` 只用于最终评估。字段匿名，不能解释具体物理含义。

# Day 13 结构特征第一轮 valid 实验

## 本轮目标

Day 13 在 Day 12 结构特征设计的基础上，开始做第一轮结构特征实验。本轮严格只使用 official training set 内部划分出的 `train_inner / valid`，不使用 official test 做评估或反向选择。

本轮只训练 XGBoost，不做 GridSearch、不做 SHAP、不做 PCA、不加入 SVM，也不解释匿名字段的真实物理含义。

## 实验组

本轮没有把 Day 12 的 60 个结构特征一次性作为主结论，而是按结构信号来源拆成 6 个实验组：

| experiment_group | 结构特征数 | 说明 |
|---|---:|---|
| baseline_median_all | 0 | 原始数值特征 median_all，不加结构特征 |
| median_all_sample_missing_rate | 1 | 增加样本级缺失率 |
| median_all_selected_missing_indicators_top30 | 30 | 增加 train_inner 上筛选出的 Top 30 missing indicators |
| median_all_prefix_zero_rate | 5 | 增加 ag、ay、cn、az、cs 前缀组零值率 |
| median_all_structural_core | 36 | sample_missing_rate + Top 30 missing indicators + prefix zero rate |
| median_all_structural_all | 60 | Day 12 第一轮全部结构特征，仅作为上限观察 |

## valid 结果

| experiment_group | best_threshold | Precision | Recall | F2 | PR-AUC | FP | FN | Total Cost |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| median_all_structural_all | 0.18 | 0.3679 | 0.9750 | 0.7331 | 0.8635 | 335 | 5 | 5850 |
| median_all_selected_missing_indicators_top30 | 0.30 | 0.4308 | 0.9650 | 0.7732 | 0.8604 | 255 | 7 | 6050 |
| median_all_prefix_zero_rate | 0.09 | 0.2936 | 0.9850 | 0.6696 | 0.8625 | 474 | 3 | 6240 |
| median_all_sample_missing_rate | 0.15 | 0.3421 | 0.9750 | 0.7117 | 0.8660 | 375 | 5 | 6250 |
| baseline_median_all | 0.16 | 0.3593 | 0.9700 | 0.7239 | 0.8672 | 346 | 6 | 6460 |
| median_all_structural_core | 0.16 | 0.3540 | 0.9700 | 0.7196 | 0.8706 | 354 | 6 | 6540 |

## 关键观察

1. `median_all_structural_all` 在 valid 上 total cost 最低，为 5850，但它包含 60 个结构特征，只能作为上限观察，不能直接作为最终主结论。
2. `median_all_selected_missing_indicators_top30` 是更窄、更可解释的候选方案，valid total cost 从 baseline 的 6460 降到 6050，主要通过减少 FP 获得成本下降，但 FN 从 6 增加到 7。
3. `median_all_prefix_zero_rate` 的 FN 最低，为 3，recall 达到 0.9850，说明前缀组零值率可能包含结构信号；但 FP 增加到 474，precision 明显下降。
4. `median_all_sample_missing_rate` 相比 baseline 降低了 valid total cost，并把 FN 从 6 降到 5，说明样本整体缺失程度存在一定信号。
5. `median_all_structural_core` 没有接近 `structural_all`，且略差于 baseline，说明简单叠加核心结构特征可能引入冗余或噪声，需要 Day 14 谨慎观察。

## Day 14 建议

Day 14 建议只选择 1-2 个 valid 候选方案进入 official test 最终观察：

1. `median_all_structural_all`：valid 成本最低，但作为结构特征上限方案观察泛化风险；
2. `median_all_selected_missing_indicators_top30`：结构更窄、成本较低，适合作为更稳健的候选方案。

如果 Day 14 需要额外观察漏报控制，可以把 `median_all_prefix_zero_rate` 作为补充方案，但不建议把它作为主方案，因为 FP 较高。

# Day 14 结构特征候选方案 official test 最终观察

## 本轮目标

Day 14 只对 Day 13 valid 选出的少数候选方案做 official test 最终观察。本轮不在 test 上重新选择策略、结构特征或阈值，也不根据 test 结果反向修改 Day 13 的选择逻辑。

所有 imputer 和结构特征规则仍然只在 train_inner 上 fit，official test 只做 transform 和最终观察。

## 固定候选方案

本轮评估 4 个候选方案：

| candidate_group | valid threshold | 说明 |
|---|---:|---|
| baseline_median_all | 0.16 | 不加结构特征，用作对照 |
| median_all_selected_missing_indicators_top30 | 0.30 | 更窄的 selected missing indicators 候选 |
| median_all_prefix_zero_rate | 0.09 | 验证前缀组零值率是否泛化 |
| median_all_structural_all | 0.18 | valid 成本最低的上限观察方案 |

## official test 结果

| candidate_group | threshold | Precision | Recall | F2 | AP | FP | FN | Total Cost |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| median_all_structural_all | 0.18 | 0.4770 | 0.9680 | 0.8027 | 0.9055 | 398 | 12 | 9980 |
| baseline_median_all | 0.16 | 0.4559 | 0.9653 | 0.7890 | 0.9086 | 432 | 13 | 10820 |
| median_all_prefix_zero_rate | 0.09 | 0.3846 | 0.9733 | 0.7452 | 0.9093 | 584 | 10 | 10840 |
| median_all_selected_missing_indicators_top30 | 0.30 | 0.5457 | 0.9387 | 0.8205 | 0.9085 | 293 | 23 | 14430 |

## 泛化观察

1. `median_all_structural_all` 在 official test 上 total cost 最低，为 9980，相比 baseline 的 10820 有一定下降；但它包含 60 个结构特征，仍然只能作为上限观察，不能直接写成最终主方案。
2. `median_all_prefix_zero_rate` 在 test 上 FN 最低，为 10，recall 最高，为 0.9733；但 FP 增加到 584，导致 total cost 与 baseline 基本持平，说明前缀零值结构有召回信号，但误报代价较高。
3. `median_all_selected_missing_indicators_top30` 在 valid 上表现较好，但 official test 上 FN 增加到 23，total cost 升到 14430，说明该方案泛化不足，不适合作为当前主候选。
4. baseline_median_all 在 test 上仍然稳定，说明结构特征必须经过进一步筛选或正则化，不能只因为 valid 有提升就直接扩大特征集。

## 下一步建议

下一步不建议马上做大规模调参。更合理的方向是：

1. 拆解 `structural_all` 中哪些结构特征真正贡献泛化收益；
2. 对 prefix zero rate 和 sample_missing_rate 做更小规模组合；
3. 保留 selected missing indicators 方向，但降低 Top 30 的数量，例如 Top 5 / Top 10 / Top 20；
4. 在结构特征筛选稳定后，再做轻量 XGBoost 调参或模型解释性分析。


## Day 15：Controlled XGBoost Tuning

Day 15 进入受控 XGBoost 调参阶段。本轮固定少数候选特征方案，只使用 official train 内部划分出的 `train_inner / valid`，不使用 official test 做参数、特征方案或阈值选择。调参目标以 valid total cost 为主，辅助观察 FN、recall、F2 和 PR-AUC。

配置文件中保留了完整计划：每个候选策略 `broad=100`、`refined=50`。考虑本地交互运行耗时，本次实际运行使用环境变量覆盖为每个策略 `broad=20`、`refined=8`，共 3 个候选策略、84 个 trial。脚本仍支持后续离线跑满配置规模。

本轮候选策略包括：

| candidate_strategy | 说明 |
|---|---|
| baseline_median_all | 原始匿名数值特征 + median imputation |
| median_all_structural_all | 原始匿名数值特征 + Day13 structural_all 结构特征 |
| drop_high_missing_median | 删除极高缺失字段后 median imputation |

valid 上的最佳结果如下：

| candidate_strategy | stage | threshold | Precision | Recall | F2 | AP | FP | FN | Total Cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| median_all_structural_all | broad | 0.31 | 0.4422 | 0.9750 | 0.7857 | 0.8745 | 246 | 5 | 4960 |
| drop_high_missing_median | broad | 0.19 | 0.3874 | 0.9800 | 0.7504 | 0.8649 | 310 | 4 | 5100 |
| baseline_median_all | refined | 0.13 | 0.4080 | 0.9750 | 0.7629 | 0.8887 | 283 | 5 | 5330 |

broad / refined 对比：

- `baseline_median_all`：refined 从 broad 最优 5370 小幅降到 5330，收益有限。
- `median_all_structural_all`：最优 trial 来自 broad，refined 最优成本为 5770，未超过 broad。
- `drop_high_missing_median`：最优 trial 来自 broad，refined 最优成本为 5310，未超过 broad。

调参相对 Day13 未调参 valid 结果有一定改善：`median_all_structural_all` 从 5850 降到 4960，`baseline_median_all` 从 6460 降到 5330。但本轮仍然只是 valid 阶段结果，不能写成最终模型。Day16 建议只选择 1-2 个 tuned 候选做 official test 观察：优先 `median_all_structural_all` 作为上限观察，同时保留 `drop_high_missing_median` 作为更轻量、较稳的缺失策略候选；`baseline_median_all` 可作为对照。

## Day 16：Tuned XGBoost Official Test Evaluation

Day 16 只对 Day 15 在 valid 上选出的 tuned XGBoost 候选方案做 official test 最终观察。本轮固定 Day15 的参数和 threshold，不在 official test 上重新搜索、不重新调阈值，也不根据 test 结果反向修改 Day15。

评估的 tuned candidates：

| candidate_strategy | Day15 threshold | Day15 best trial | Day15 stage |
|---|---:|---|---|
| median_all_structural_all | 0.31 | median_all_structural_all_broad_009 | broad |
| drop_high_missing_median | 0.19 | drop_high_missing_median_broad_007 | broad |
| baseline_median_all | 0.13 | baseline_median_all_refined_002 | refined |

official test 结果如下：

| candidate_strategy | threshold | Precision | Recall | F2 | AP | FP | FN | Total Cost |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| drop_high_missing_median | 0.19 | 0.4891 | 0.9600 | 0.8050 | 0.9121 | 376 | 15 | 11260 |
| baseline_median_all | 0.13 | 0.5129 | 0.9573 | 0.8159 | 0.9218 | 341 | 16 | 11410 |
| median_all_structural_all | 0.31 | 0.5538 | 0.9467 | 0.8291 | 0.9133 | 286 | 20 | 12860 |

valid 到 official test 的变化：

| candidate_strategy | valid cost | test cost | cost delta | valid FN | test FN |
|---|---:|---:|---:|---:|---:|
| drop_high_missing_median | 5100 | 11260 | +6160 | 4 | 15 |
| baseline_median_all | 5330 | 11410 | +6080 | 5 | 16 |
| median_all_structural_all | 4960 | 12860 | +7900 | 5 | 20 |

结论：

1. Day15 tuned 方案在 valid 上成本较低，但 official test 上没有稳定泛化到同等成本水平。
2. tuned `drop_high_missing_median` 是 Day16 test 成本最低的 tuned 方案，total cost 为 11260，但仍高于 Day14 未调参 `median_all_structural_all` 的 9980。
3. tuned `median_all_structural_all` 在 valid 上最优，但 test 上 FN 增加到 20，total cost 上升到 12860，说明该 tuned 参数组合存在明显泛化落差。
4. 调参并没有带来比 Day14 未调参结构特征方案更好的 official test 成本，因此不建议继续扩大 XGBoost 随机搜索。
5. 下一步更适合转向 SQL 业务深化、模型解释性分析和 README / 项目报告最终整理，而不是继续追逐参数。

## Day 17：OOF 阈值稳定性与 Bin Projection 实验

Day 17 的动机来自 Day 15/16：单一 `train_inner / valid` split 上调出的 XGBoost 参数和阈值在 official test 上没有稳定泛化。因此本轮不再扩大调参，而是只使用 official train 内部的 OOF 预测来做阈值选择，并加入 Recall/FN floor 业务约束，同时验证匿名 histogram/bin-like 前缀组投影特征是否提供额外信号。

本轮配置文件保留默认 `5 folds x 2 repeats`，但为了控制本地交互运行时间，实际运行使用了配置允许的运行时降级：`5 folds x 1 repeat`。本轮没有使用 official test，没有重新调参，没有修改 `data/raw/`。

参与 OOF 实验的候选策略包括：

| candidate_strategy | 说明 |
|---|---|
| baseline_median_all | 原始匿名数值特征 + median imputation |
| median_all_structural_all | 原始特征 + Day13 structural_all 结构特征 |
| median_all_bin_projection | 原始特征 + 匿名 bin projection 特征 |
| median_all_structural_all_plus_bin_projection | 原始特征 + structural_all + bin projection |

OOF `cost_min` 规则下的结果如下：

| candidate_strategy | threshold | Precision | Recall | F2 | AP | FP | FN | Total Cost |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| median_all_structural_all_plus_bin_projection | 0.11 | 0.3285 | 0.9610 | 0.6939 | 0.8703 | 1964 | 39 | 39140 |
| median_all_structural_all | 0.09 | 0.3013 | 0.9660 | 0.6703 | 0.8711 | 2240 | 34 | 39400 |
| baseline_median_all | 0.12 | 0.3307 | 0.9590 | 0.6949 | 0.8691 | 1941 | 41 | 39910 |
| median_all_bin_projection | 0.10 | 0.3184 | 0.9600 | 0.6842 | 0.8701 | 2055 | 40 | 40550 |

关键观察：

1. `median_all_structural_all_plus_bin_projection` 在 OOF `cost_min` 下成本最低，相比 `median_all_structural_all` 只小幅下降 260，说明 bin projection 有轻微信号，但当前不是压倒性提升。
2. 单独 `median_all_bin_projection` 没有优于 baseline，说明 bin projection 更像结构补充信号，而不是可单独替代原始特征或 structural_all 的主线方案。
3. Recall/FN floor 可以降低 FN 或提高 recall，但代价是 FP 明显上升，total cost 大幅增加。例如 `recall_floor_975` 下 `median_all_structural_all` 选择 threshold=0.03，FN=25，recall=0.9750，但 total cost 上升到 50090。
4. `fn_floor_20` / `recall_floor_980` 并非所有策略都能满足。对 `median_all_structural_all_plus_bin_projection` 来说，相关强约束在本次 OOF 结果中没有可行阈值满足，因此结果表中 `constraint_satisfied=False`，不能误读为满足了约束。
5. OOF 阈值选择比单一 valid split 更稳健，但 Day17 结果仍然只来自 official train 内部，不是 official test 结论。

Day18 建议只选择少数候选做 official test 最终观察：

- `median_all_structural_all_plus_bin_projection` + `cost_min` threshold=0.11：用于观察 structural_all + bin projection 的 OOF 最低成本组合是否泛化。
- `median_all_structural_all` + `recall_floor_975` threshold=0.03：用于观察显式高 recall 业务约束在 official test 上的代价。

如果 Day18 仍然没有稳定改善，应停止继续追逐模型和阈值，转向 histogram/bin 结构深化、模型解释性分析、SQL 业务深化和最终 README / 报告收尾。
