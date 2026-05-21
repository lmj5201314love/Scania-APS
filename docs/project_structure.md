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
