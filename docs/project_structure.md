# 项目结构说明

本文档用于说明当前 Scania APS 预测性维护项目的目录职责和核心脚本入口，避免后续迭代时文件越来越多、功能边界变得不清楚。

## 根目录

- `README.md`：面向 GitHub、简历和面试官的项目总览，重点展示业务背景、核心结果、运行方式和项目局限。
- `AGENTS.md`：给 Codex 或后续协作者使用的项目协作规范。
- `config/config.yaml`：项目配置的单一事实来源，包含数据路径、标签映射、缺失值 token、业务成本、评估指标、模型参数、validation 划分配置和消融实验配置。
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

Notebook 用于记录分析过程，不应堆放大量可复用函数；可复用逻辑应放入 `src/scania_aps/`。

## src/scania_aps/

- `config.py`：统一读取 `config/config.yaml`，返回项目配置对象。
- `data/load_data.py`：读取原始 train/test，并按配置映射 target。
- `data/clean_data.py`：baseline 和提升模型使用的基础数据准备逻辑。
- `data/split_data.py`：从官方 training set 中划分 train_inner / valid，并保存 split indices。
- `features/build_features.py`：缺失值与特征工程消融实验的数据处理模块，支持 median、drop_50/drop_80、缺失指示、原生缺失、低方差、高相关和 L1 特征选择等策略。
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

测试只覆盖关键业务函数，不追求过度工程化。
