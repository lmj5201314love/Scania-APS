# 项目结构说明

本文档用于说明当前 Scania APS 预测性维护项目的目录职责和核心脚本入口，避免后续迭代时文件越来越多、功能边界变得不清楚。

## 根目录

- `README.md`：面向 GitHub、简历和面试官的项目总览，重点展示业务背景、核心结果、运行方式和项目局限。
- `AGENTS.md`：给 Codex 或后续协作者使用的项目协作规范。
- `config/config.yaml`：项目配置的单一事实来源，包含数据路径、标签映射、缺失值 token、业务成本、评估指标、模型参数、validation 划分配置和消融实验配置。
- `config/structural_features.yaml`：Day 12 结构特征设计配置，记录候选前缀组、样本级统计、prefix 聚合、missing indicator 和异常统计的开关与阈值。
- `requirements.txt`：项目基础依赖。
- `.env.example`：MySQL 连接配置模板，不包含真实密码。

## data/

- `data/raw/`：原始 Scania APS train/test CSV。该目录下文件禁止修改、覆盖、重命名或删除。
- `data/interim/`：中间数据目录。本轮 validation 增强会在 `data/interim/splits/` 保存 train_inner / valid 的原始索引。
- `data/processed/`：后续可复现实验中生成的处理后数据目录，目前不作为主流程输出位置。

## notebooks/

- `01_data_understanding.ipynb`：Day 1 数据理解和业务背景。
- `02_missing_value_analysis.ipynb`：Day 2 基础数据质量、缺失值和标签分布分析。
- `03_sql_analysis_support.ipynb`：Day 3 SQL 支撑说明和辅助表准备。
- `04_model_baseline.ipynb`：Day 4 Dummy / Logistic baseline。
- `05_model_improvement.ipynb`：Day 5 Random Forest / XGBoost 提升模型对比。
- `06_threshold_cost_analysis.ipynb`：Day 6 基于已有预测概率的阈值成本敏感性分析。
- `07_risk_level_and_business_summary.ipynb`：Day 7 风险分层、维修优先级和业务交付总结。
- `08_validation_model_selection.ipynb`：validation-based model selection，在 valid 上选择模型和阈值，再在 official test 上评估。
- `09_feature_ablation_experiments.ipynb`：缺失值与特征工程消融实验，对比缺失处理、缺失指示、原生缺失和基础特征筛选策略。
- `10_distribution_and_structural_signal_analysis.ipynb`：Day 10 字段级分布诊断，分析缺失率、零值率、偏态、长尾、pos/neg 差异和 train/test 漂移。
- `11_prefix_group_signal_analysis.ipynb`：Day 11 前缀组结构信号分析，把匿名字段前缀作为结构分组线索，为 Day 12 结构特征设计做准备。
- `12_structural_feature_design.ipynb`：Day 12 结构特征方案设计，只整理特征家族、fit/transform 边界和 Day 13 实验矩阵，不训练模型。

Notebook 用于记录分析过程，不应堆放大量可复用函数；可复用逻辑应放入 `src/scania_aps/`。

## src/scania_aps/

- `config.py`：统一读取 `config/config.yaml`，返回项目配置对象。
- `data/load_data.py`：读取原始 train/test，并按配置映射 target。
- `data/clean_data.py`：baseline 和提升模型使用的基础数据准备逻辑。
- `data/split_data.py`：从官方 training set 中划分 train_inner / valid，并保存 split indices。
- `analysis/distribution_diagnostics.py`：字段级分布诊断工具，输出缺失、零值、偏态、长尾、pos/neg 差异和 train/valid/test 漂移统计。
- `analysis/prefix_group_analysis.py`：前缀组结构信号分析工具，基于 Day 10 输出聚合匿名字段前缀组统计、信号排序和组内字段明细。
- `features/build_features.py`：缺失值与特征工程消融实验的数据处理模块，支持 median、drop_50/drop_80、缺失指示、原生缺失、低方差、高相关和 L1 特征选择等策略。
- `features/structural_feature_design.py`：Day 12 结构特征设计表生成工具，只生成设计说明表，不生成训练特征矩阵。
- `evaluation/cost_utils.py`：成本敏感评估函数，成本必须来自 cfg。
- `evaluation/metrics.py`：precision、recall、F1、F2、PR-AUC 和 total cost 评估。
- `evaluation/threshold_utils.py`：阈值网格分析和低成本阈值汇总。
- `evaluation/risk_utils.py`：风险等级、维修建议和预测类型分类。
- `models/train_baseline.py`：Dummy / Logistic baseline 训练和评估。
- `models/train_advanced.py`：Random Forest / XGBoost 提升模型训练和评估。
- `models/validation_selection.py`：在 train_inner/valid/test 流程中选择模型、策略和阈值。
- `models/feature_ablation.py`：运行缺失值与特征工程消融实验，在 valid 上选择阈值，并在 official test 上评估。

以下模块为后续增强预留，当前只保留说明，避免空文件造成误解：

- `models/predict.py`：后续批量预测入口。
- `database/mysql_io.py`、`database/write_predictions.py`：后续自动写入 MySQL。
- `visualization/plots.py`：后续复用可视化函数。

## scripts/

- `02_train_baseline.py`：从项目根目录运行 Day 4 baseline。
- `03_train_advanced_models.py`：从项目根目录运行 Day 5 提升模型对比。
- `04_evaluate_thresholds.py`：读取 Day 4/Day 5 预测概率，运行 Day 6 阈值成本分析。
- `05_build_risk_tables.py`：读取 Day 6 最优阈值和 Day 5 预测概率，生成 Day 7 风险分层和维修优先级 CSV。
- `06_validation_model_selection.py`：运行 validation-based model selection，生成 valid 阈值结果和 official test 最终评估。
- `07_feature_ablation_experiments.py`：运行缺失值与特征工程消融实验，输出 valid 阈值结果、official test 评估和策略元数据。
- `08_distribution_diagnostics.py`：运行 Day 10 字段级分布诊断，生成可复用诊断表和基础图表。
- `09_prefix_group_analysis.py`：运行 Day 11 前缀组结构信号分析，生成 prefix group 统计、排序、成员表和图表。
- `10_build_structural_feature_design.py`：生成 Day 12 结构特征设计表，明确每类特征的来源、计算方式、fit/transform 边界和 Day 13 优先级。
- `generate_create_tables_sql.py`：根据原始 CSV 表头生成 MySQL 建表 SQL。
- `generate_mysql_schema.py`：生成原始宽表相关 MySQL schema。
- `generate_sql_missing_analysis.py`：生成宽表缺失率 SQL。
- `prepare_sql_support_tables.py`：把 Day 2 输出整理成适合导入 MySQL 的辅助表。

已删除空的 `01_prepare_data.py`，因为当前数据读取和准备已经由 `src/scania_aps/data/` 与训练脚本承担，保留空入口会误导读者。

## sql/

- `00_init_database.sql`：创建和切换数据库。
- `01_create_tables.sql`：创建原始宽表和辅助分析表。
- `02_import_check.sql`：导入后基础检查。
- `03_data_quality_summary.sql`：基础数据质量 SQL 复核。
- `04_missing_summary_analysis.sql`：缺失率和缺失模式 SQL 分析。
- `05_business_cost_analysis.sql`：业务成本复核，使用 SQL 会话变量表示 FP/FN 成本。
- `06_model_result_analysis.sql`：预测结果、默认阈值和概率分桶分析。
- `07_risk_level_analysis.sql`：风险分层、维修优先级和成本对比分析。
- `load_data_import.sql`：CSV 导入辅助 SQL。

SQL 中的成本变量应与 `config/config.yaml` 保持一致；正式生产版本可以由 Python 根据 cfg 自动生成 SQL。

## outputs/

- `outputs/metrics/`：模型指标、阈值分析结果和 validation-based selection 结果。
- `outputs/predictions/`：模型预测概率和预测标签，包括 validation 与 official test 的预测结果。
- `outputs/tables/`：数据质量、SQL 辅助表、风险分层、业务汇总表和 validation split 摘要。
- `outputs/figures/`：缺失分析和阈值分析图表。

validation 增强新增的主要输出包括：

- `outputs/metrics/validation_threshold_metrics.csv`
- `outputs/metrics/validation_best_threshold_summary.csv`
- `outputs/metrics/final_test_evaluation_from_valid_selection.csv`
- `outputs/metrics/validation_vs_day6_backtest_compare.csv`
- `outputs/predictions/validation_predictions.csv`
- `outputs/predictions/final_test_predictions_from_valid_selection.csv`
- `outputs/tables/validation_split_summary.csv`
- `data/interim/splits/train_inner_indices.csv`
- `data/interim/splits/valid_indices.csv`

缺失值与特征工程消融实验新增的主要输出包括：

- `outputs/metrics/feature_ablation_valid_threshold_metrics.csv`
- `outputs/metrics/feature_ablation_valid_best_summary.csv`
- `outputs/metrics/feature_ablation_final_test_results.csv`
- `outputs/tables/feature_ablation_strategy_metadata.csv`
- `outputs/tables/missing_indicator_signal_summary.csv`

Day 10 字段级分布诊断新增的主要输出包括：

- `outputs/metrics/day10_feature_distribution_summary.csv`
- `outputs/metrics/day10_missing_zero_summary.csv`
- `outputs/metrics/day10_pos_neg_distribution_diff.csv`
- `outputs/metrics/day10_train_valid_test_drift_summary.csv`
- `outputs/metrics/day10_top_feature_diagnostics.csv`
- `outputs/figures/day10_top_skewed_features.png`
- `outputs/figures/day10_pos_neg_missing_diff_top20.png`
- `outputs/figures/day10_train_test_drift_top20.png`
- `outputs/figures/day10_zero_rate_top20.png`

Day 11 前缀组结构信号分析新增的主要输出包括：

- `outputs/metrics/day11_prefix_group_summary.csv`
- `outputs/metrics/day11_prefix_group_signal_ranking.csv`
- `outputs/tables/day11_prefix_feature_members.csv`
- `outputs/figures/day11_prefix_avg_missing_rate_top20.png`
- `outputs/figures/day11_prefix_avg_zero_rate_top20.png`
- `outputs/figures/day11_prefix_pos_neg_missing_diff_top20.png`
- `outputs/figures/day11_prefix_signal_score_top20.png`
- `outputs/figures/day11_prefix_drift_risk_top20.png`

Day 12 结构特征方案设计新增的主要输出包括：

- `docs/structural_feature_design.md`
- `config/structural_features.yaml`
- `outputs/tables/day12_structural_feature_design_table.csv`

这些是本地运行产物，通常不应强行提交到 GitHub。

## reports/

- `summary.md`：按 Day 和增强阶段记录阶段性总结。
- `missing_value_strategy.md`：缺失值处理策略说明。
- `project_report.md`：完整项目报告。
- `resume_bullets.md`：简历项目经历表达。
- `interview_qa.md`：面试问答准备。

## tests/

- `test_cost_utils.py`：成本敏感函数测试。
- `test_threshold_utils.py`：阈值分析工具测试。
- `test_split_data.py`：validation 划分工具测试。
- `test_output_schema.py`：关键输出文件 schema 轻量检查。
- `test_feature_building.py`：缺失值与特征构建策略的轻量单元测试。
- `test_feature_ablation_schema.py`：消融实验结果表 schema 测试。
- `test_distribution_diagnostics.py`：字段级分布诊断函数测试。
- `test_prefix_group_analysis.py`：前缀组结构信号分析函数测试。
- `test_structural_feature_design.py`：结构特征设计配置和设计表生成测试。

测试只覆盖关键业务函数，不追求过度工程化。

## Day 13 结构特征 valid 实验补充

Day 13 新增文件和输出如下：

- `src/scania_aps/features/structural_features.py`：结构特征 fit/transform 工具，只在 train_inner 上确定字段列表、前缀成员关系和 selected missing indicator 字段，再应用到 valid。
- `src/scania_aps/models/structural_feature_experiments.py`：结构特征 valid-only 实验模块，使用 XGBoost 比较不同结构特征组的 valid 阈值结果。
- `scripts/11_structural_feature_valid_experiments.py`：从项目根目录运行 Day 13 实验，只使用 train_inner / valid，不使用 official test。
- `notebooks/13_structural_feature_valid_experiments.ipynb`：记录 Day 13 实验流程、实验组、valid 结果和 Day 14 建议。
- `tests/test_structural_features.py`：测试样本级缺失率、样本级零值率、前缀组零值率、selected missing indicators 和 transform 不修改原始 DataFrame。
- `tests/test_structural_feature_experiments_schema.py`：测试结构特征实验结果表 schema。

Day 13 新增本地输出：

- `outputs/metrics/day13_structural_feature_valid_threshold_metrics.csv`
- `outputs/metrics/day13_structural_feature_valid_best_summary.csv`
- `outputs/tables/day13_structural_feature_experiment_metadata.csv`
- `outputs/tables/day13_selected_missing_indicator_columns.csv`
- `outputs/tables/day13_structural_feature_names_by_group.csv`

这些输出只代表 valid 阶段结果，不应被解释为 official test 或生产环境最终结论。

## Day 14 结构特征 official test 观察补充

Day 14 新增文件和输出如下：

- `src/scania_aps/models/structural_feature_test_evaluation.py`：结构特征候选方案 official test 观察模块，固定使用 Day 13 valid 阈值，不在 test 上重新选择方案。
- `scripts/12_structural_feature_test_evaluation.py`：从项目根目录运行 Day 14 official test 观察，输出 test 指标、预测明细、valid/test 对比和元数据。
- `notebooks/14_structural_feature_test_evaluation.ipynb`：记录 Day 14 固定候选方案、official test 观察结果和泛化判断。
- `tests/test_structural_feature_test_evaluation_schema.py`：使用小型模拟数据测试 Day 14 输出 schema 和阈值来源。

Day 14 新增本地输出：

- `outputs/metrics/day14_structural_feature_test_results.csv`
- `outputs/metrics/day14_structural_feature_valid_test_compare.csv`
- `outputs/predictions/day14_structural_feature_test_predictions.csv`
- `outputs/tables/day14_structural_feature_test_metadata.csv`

这些输出只用于观察 Day 13 valid 候选方案在 official test 上的泛化情况，不能用于反向修改 Day 13 候选组或阈值。


## Day 15 Controlled XGBoost Tuning 补充

Day 15 新增文件和输出如下：

- `src/scania_aps/models/xgb_tuning.py`：受控 XGBoost 调参模块，支持参数随机采样、broad/refined 搜索空间构造、候选策略特征准备、trial 级阈值评估和 valid best summary 汇总。
- `scripts/13_xgb_tuning_valid_experiments.py`：从项目根目录运行 Day15 two-stage randomized search。脚本只使用 `train_inner / valid`，不使用 official test。
- `notebooks/15_xgb_tuning_valid_experiments.ipynb`：记录 Day15 调参目标、候选策略、broad/refined 思路和输出复盘方式。
- `tests/test_xgb_tuning_schema.py`：使用小型模拟数据测试参数采样、refined search space 构造、特征准备和 trial 结果 schema。

Day15 新增本地输出：

- `outputs/metrics/day15_xgb_tuning_valid_trial_results.csv`：每个 trial 在 valid 上的最佳阈值结果。
- `outputs/metrics/day15_xgb_tuning_valid_best_summary.csv`：每个候选策略的 valid 最优 trial 摘要。
- `outputs/metrics/day15_xgb_tuning_valid_threshold_metrics.csv`：所有 trial 的完整 threshold grid 结果。
- `outputs/metrics/day15_xgb_tuning_refinement_summary.csv`：broad 与 refined 阶段对比。
- `outputs/tables/day15_xgb_tuning_candidate_metadata.csv`：候选策略特征数量、结构特征数量、运行 trial 数等元数据。
- `outputs/tables/day15_xgb_tuning_search_space.csv`：broad/refined 搜索空间展开表。
- `outputs/tables/day15_xgb_tuning_top_trials_by_strategy.csv`：每个候选策略用于 refined 阶段的 top trials。
- `outputs/predictions/day15_xgb_tuning_valid_best_predictions.csv`：每个候选策略 valid best trial 的 valid 预测明细。
- `outputs/figures/day15_xgb_tuning_valid_cost_top20.png`：valid cost Top 20 trial 图。
- `outputs/figures/day15_xgb_tuning_strategy_cost_compare.png`：候选策略最优 valid cost 对比图。
- `outputs/figures/day15_xgb_tuning_broad_vs_refined.png`：broad 与 refined 阶段最优成本对比图。

这些输出只代表 valid 阶段调参结果，不能被解释为 official test 或生产最终结论。Day16 才能对少数 tuned 候选方案做 official test 观察。

## Day 16 Tuned XGBoost Official Test Evaluation 补充

Day16 新增文件和输出如下：

- `src/scania_aps/models/xgb_tuning_test_evaluation.py`：读取 Day15 valid best summary 中的固定参数和 threshold，在 official test 上评估 tuned XGBoost candidates。
- `scripts/14_xgb_tuning_test_evaluation.py`：从项目根目录运行 Day16 official test 观察；不重新调参、不重新选阈值。
- `notebooks/16_xgb_tuning_test_evaluation.ipynb`：记录 Day16 目标、固定候选方案、official test 结果、valid/test 对比和后续建议。
- `tests/test_xgb_tuning_test_evaluation_schema.py`：使用小型模拟数据测试 Day16 输出 schema、阈值来源和参数读取逻辑。

Day16 新增本地输出：

- `outputs/metrics/day16_xgb_tuning_test_results.csv`
- `outputs/metrics/day16_xgb_tuning_valid_test_compare.csv`
- `outputs/predictions/day16_xgb_tuning_test_predictions.csv`
- `outputs/tables/day16_xgb_tuning_test_metadata.csv`
- `outputs/figures/day16_xgb_tuning_test_cost_compare.png`
- `outputs/figures/day16_xgb_tuning_valid_vs_test_cost.png`

这些输出只用于观察 Day15 tuned candidates 在 official test 上的泛化表现，不能用于反向修改 Day15 参数、阈值或候选特征方案。

## Day 17 OOF 阈值稳定性与 Bin Projection 补充

Day17 新增文件和输出如下：

- `src/scania_aps/features/bin_projection.py`：匿名 histogram/bin-like 前缀组投影特征工具，支持 prefix/bin index 解析、bin group membership fit、行级 projection 特征 transform 和 metadata 输出。
- `src/scania_aps/models/oof_threshold_experiments.py`：OOF / Repeated CV 阈值选择实验模块，支持 cost_min、Recall floor、FN floor 和 OOF 稳定性汇总。
- `scripts/15_oof_recall_floor_bin_projection.py`：从项目根目录运行 Day17 实验，只使用 official train，不使用 official test。
- `notebooks/17_oof_recall_floor_bin_projection.ipynb`：记录 Day17 实验边界、OOF 逻辑、Recall/FN floor、bin projection 和 Day18 候选建议。
- `tests/test_bin_projection.py`：bin projection 解析、排序、NaN/全零安全处理和不修改原始 DataFrame 的单元测试。
- `tests/test_oof_threshold_experiments_schema.py`：OOF split 和带约束 threshold selection 的轻量 schema 测试。

Day17 新增本地输出：

- `outputs/metrics/day17_oof_threshold_metrics.csv`
- `outputs/metrics/day17_oof_best_threshold_summary.csv`
- `outputs/metrics/day17_oof_stability_summary.csv`
- `outputs/metrics/day17_oof_strategy_compare.csv`
- `outputs/predictions/day17_oof_raw_predictions.csv`
- `outputs/predictions/day17_oof_averaged_predictions.csv`
- `outputs/tables/day17_oof_fold_summary.csv`
- `outputs/tables/day17_bin_projection_metadata.csv`
- `outputs/tables/day17_oof_candidate_metadata.csv`
- `outputs/figures/day17_oof_cost_threshold_curve.png`
- `outputs/figures/day17_oof_recall_threshold_curve.png`
- `outputs/figures/day17_oof_strategy_cost_compare.png`
- `outputs/figures/day17_oof_threshold_rule_compare.png`

这些输出只代表 official train 内部 OOF 分析结果，不应解释为 official test 或生产环境最终结论。

## Day 18 OOF Probability Ensemble 补充

Day18 新增文件和输出如下：

- `src/scania_aps/models/oof_ensemble_experiments.py`：同折 OOF base prediction、FN/FP overlap、固定 recipe 概率 ensemble、threshold grid 和 Day19 候选筛选逻辑。
- `scripts/16_oof_probability_ensemble.py`：从项目根目录运行 Day18 OOF ensemble 实验；只使用 official train，不使用 official test。
- `notebooks/18_oof_probability_ensemble.ipynb`：记录 Day18 的实验边界、base strategy、overlap analysis、12 个 recipe、threshold rule 和候选筛选结论。
- `tests/test_oof_ensemble_experiments_schema.py`：用小型模拟数据测试 recipe 计算、rank average、threshold rule 和 diagnostic candidate 排除逻辑。

Day18 新增本地输出：

- `outputs/predictions/day18_oof_base_raw_predictions.csv`
- `outputs/predictions/day18_oof_base_averaged_predictions.csv`
- `outputs/predictions/day18_oof_ensemble_predictions.csv`
- `outputs/metrics/day18_oof_base_threshold_metrics.csv`
- `outputs/metrics/day18_oof_base_best_summary.csv`
- `outputs/metrics/day18_oof_ensemble_threshold_metrics.csv`
- `outputs/metrics/day18_oof_ensemble_best_summary.csv`
- `outputs/metrics/day18_oof_ensemble_strategy_compare.csv`
- `outputs/tables/day18_oof_fn_overlap_summary.csv`
- `outputs/tables/day18_oof_fp_overlap_summary.csv`
- `outputs/tables/day18_oof_rescuable_positive_samples.csv`
- `outputs/tables/day18_oof_ensemble_recipe_metadata.csv`
- `outputs/tables/day18_official_test_candidate_recommendations.csv`
- `outputs/tables/day18_oof_base_candidate_metadata.csv`
- `outputs/tables/day18_oof_base_fold_summary.csv`
- `outputs/figures/day18_oof_ensemble_cost_compare.png`
- `outputs/figures/day18_oof_ensemble_fn_fp_tradeoff.png`
- `outputs/figures/day18_oof_ensemble_threshold_rule_compare.png`
- `outputs/figures/day18_oof_fn_overlap_summary.png`

这些输出只代表 official train 内部 OOF 分析，不能解释为 official test 或生产环境最终结论。

## Day 19 SQL 业务分析与 MySQL 导入准备

Day 19 不继续追模型分数，转向 SQL 业务交付分析。核心目标是把当前最终候选 `median_all_structural_all` 的 official test 预测结果整理为 MySQL 可导入表，并提供维修容量、风险工作量、错误分析、成本对比、监控模板、decile/lift/gain 和阈值敏感性 SQL。

### 新增脚本

- `scripts/17_prepare_sql_business_tables.py`：读取 Day14/Day16/Day18 输出，生成 `outputs/sql_exports/` 下的 MySQL 导入 CSV。

### 新增导出目录

- `outputs/sql_exports/model_prediction_results.csv`
- `outputs/sql_exports/model_policy_comparison.csv`
- `outputs/sql_exports/threshold_sensitivity_results.csv`
- `outputs/sql_exports/sql_export_manifest.csv`

### 新增 SQL

- `sql/00_create_business_analysis_tables.sql`：创建业务分析表。
- `sql/08_topk_maintenance_capacity_analysis.sql`：Top-K 维修容量分析。
- `sql/09_risk_workload_analysis.sql`：风险等级和维修工作量分析。
- `sql/10_prediction_error_analysis.sql`：FP/FN 错误分析。
- `sql/11_business_cost_policy_comparison.sql`：策略级成本对比。
- `sql/12_model_monitoring_template.sql`：生产监控 SQL 模板。
- `sql/13_decile_lift_gain_analysis.sql`：decile / lift / gain 分析。
- `sql/14_threshold_sensitivity_analysis.sql`：阈值敏感性分析。

### 可选 Notebook

- `notebooks/19_sql_business_analysis.ipynb`：如需在无 MySQL 环境下快速预览 SQL 业务分析结果，可读取 `outputs/sql_exports/` CSV 进行本地展示。

Day 19 的 SQL 输出用于业务分析和面试讲述，不连接 MySQL、不导入 MySQL、不修改 `data/raw/`，也不改变 Day14 final candidate。

## Day 20 SQL Business Insights & Visualization

Day20 不继续建模，也不连接 MySQL。本轮只读取 Day19 `outputs/sql_exports/` CSV，把 SQL 业务分析结果转成 final tables、final figures 和可读业务洞察报告，服务 README、项目报告和面试复述。

Day20 新增文件如下：

- `scripts/18_generate_business_insight_figures.py`：读取 Day19 SQL exports，生成 final tables、PNG 图表和 `reports/sql_business_insights.md`。脚本不重新训练模型、不重新选择 threshold、不修改 `data/raw/`。
- `notebooks/20_sql_business_insights_and_visualization.ipynb`：展示 Day20 的 Top-K、风险工作量、成本策略、decile/lift/gain、阈值敏感性和错误分析结果。
- `reports/sql_business_insights.md`：面向 README 和面试复述的 SQL business insights 报告。
- `tests/test_business_insight_outputs.py`：使用小型模拟数据测试 Day20 汇总函数，不依赖真实 Scania 大文件、不连接 MySQL。

Day20 新增输出目录如下：

- `outputs/tables/final/`：保存 final Top-K、risk workload、error breakdown、decile/lift/gain、threshold sensitivity、policy comparison 等 CSV。
- `outputs/figures/final/`：保存 README/report 可引用的 final PNG 图表。

Day20 边界：当前最终候选仍是 Day14 `median_all_structural_all`，official test threshold=0.18、FP=398、FN=12、total_cost=9980；threshold sensitivity 只用于策略敏感性展示，不能用于反向修改最终阈值。

## Day 21 Model Interpretability & Presentation Audit

Day21 进入模型解释性和最终展示审计阶段。本轮允许为了复现 Day14 final candidate 重新 fit 同配置模型，但不调参、不重新选择 threshold、不根据解释结果改模型、不修改 `data/raw/`。

Day21 新增文件如下：

- `src/scania_aps/interpretability/__init__.py`：解释性分析包入口。
- `src/scania_aps/interpretability/model_interpretability.py`：复现 Day14 final candidate、计算 XGBoost importance、permutation importance、SHAP importance、feature family summary 和 case explanation tables。
- `scripts/19_model_interpretability.py`：运行 Day21 解释性分析，生成 final tables、final figures 和报告。
- `notebooks/21_model_interpretability.ipynb`：展示 Day21 解释性输出，不调参、不改 threshold。
- `reports/model_interpretability.md`：模型解释性报告。
- `reports/readme_presentation_audit.md`：README 展示审计报告，供 Day22 最终 README 改版使用。
- `tests/test_model_interpretability_schema.py`：使用小型模拟数据测试解释性输出 schema，不依赖真实 Scania 大文件。

Day21 新增 final tables：

- `outputs/tables/final/final_xgb_feature_importance_top50.csv`
- `outputs/tables/final/final_permutation_importance_top30.csv`
- `outputs/tables/final/final_shap_mean_abs_top50.csv`
- `outputs/tables/final/final_feature_family_importance_summary.csv`
- `outputs/tables/final/final_fn_shap_case_analysis.csv`
- `outputs/tables/final/final_high_risk_tp_shap_case_analysis.csv`
- `outputs/tables/final/final_high_confidence_fp_shap_case_analysis.csv`

Day21 新增 final figures：

- `outputs/figures/final/final_xgb_gain_importance_top20.png`
- `outputs/figures/final/final_permutation_importance_top20.png`
- `outputs/figures/final/final_shap_bar_top20.png`
- `outputs/figures/final/final_shap_summary_top20.png`
- `outputs/figures/final/final_feature_family_importance.png`

Day21 解释边界：SHAP / importance 只解释模型评分贡献，不能解释匿名字段真实物理含义；`sample_id` 仍然只是匿名样本编号，不是真实车辆 ID。
