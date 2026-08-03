# Notebook 使用说明

本目录按最终展示和历史实验过程分为两个子目录：

- `notebooks/final/`：用于展示最终分析主线，采用问题驱动的中文分析叙事，适合读者快速浏览项目关键流程和结果。它不是唯一复现入口，项目复现主入口仍然是 `scripts/`。
- `notebooks/archive/`：保存历史实验过程，用于审计、复盘和解释模型选择路径。archive notebook 已加入统一中文归档说明，但不逐篇全文精修；部分 archive notebook 依赖本地生成的过程 outputs，这些大文件不再上传 GitHub。

## 最终展示 notebook

这些 notebook 已完成 Final Packaging Day 4.5 去模板化修复：不再使用“分析目标 / 输入与输出 / 方法概述 / 关键结论 / 结果解释 / 注意事项”的六段式前置模板，而是按照“问题说明 → 代码 / 表格 / 图表 → 结果解释 → 项目决策影响”的顺序组织。Markdown 展示内容以中文为主，必要技术名词如 XGBoost、SHAP、PR-AUC、OOF 保留英文。

| Notebook | 用途 | 主要输入 | 主要输出 | 是否适合 GitHub 展示 |
|---|---|---|---|---|
| `final/01_data_understanding.ipynb` | 数据规模、标签含义和原始字段初步理解 | `data/raw/aps_failure_training_set.csv`, `data/raw/aps_failure_test_set.csv` | 数据理解记录 | 是，需要用户自行放置 raw CSV |
| `final/10_distribution_and_structural_signal_analysis.ipynb` | 字段级缺失、零值、漂移和结构信号诊断 | raw data、Day10 诊断模块 | Day10 诊断表和图 | 是 |
| `final/14_structural_feature_test_evaluation.ipynb` | 展示 Day14 final candidate 的 official test 结果 | Day13 valid-selected strategy、raw data | Day14 official test metrics | 是 |
| `final/20_sql_business_insights_and_visualization.ipynb` | 展示 SQL 业务洞察、Top-K、risk workload 和 lift/gain | `outputs/sql_exports/`, `outputs/tables/final/`, `outputs/figures/final/` | final business tables / figures | 是 |
| `final/21_model_interpretability.ipynb` | 展示 XGBoost importance、permutation、SHAP 和 feature family 贡献 | final interpretability tables / figures | final interpretability figures / case tables | 是 |

## 历史实验 notebook

archive notebook 保留项目从 baseline、阈值敏感性、validation、结构特征、调参、OOF 到 SQL 导出的历史过程。它们主要用于审计和复盘，不作为最终展示入口；如果需要复现历史实验，应优先查看 `reports/notebook_reproducibility_audit.md` 中的依赖和脚本说明。

| Notebook | 实验阶段 | 是否依赖生成产物 | 再生成入口 |
|---|---|---|---|
| `archive/02_missing_value_analysis.ipynb` | Day2 缺失值分析 | 只依赖 raw data | 下载原始 CSV 到 `data/raw/` |
| `archive/03_sql_analysis_support.ipynb` | Day3 SQL 支撑分析 | raw data / SQL 辅助表 | `python scripts/prepare_sql_support_tables.py` |
| `archive/04_model_baseline.ipynb` | Day4 基线建模 | `outputs/predictions/day4_baseline_predictions.csv` | `python scripts/02_train_baseline.py` |
| `archive/05_model_improvement.ipynb` | Day5 提升模型对比 | `outputs/predictions/day5_model_compare_predictions.csv` | `python scripts/03_train_advanced_models.py` |
| `archive/06_threshold_cost_analysis.ipynb` | Day6 阈值成本敏感性 | `outputs/metrics/day6_threshold_metrics.csv` | `python scripts/04_evaluate_thresholds.py` |
| `archive/07_risk_level_and_business_summary.ipynb` | Day7 风险分层和维修优先级 | `outputs/tables/day7_maintenance_priority_list.csv` | `python scripts/05_build_risk_tables.py` |
| `archive/08_validation_model_selection.ipynb` | Day8 validation-based selection | `outputs/metrics/validation_threshold_metrics.csv` | `python scripts/06_validation_model_selection.py` |
| `archive/09_feature_ablation_experiments.ipynb` | Day9 特征消融实验 | feature ablation 指标 | `python scripts/07_feature_ablation_experiments.py` |
| `archive/11_prefix_group_signal_analysis.ipynb` | Day11 前缀组信号分析 | prefix diagnostics 输出 | `python scripts/09_prefix_group_analysis.py` |
| `archive/12_structural_feature_design.ipynb` | Day12 结构特征设计 | 结构特征设计表 | `python scripts/10_build_structural_feature_design.py` |
| `archive/13_structural_feature_valid_experiments.ipynb` | Day13 结构特征 valid 实验 | `outputs/metrics/day13_structural_feature_valid_threshold_metrics.csv` | `python scripts/11_structural_feature_valid_experiments.py` |
| `archive/15_xgb_tuning_valid_experiments.ipynb` | Day15 受控 XGBoost 调参 | `outputs/metrics/day15_xgb_tuning_valid_trial_results.csv` | `python scripts/13_xgb_tuning_valid_experiments.py` |
| `archive/16_xgb_tuning_test_evaluation.ipynb` | Day16 tuned 方案 official test 观察 | Day15 调参摘要和 Day16 结果 | `python scripts/14_xgb_tuning_test_evaluation.py` |
| `archive/17_oof_recall_floor_bin_projection.ipynb` | Day17 OOF 阈值与 bin projection | OOF raw / averaged predictions 和 threshold metrics | `python scripts/15_oof_recall_floor_bin_projection.py` |
| `archive/18_oof_probability_ensemble.ipynb` | Day18 OOF probability ensemble | Day18 OOF 摘要和 overlap 表 | `python scripts/16_oof_probability_ensemble.py` |
| `archive/19_sql_business_analysis.ipynb` | Day19 SQL business export 预览 | `outputs/sql_exports/` 和 Day14 predictions | `python scripts/17_prepare_sql_business_tables.py` |

## 复现说明

- 项目复现主入口是 `scripts/`，notebooks 主要用于解释、展示和复盘。
- Day2 outputs cleanup 后，大型过程产物如 `outputs/predictions/*.csv`、部分 `*threshold_metrics.csv` 和 `*trial_results.csv` 不再上传 GitHub。
- 如果 archive notebook 读取这些过程产物，请先运行上表中的对应脚本重新生成。
- final notebooks 应优先依赖 `outputs/tables/final/`、`outputs/figures/final/` 和 `outputs/sql_exports/`，避免依赖大型 raw predictions。
- 原始 Scania APS CSV 不提交到 Git，用户需要自行下载并放入 `data/raw/`。
- 新增或修改 final notebook 时，应采用问题驱动叙事，在相关代码、表格或图表附近解释结果含义；不使用大段前置模板，不写入学习口吻、AI 协作痕迹或匿名字段的真实物理解释。
