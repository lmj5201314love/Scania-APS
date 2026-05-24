# outputs 产物说明与阅读索引

本文件用于解释 `outputs/` 目录下各类运行产物的来源、作用和主要结论。  
这些文件是本地分析结果，通常不应强行提交到 GitHub；正式展示时优先引用 `README.md`、`reports/project_report.md` 和 `reports/summary.md`。

## 阅读顺序建议

如果只是快速看项目结果，建议按下面顺序阅读：

1. `outputs/metrics/day14_structural_feature_test_results.csv`
2. `outputs/metrics/feature_ablation_final_test_results.csv`
3. `outputs/metrics/final_test_evaluation_from_valid_selection.csv`
4. `outputs/tables/day7_business_result_summary.csv`
5. `outputs/tables/day7_risk_level_summary.csv`

如果要追溯完整项目过程，再依次查看 Day 2 数据质量、Day 6 阈值分析、Day 10/11/12/13 结构特征分析相关文件。

## 目录说明

| 子目录 | 作用 |
|---|---|
| `outputs/tables/` | 数据质量分析、业务汇总、风险分层、结构特征设计等表格产物 |
| `outputs/metrics/` | 模型指标、阈值分析、valid/test 对比、结构特征实验结果 |
| `outputs/predictions/` | 模型预测概率、预测标签、样本级预测明细 |
| `outputs/figures/` | 缺失值、阈值曲线、字段分布、前缀组分析等图表 |

## 关键结论速查

### 成本设定

项目使用成本敏感评估：

- FP，误报成本：`10`
- FN，漏报成本：`500`

因此不能只看 accuracy，而要重点看 recall、F2、PR-AUC、FN 和 total cost。

### 当前最重要结果

Day 14 对 Day 13 valid 选出的结构特征候选方案做了 official test 最终观察：

| 方案 | 阈值来源 | Precision | Recall | F2 | AP | FP | FN | Total Cost | 结论 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `median_all_structural_all` | Day 13 valid | 0.4770 | 0.9680 | 0.8027 | 0.9055 | 398 | 12 | 9980 | official test 成本最低，但包含 60 个结构特征，只能作为上限观察 |
| `baseline_median_all` | Day 13 valid | 0.4559 | 0.9653 | 0.7890 | 0.9086 | 432 | 13 | 10820 | 稳定基线 |
| `median_all_prefix_zero_rate` | Day 13 valid | 0.3846 | 0.9733 | 0.7452 | 0.9093 | 584 | 10 | 10840 | FN 最低，但 FP 明显升高 |
| `median_all_selected_missing_indicators_top30` | Day 13 valid | 0.5457 | 0.9387 | 0.8205 | 0.9085 | 293 | 23 | 14430 | valid 表现较好，但 test 泛化不足 |

当前建议：不要直接把 `structural_all` 写成最终主方案。下一步更适合拆解结构特征贡献，筛出更稳、更少的结构特征组合。

## tables 文件说明

### Day 2 数据质量与缺失值分析

| 文件 | 作用 | 主要结论 |
|---|---|---|
| `dataset_overview.csv` | train/test 行列数、特征数、标签列检查 | train/test 使用官方划分，不重新合并切分 |
| `label_distribution.csv` | `pos` / `neg` 标签分布 | 类别极不平衡，不能以 accuracy 为核心 |
| `column_type_summary.csv` | 字段类型统计 | 除标签外主要是数值型匿名特征 |
| `missing_summary_train.csv` | train 每列缺失数量和缺失率 | 识别字段级缺失严重程度 |
| `missing_summary_test.csv` | test 每列缺失数量和缺失率 | 用于和 train 缺失模式对比 |
| `missing_level_summary.csv` | 按缺失率区间统计字段数量 | 高缺失字段需要识别，但 Day 2 不直接删除 |
| `high_missing_features.csv` | 缺失率较高字段清单 | `br_000`、`bq_000`、`bp_000`、`bo_000` 等值得重点关注 |
| `train_test_missing_compare.csv` | train/test 缺失率差异 | 整体缺失模式接近，部分字段有差异 |
| `class_missing_compare.csv` | pos/neg 缺失率差异 | pos/neg 缺失模式差异明显，说明缺失模式可能有预测信号 |
| `duplicate_summary.csv` | 重复行检查 | 用于基础数据质量复核 |

### SQL 支撑表

| 文件 | 作用 |
|---|---|
| `sql_support/dataset_overview_for_mysql.csv` | 可导入 MySQL 的数据集概览表 |
| `sql_support/label_distribution_for_mysql.csv` | 可导入 MySQL 的标签分布表 |
| `sql_support/feature_missing_summary_for_mysql.csv` | 可导入 MySQL 的字段缺失汇总表 |

这些文件用于 Day 3 SQL 复核，不是建模输入。

### Day 7 风险分层和业务结果

| 文件 | 作用 | 主要结论 |
|---|---|---|
| `day7_maintenance_priority_list.csv` | 样本级维修优先级清单 | 包含预测概率、风险等级、建议动作 |
| `day7_risk_level_summary.csv` | 风险等级汇总 | Critical / High / Medium / Low 分层可支持维修排序 |
| `day7_business_result_summary.csv` | 业务成本汇总 | 测试集回溯方案 total cost 为 8640，相比 naive baseline 下降 95.39% |

注意：Day 7 阈值来自 test 回溯敏感性分析，不是生产最终阈值。

### Validation 和结构特征相关表

| 文件 | 作用 | 主要结论 |
|---|---|---|
| `validation_split_summary.csv` | train_inner / valid 划分概览 | 用于保证 valid-based 选择流程可复现 |
| `feature_ablation_strategy_metadata.csv` | 缺失值和特征工程消融实验元数据 | 记录每种策略的特征数量、删列数量和处理方式 |
| `missing_indicator_signal_summary.csv` | 缺失指示变量信号汇总 | 缺失模式本身有预测信号，但不能单独替代原始数值 |
| `day11_prefix_feature_members.csv` | 前缀组和字段明细 | 多字段前缀主要是 `ag`、`ay`、`az`、`ba`、`cn`、`cs`、`ee` |
| `day12_structural_feature_design_table.csv` | 结构特征设计表 | 设计样本级缺失/零值、前缀聚合、selected missing indicators 等特征家族 |
| `day13_selected_missing_indicator_columns.csv` | Day 13 train_inner 上选出的 Top 30 missing indicator 字段 | Top 字段包括 `br_000`、`bq_000`、`bp_000`、`bo_000`、`bn_000` 等 |
| `day13_structural_feature_experiment_metadata.csv` | Day 13 valid 实验元数据 | 记录每个结构特征组的原始特征数、结构特征数和特征名 |
| `day13_structural_feature_names_by_group.csv` | Day 13 每个实验组包含的结构特征明细 | 方便拆解 structural_all |
| `day14_structural_feature_test_metadata.csv` | Day 14 official test 观察元数据 | 记录 test 观察时每个候选组的特征数量和阈值来源 |

## metrics 文件说明

### Day 4 / Day 5 建模基线

| 文件 | 作用 | 主要结论 |
|---|---|---|
| `day4_baseline_metrics.csv` | Dummy / Logistic baseline 指标 | Logistic + `drop_high_missing_median` 默认阈值下 total cost 为 17180，明显优于 Dummy |
| `day5_model_compare_metrics.csv` | Random Forest / XGBoost 默认阈值对比 | XGBoost 默认阈值下 F2 / PR-AUC 较强，但默认阈值成本仍有优化空间 |

### Day 6 阈值成本分析

| 文件 | 作用 | 主要结论 |
|---|---|---|
| `day6_threshold_metrics.csv` | 每个模型/策略在不同阈值下的完整指标 | 用于画 threshold-cost / precision-recall / F2 曲线 |
| `day6_best_threshold_summary.csv` | 每个模型/策略的低成本阈值汇总 | test 回溯下 `XGBoost + median_all + threshold 0.20` total cost 为 8640 |

注意：Day 6 是 test 回溯敏感性分析，不能当成严谨生产阈值选择。

### Validation-based model selection

| 文件 | 作用 | 主要结论 |
|---|---|---|
| `validation_threshold_metrics.csv` | train_inner 训练、valid 阈值网格结果 | 只在 valid 上选择模型/策略/阈值 |
| `validation_best_threshold_summary.csv` | valid 上每个模型/策略的最佳阈值 | 用于选择进入 official test 的组合 |
| `final_test_evaluation_from_valid_selection.csv` | valid 选择后在 official test 上评估一次 | `XGBoost + drop_high_missing_median + threshold 0.14` test total cost 为 10190 |
| `validation_vs_day6_backtest_compare.csv` | valid 选择结果 vs Day 6 test 回溯最优 | test 回溯最优存在一定乐观偏差 |

### Missing value & feature engineering ablation

| 文件 | 作用 | 主要结论 |
|---|---|---|
| `feature_ablation_valid_threshold_metrics.csv` | 各缺失/特征工程策略在 valid 上的阈值网格 | 用于 valid-only 策略选择 |
| `feature_ablation_valid_best_summary.csv` | 各策略 valid 最优阈值汇总 | 用于观察哪些策略值得进入 test 评估 |
| `feature_ablation_final_test_results.csv` | valid 选择后在 official test 上的结果 | `median_with_indicator` test total cost 为 10060，说明缺失指示方向值得继续观察 |

### Day 10 字段级分布诊断

| 文件 | 作用 | 主要结论 |
|---|---|---|
| `day10_feature_distribution_summary.csv` | 字段级缺失、零值、分位数、偏态、长尾统计 | 高偏态/长尾明显，支持中位数填充和树模型 |
| `day10_missing_zero_summary.csv` | 缺失率、零值率、近零值率汇总 | 高零值字段很多，支持后续 zero-rate 结构特征 |
| `day10_pos_neg_distribution_diff.csv` | pos/neg 缺失、零值、分位数差异 | pos/neg 缺失差异明显，支持 missing indicator 方向 |
| `day10_train_valid_test_drift_summary.csv` | train_inner/valid/test 分布漂移观察 | 缺失率漂移整体不明显，部分长尾字段 p99 差异较大 |
| `day10_top_feature_diagnostics.csv` | Top 高缺失、高零值、高偏态、pos/neg 差异、drift 字段 | 用于快速定位重点字段 |

### Day 11 前缀组结构信号分析

| 文件 | 作用 | 主要结论 |
|---|---|---|
| `day11_prefix_group_summary.csv` | 前缀组聚合统计 | 107 个前缀组，其中多字段组主要为 `ag`、`ay`、`az`、`ba`、`cn`、`cs`、`ee` |
| `day11_prefix_group_signal_ranking.csv` | 前缀组结构信号排序 | `ag`、`ay`、`cn`、`az`、`cs` 是结构特征候选重点 |

### Day 13 / Day 14 结构特征实验

| 文件 | 作用 | 主要结论 |
|---|---|---|
| `day13_structural_feature_valid_threshold_metrics.csv` | Day 13 结构特征组在 valid 上的完整阈值网格 | 只用于 valid 阶段选择，不看 official test |
| `day13_structural_feature_valid_best_summary.csv` | Day 13 每个结构特征组的 valid 最佳阈值 | `structural_all` valid total cost 最低，为 5850；但只是上限观察 |
| `day14_structural_feature_test_results.csv` | Day 14 固定候选方案在 official test 上的最终观察 | `structural_all` test total cost 为 9980，但不能直接当最终主方案 |
| `day14_structural_feature_valid_test_compare.csv` | Day 13 valid 结果与 Day 14 test 结果对比 | `selected_missing_indicators_top30` valid 较好，但 test 上 FN 增加，泛化不足 |

## predictions 文件说明

| 文件 | 作用 | 使用场景 |
|---|---|---|
| `day4_baseline_predictions.csv` | Day 4 Dummy / Logistic baseline 预测明细 | 追溯 baseline 预测概率和标签 |
| `day5_model_compare_predictions.csv` | Day 5 RF / XGBoost 预测明细 | Day 6 阈值分析的数据来源 |
| `validation_predictions.csv` | validation-based 流程中 valid 预测明细 | 检查 valid 阈值选择输入 |
| `final_test_predictions_from_valid_selection.csv` | valid 选择后 official test 预测明细 | 检查严谨流程下的 test 预测 |
| `day14_structural_feature_test_predictions.csv` | Day 14 结构特征候选方案 official test 预测明细 | 后续可用于风险分层或 SQL 导入观察，但不能反向选阈值 |

预测明细通常包含：

- `dataset`
- `sample_id`
- `y_true`
- `y_proba`
- `y_pred`
- `model_name`
- `strategy`
- `threshold`

## figures 文件说明

### Day 2 缺失值图表

| 文件 | 作用 |
|---|---|
| `day2_label_distribution.png` | train 标签分布柱状图 |
| `day2_missing_rate_top30_train.png` | train 缺失率 Top 30 字段 |
| `day2_train_test_missing_diff_top30.png` | train/test 缺失率差异 Top 30 |
| `day2_class_missing_diff_top30.png` | pos/neg 缺失率差异 Top 30 |

### Day 6 阈值图表

| 文件 | 作用 |
|---|---|
| `day6_threshold_cost_curve.png` | threshold vs total cost |
| `day6_threshold_precision_recall_curve.png` | threshold vs precision / recall |
| `day6_threshold_f2_curve.png` | threshold vs F2 |

### Day 10 字段级诊断图表

| 文件 | 作用 |
|---|---|
| `day10_top_skewed_features.png` | 高偏态字段 Top 图 |
| `day10_zero_rate_top20.png` | 高零值率字段 Top 图 |
| `day10_pos_neg_missing_diff_top20.png` | pos/neg 缺失率差异 Top 图 |
| `day10_train_test_drift_top20.png` | train/test 分布漂移 Top 图 |

### Day 11 前缀组图表

| 文件 | 作用 |
|---|---|
| `day11_prefix_avg_missing_rate_top20.png` | 平均缺失率最高的前缀组 |
| `day11_prefix_avg_zero_rate_top20.png` | 平均零值率最高的前缀组 |
| `day11_prefix_pos_neg_missing_diff_top20.png` | pos/neg 缺失差异最大的前缀组 |
| `day11_prefix_signal_score_top20.png` | prefix signal score 排名 |
| `day11_prefix_drift_risk_top20.png` | drift risk score 排名 |

## 如何维护这个文件

后续如果新增 Day 15 或其他增强实验，请同步更新：

1. 新增输出文件路径；
2. 文件用途；
3. 是否用于 valid 选择或 official test 观察；
4. 关键结论；
5. 是否存在不能过度解释的限制。

项目里的核心边界仍然是：

- 不修改 `data/raw/`；
- 不用 official test 反向选择策略、阈值或特征；
- 不把 test 回溯结果写成生产最终结论；
- 匿名字段和前缀不能解释为真实物理含义。

## Day 15：Controlled XGBoost Tuning 输出说明

Day15 是受控 XGBoost 调参阶段，只使用 official train 内部划分出的 `train_inner / valid`，不使用 official test 做参数、特征方案或阈值选择。本轮输出只能解释为 valid 阶段调参结果，不能写成 official test 结果或生产最终模型。

### Day15 metrics 文件

| 文件 | 作用 | 主要说明 |
|---|---|---|
| `outputs/metrics/day15_xgb_tuning_valid_trial_results.csv` | 每个 XGBoost trial 在 valid 上的最佳阈值结果 | 一行对应一个 trial，用于比较不同参数组合的 valid total cost |
| `outputs/metrics/day15_xgb_tuning_valid_best_summary.csv` | 每个候选策略的 valid 最优 trial 摘要 | 用于决定 Day16 official test 观察候选 |
| `outputs/metrics/day15_xgb_tuning_valid_threshold_metrics.csv` | 所有 trial 的完整 threshold grid 结果 | 可复查每个 trial 在不同阈值下的 precision、recall、F2、FP、FN 和 total cost |
| `outputs/metrics/day15_xgb_tuning_refinement_summary.csv` | broad 与 refined 阶段对比 | 用于判断 refined 阶段是否相比 broad 阶段带来收益 |

### Day15 tables 文件

| 文件 | 作用 | 主要说明 |
|---|---|---|
| `outputs/tables/day15_xgb_tuning_candidate_metadata.csv` | 候选策略元数据 | 记录候选策略、原始特征数、结构特征数、删除字段数、实际运行 trial 数 |
| `outputs/tables/day15_xgb_tuning_search_space.csv` | 搜索空间展开表 | 记录 broad/refined 阶段每个参数的搜索范围，便于复盘 |
| `outputs/tables/day15_xgb_tuning_top_trials_by_strategy.csv` | 每个策略 broad 阶段 Top trials | refined search space 基于这些 valid 表现较好的 trial 构造 |

### Day15 predictions 文件

| 文件 | 作用 | 主要说明 |
|---|---|---|
| `outputs/predictions/day15_xgb_tuning_valid_best_predictions.csv` | 每个候选策略 valid best trial 的 valid 预测明细 | 包含 valid 上的 `y_true`、`y_proba`、`y_pred`、阈值和 trial id；不包含 official test 结果 |

### Day15 figures 文件

| 文件 | 作用 |
|---|---|
| `outputs/figures/day15_xgb_tuning_valid_cost_top20.png` | valid total cost 最低的 Top 20 trials |
| `outputs/figures/day15_xgb_tuning_strategy_cost_compare.png` | 各候选策略 valid 最优 total cost 对比 |
| `outputs/figures/day15_xgb_tuning_broad_vs_refined.png` | broad 与 refined 阶段最优 valid total cost 对比 |

### Day15 当前实际运行结果

配置文件中保留完整计划：每个候选策略 `broad=100`、`refined=50`。考虑本地交互运行耗时，本次实际运行使用环境变量覆盖为每个候选策略 `broad=20`、`refined=8`，共 3 个候选策略、84 个 trial。后续如果要更充分复盘，可以按 `config/config.yaml` 跑满规模。

valid 上当前最佳结果：

| candidate_strategy | stage | threshold | Precision | Recall | F2 | AP | FP | FN | Total Cost |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `median_all_structural_all` | broad | 0.31 | 0.4422 | 0.9750 | 0.7857 | 0.8745 | 246 | 5 | 4960 |
| `drop_high_missing_median` | broad | 0.19 | 0.3874 | 0.9800 | 0.7504 | 0.8649 | 310 | 4 | 5100 |
| `baseline_median_all` | refined | 0.13 | 0.4080 | 0.9750 | 0.7629 | 0.8887 | 283 | 5 | 5330 |

解释边界：

- Day15 没有使用 official test；
- valid 最优不是最终模型；
- `median_all_structural_all` 是当前 valid 成本最低的 tuned 候选，但仍然包含较多结构特征，只适合进入 Day16 做 official test 观察；
- `drop_high_missing_median` 是更轻量的缺失处理候选，也建议进入 Day16 作为对照；
- 如果 Day16 official test 结果不稳定，不能回头用 test 反向修改 Day15 参数或 refined search space。

## Day 16：Tuned XGBoost Official Test Evaluation

Day16 固定 Day15 valid 上选出的 XGBoost 参数和 threshold，在 official test 上做最终观察。本轮不重新调参、不重新选 threshold，也不根据 official test 结果反向修改 Day15。

### metrics

| 文件 | 说明 |
|---|---|
| `outputs/metrics/day16_xgb_tuning_test_results.csv` | Day15 tuned candidates 在 official test 上的最终观察结果，包括 precision、recall、F2、AP、FP、FN 和 total_cost。 |
| `outputs/metrics/day16_xgb_tuning_valid_test_compare.csv` | Day15 valid best 与 Day16 official test 的对比表，用于观察调参收益是否泛化。 |

### predictions

| 文件 | 说明 |
|---|---|
| `outputs/predictions/day16_xgb_tuning_test_predictions.csv` | 3 个 tuned candidates 在 official test 上的预测明细。该文件只用于最终观察，不能用于反向调参。 |

### tables

| 文件 | 说明 |
|---|---|
| `outputs/tables/day16_xgb_tuning_test_metadata.csv` | Day16 每个候选方案的参数来源、阈值来源、特征数量、删除字段、结构特征数量等元数据。 |

### figures

| 文件 | 说明 |
|---|---|
| `outputs/figures/day16_xgb_tuning_test_cost_compare.png` | Day16 tuned candidates 的 official test total cost 对比。 |
| `outputs/figures/day16_xgb_tuning_valid_vs_test_cost.png` | Day15 valid cost 与 Day16 official test cost 对比。 |

### 当前结论

Day16 tuned candidates 的 official test 成本没有超过 Day14 未调参 `median_all_structural_all`。因此 Day15 的低 valid cost 不应写成最终模型效果，后续应转向 SQL 深化、模型解释性分析和 README / 报告收尾。

## Day 17：OOF Threshold Selection and Bin Projection 输出说明

Day17 输出只来自 official train 内部的 OOF / Repeated CV 实验，不包含 official test 结果，不能解释为最终模型效果。

### metrics

| 文件 | 说明 |
|---|---|
| `outputs/metrics/day17_oof_threshold_metrics.csv` | 每个 candidate_strategy 在 OOF averaged prediction 上的完整 threshold grid 指标。 |
| `outputs/metrics/day17_oof_best_threshold_summary.csv` | 每个 candidate_strategy 在 `cost_min`、Recall floor 和 FN floor 规则下选出的 OOF 阈值摘要。 |
| `outputs/metrics/day17_oof_stability_summary.csv` | 在所选阈值下，不同 fold/repeat 的 cost、FN、recall、precision、F2 波动统计。 |
| `outputs/metrics/day17_oof_strategy_compare.csv` | 便于横向比较不同策略与不同阈值规则的摘要表。 |

### predictions

| 文件 | 说明 |
|---|---|
| `outputs/predictions/day17_oof_raw_predictions.csv` | 每个 repeat/fold 的 OOF 预测明细，同一样本在不同 repeat 中可能有多条预测。 |
| `outputs/predictions/day17_oof_averaged_predictions.csv` | 同一样本跨 repeats 取平均后的 OOF 预测，用于最终 OOF threshold selection。 |

### tables

| 文件 | 说明 |
|---|---|
| `outputs/tables/day17_oof_fold_summary.csv` | 每个 candidate_strategy、repeat、fold 的样本量和正类数量。 |
| `outputs/tables/day17_bin_projection_metadata.csv` | bin projection 使用的匿名 prefix、源字段、bin 数量和生成特征名。 |
| `outputs/tables/day17_oof_candidate_metadata.csv` | 每个 OOF fold 的候选策略特征数量、结构特征数量和 bin projection 特征数量。 |

### figures

| 文件 | 说明 |
|---|---|
| `outputs/figures/day17_oof_cost_threshold_curve.png` | OOF threshold 与 total cost 曲线。 |
| `outputs/figures/day17_oof_recall_threshold_curve.png` | OOF threshold 与 recall 曲线。 |
| `outputs/figures/day17_oof_strategy_cost_compare.png` | `cost_min` 规则下不同策略的 OOF total cost 对比。 |
| `outputs/figures/day17_oof_threshold_rule_compare.png` | 不同 Recall/FN floor 规则下的 OOF total cost 对比。 |

本次本地运行实际使用 `5 folds x 1 repeat`，配置文件仍保留默认 `5 folds x 2 repeats`。若后续离线复盘可按配置跑满更大规模。

## Day 18 OOF Probability Ensemble 输出说明

Day18 输出只来自 official train 内部 OOF 实验，不包含 official test 结果，不应解释为最终模型效果。

### predictions

| 文件 | 说明 |
|---|---|
| `outputs/predictions/day18_oof_base_raw_predictions.csv` | 三个 base strategy 在每个 fold_valid 上的原始 OOF 预测。 |
| `outputs/predictions/day18_oof_base_averaged_predictions.csv` | 按 sample 和 base strategy 聚合后的 OOF 平均概率；当前为 5 folds x 1 repeat。 |
| `outputs/predictions/day18_oof_ensemble_predictions.csv` | 12 个固定 recipe 生成的 OOF ensemble score。 |

### metrics

| 文件 | 说明 |
|---|---|
| `outputs/metrics/day18_oof_base_threshold_metrics.csv` | base strategy 的完整 OOF threshold grid。 |
| `outputs/metrics/day18_oof_base_best_summary.csv` | base strategy 的 `cost_min` OOF 阈值摘要。 |
| `outputs/metrics/day18_oof_ensemble_threshold_metrics.csv` | 12 个 ensemble recipe 的完整 threshold grid。 |
| `outputs/metrics/day18_oof_ensemble_best_summary.csv` | 每个 ensemble 在 cost_min / recall floor / FN floor 下的 OOF 最佳阈值。 |
| `outputs/metrics/day18_oof_ensemble_strategy_compare.csv` | 便于横向对比 ensemble recipe 与 threshold rule 的汇总表。 |

### tables

| 文件 | 说明 |
|---|---|
| `outputs/tables/day18_oof_fn_overlap_summary.csv` | 以 structural_all 为 reference 的 FN overlap 与可补回样本数量。 |
| `outputs/tables/day18_oof_fp_overlap_summary.csv` | 三个 base strategy 的 FP 重叠关系。 |
| `outputs/tables/day18_oof_rescuable_positive_samples.csv` | structural_all 漏掉的正类样本及其他模型是否能补回。 |
| `outputs/tables/day18_oof_ensemble_recipe_metadata.csv` | 12 个 ensemble recipe 的权重、分组和用途说明。 |
| `outputs/tables/day18_official_test_candidate_recommendations.csv` | 根据 OOF cost、FN reduction 和 FP/FN tradeoff 筛选 Day19 official test 候选；当前无推荐候选。 |
| `outputs/tables/day18_oof_base_candidate_metadata.csv` | base OOF strategy 的 fold 级特征数量和结构特征信息。 |
| `outputs/tables/day18_oof_base_fold_summary.csv` | 每个 fold 的训练/验证行数和正类数量。 |

### figures

| 文件 | 说明 |
|---|---|
| `outputs/figures/day18_oof_ensemble_cost_compare.png` | cost_min 下 ensemble total cost 对比。 |
| `outputs/figures/day18_oof_ensemble_fn_fp_tradeoff.png` | cost_min 下 FP/FN 权衡散点图。 |
| `outputs/figures/day18_oof_ensemble_threshold_rule_compare.png` | 不同 threshold selection rule 的最低 OOF cost。 |
| `outputs/figures/day18_oof_fn_overlap_summary.png` | structural_all FN 被 indicator / prefix zero 补回的数量。 |

## Day 19 SQL business analysis exports

Day 19 不做建模，只把当前最终候选 `median_all_structural_all` 的 official test 预测结果整理成 MySQL 可导入表，并补充业务分析 SQL。

### sql_exports

| 文件 | 说明 |
|---|---|
| `outputs/sql_exports/model_prediction_results.csv` | Day14 `median_all_structural_all` final candidate 的 official test 样本级预测结果，包含 risk level、confusion type、sample cost、probability band 和 decile。 |
| `outputs/sql_exports/model_policy_comparison.csv` | naive baseline、Day14 baseline、Day14 final candidate、Day16 tuned best 和 Day18 OOF best 的策略级成本对比。注意 OOF 结果不可与 official test 直接横向比较。 |
| `outputs/sql_exports/threshold_sensitivity_results.csv` | 基于 final candidate 概率的 0.01-0.99 阈值敏感性表，只用于业务策略观察，不用于修改最终阈值。 |
| `outputs/sql_exports/sql_export_manifest.csv` | Day19 导出文件清单，记录行数、列数、目标 MySQL 表和生成时间。 |

### sql files

| 文件 | 说明 |
|---|---|
| `sql/00_create_business_analysis_tables.sql` | 创建 Day19 业务分析 MySQL 表。 |
| `sql/08_topk_maintenance_capacity_analysis.sql` | Top-K 维修容量分析：检查 Top 50/100/200/500/1000 高风险样本时能覆盖多少真实故障。 |
| `sql/09_risk_workload_analysis.sql` | 风险等级与维修工作量分析。 |
| `sql/10_prediction_error_analysis.sql` | TP/FP/TN/FN、FP/FN 风险档和概率区间错误分析。 |
| `sql/11_business_cost_policy_comparison.sql` | naive baseline、Day14、Day16、Day18 OOF 的成本策略对比。 |
| `sql/12_model_monitoring_template.sql` | 未来上线批次监控模板，不代表已有生产数据。 |
| `sql/13_decile_lift_gain_analysis.sql` | decile / lift / gain 排序能力分析。 |
| `sql/14_threshold_sensitivity_analysis.sql` | 阈值变化下的工作量、FP、FN、recall、F2 和 total cost 分析。 |

## Day 20 SQL business insights and visualization

Day20 不做建模、不重新选择 threshold、不连接 MySQL，只读取 Day19 `outputs/sql_exports/` CSV，将 SQL 业务分析口径转成 README / report 可引用的 final tables、final figures 和业务洞察报告。

### Day20 final tables

| 文件 | 说明 |
|---|---|
| `outputs/tables/final/final_topk_maintenance_capacity.csv` | Top-K 维修容量分析，展示 Top 50/100/200/500/1000 高风险匿名样本覆盖多少真实 APS 故障。 |
| `outputs/tables/final/final_risk_workload_summary.csv` | 按 `risk_level` 和 `suggested_action` 汇总样本数、真实故障率、预测正类数、TP/FP/FN 和工作量。 |
| `outputs/tables/final/final_error_breakdown_summary.csv` | 按 confusion type、risk level 和 probability band 汇总错误来源与样本成本。 |
| `outputs/tables/final/final_decile_lift_gain_summary.csv` | Decile / lift / gain 分析，`decile=1` 表示预测概率最高的 10% 样本。 |
| `outputs/tables/final/final_threshold_sensitivity_summary.csv` | 基于 Day14 final candidate 概率的 threshold sensitivity 汇总，使用标准列名 `precision`、`recall`、`f2`。 |
| `outputs/tables/final/final_threshold_policy_highlights.csv` | `final_threshold_018`、min cost、recall floor、FN floor 等策略敏感性高亮；不用于反向修改最终阈值。 |
| `outputs/tables/final/final_policy_cost_comparison.csv` | official test policy 与 oof_train policy 的成本对比表；OOF 行单独标注不可与 official test 直接横向比较。 |

### Day20 final figures

| 文件 | 说明 |
|---|---|
| `outputs/figures/final/final_cost_policy_comparison.png` | official test policy total cost 对比。 |
| `outputs/figures/final/final_topk_maintenance_capacity.png` | Top-K 维修容量与 recall@K。 |
| `outputs/figures/final/final_risk_level_workload.png` | 风险等级样本数与真实故障率。 |
| `outputs/figures/final/final_decile_lift_gain.png` | Decile lift 与累计 recall。 |
| `outputs/figures/final/final_threshold_sensitivity.png` | Threshold vs total cost，标注 Day14 final threshold=0.18。 |
| `outputs/figures/final/final_threshold_fn_curve.png` | Threshold vs FN curve。 |
| `outputs/figures/final/final_threshold_workload_curve.png` | Threshold vs workload rate。 |
| `outputs/figures/final/final_confusion_error_breakdown.png` | TP / FP / FN / TN 数量对比。 |

### Day20 reports and notebook

| 文件 | 说明 |
|---|---|
| `reports/sql_business_insights.md` | SQL business insights 报告，包含 Top-K、风险工作量、成本策略、Lift/Gain、阈值敏感性和错误分析结论。 |
| `notebooks/20_sql_business_insights_and_visualization.ipynb` | Day20 展示 notebook，只读取 Day19/Day20 CSV 和 final figures，不连接 MySQL。 |

Day20 当前业务结论：最终候选仍是 Day14 `median_all_structural_all`，official test threshold=0.18、FP=398、FN=12、total_cost=9980；Day6 的 8640 仍是 test 回溯观察，Day16 tuned 没有泛化，Day18 ensemble 未满足进入 official test 条件。
