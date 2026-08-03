# Notebook 复现依赖审计

本报告记录 Final Packaging Day 3 对 notebook 依赖关系的整理结果。本轮只调整 notebook 展示结构和复现说明，不删除 notebook、不移动 outputs、不重新训练模型、不重新生成 outputs，也不修改 `data/raw/`。

## 1. 整理原则

- `notebooks/final/` 保留最终展示主线，适合 GitHub 浏览和项目讲解。
- `notebooks/archive/` 保留历史实验过程，作为审计、复盘和学习记录。
- 复现主入口仍是 `scripts/`，notebook 主要用于展示分析过程和关键结论。
- 大型过程产物不再上传 GitHub，但本地保留；archive notebook 如需这些文件，应按下表运行对应脚本重新生成。
- `sample_id` 只表示匿名样本编号，不是真实车辆 ID。

## 2. Final Notebooks

| Notebook | 主要依赖 | GitHub 是否保留依赖 | 再生成入口 | 说明 |
|---|---|---|---|---|
| `notebooks/final/01_data_understanding.ipynb` | `data/raw/aps_failure_training_set.csv`、`data/raw/aps_failure_test_set.csv` | 否 | 用户自行下载 Scania APS 原始 CSV 并放入 `data/raw/` | 原始数据不提交 Git；该 notebook 只做数据理解和业务背景。 |
| `notebooks/final/10_distribution_and_structural_signal_analysis.ipynb` | Day10 字段分布诊断表和图 | 是 | `python scripts/08_distribution_diagnostics.py` | 用于展示缺失率、零值率、pos/neg 差异和漂移诊断。 |
| `notebooks/final/14_structural_feature_test_evaluation.ipynb` | Day14 final candidate 评估结果 | 部分保留 | `python scripts/12_structural_feature_test_evaluation.py` | `outputs/metrics/day14_structural_feature_test_results.csv` 继续上传；样本级预测明细本地保留、不再上传。 |
| `notebooks/final/20_sql_business_insights_and_visualization.ipynb` | `outputs/sql_exports/*.csv`、`outputs/tables/final/*.csv`、`outputs/figures/final/*.png` | 是 | `python scripts/17_prepare_sql_business_tables.py`；`python scripts/18_generate_business_insight_figures.py` | 展示 Top-K、risk level、lift/gain、threshold sensitivity 等最终业务洞察。 |
| `notebooks/final/21_model_interpretability.ipynb` | `outputs/tables/final/final_*importance*.csv`、`outputs/figures/final/final_*importance*.png`、SHAP case tables | 是 | `python scripts/19_model_interpretability.py` | 展示 XGBoost importance、permutation importance、SHAP 和 feature family 贡献。 |

## 3. Archive Notebooks

| Notebook | 依赖文件或模式 | GitHub 是否保留依赖 | 再生成入口 | 说明 |
|---|---|---|---|---|
| `notebooks/archive/02_missing_value_analysis.ipynb` | `data/raw/*.csv` | 否 | 用户自行下载 Scania APS 原始 CSV | 原始数据依赖正常，不提交 Git。 |
| `notebooks/archive/03_sql_analysis_support.ipynb` | `data/raw/*.csv`、`outputs/tables/sql_support/*.csv` | 原始数据否，辅助表是 | `python scripts/prepare_sql_support_tables.py` | SQL 辅助表用于早期 MySQL 分析支撑。 |
| `notebooks/archive/04_model_baseline.ipynb` | `outputs/predictions/day4_baseline_predictions.csv` | 否 | `python scripts/02_train_baseline.py` | 预测明细本地保留，不作为最终展示资产上传。 |
| `notebooks/archive/05_model_improvement.ipynb` | `outputs/predictions/day5_model_compare_predictions.csv` | 否 | `python scripts/03_train_advanced_models.py` | Random Forest / XGBoost 早期对比预测明细可再生成。 |
| `notebooks/archive/06_threshold_cost_analysis.ipynb` | `outputs/metrics/day6_threshold_metrics.csv` | 否 | `python scripts/04_evaluate_thresholds.py` | Day6 阈值网格是历史敏感性观察，不作为最终主结果。 |
| `notebooks/archive/07_risk_level_and_business_summary.ipynb` | `outputs/tables/day7_maintenance_priority_list.csv` | 否 | `python scripts/05_build_risk_tables.py` | Day7 大型维修优先级明细本地保留。 |
| `notebooks/archive/08_validation_model_selection.ipynb` | `outputs/metrics/validation_threshold_metrics.csv`、`outputs/predictions/validation_predictions.csv` | 否 | `python scripts/06_validation_model_selection.py` | validation 阶段过程明细可再生成。 |
| `notebooks/archive/09_feature_ablation_experiments.ipynb` | `outputs/metrics/feature_ablation_valid_threshold_metrics.csv` | 否 | `python scripts/07_feature_ablation_experiments.py` | 特征消融完整 threshold grid 本地保留。 |
| `notebooks/archive/11_prefix_group_signal_analysis.ipynb` | `outputs/metrics/day11_*`、`outputs/tables/day11_*`、`outputs/figures/day11_*` | 是 | `python scripts/09_prefix_group_analysis.py` | 前缀组结构信号分析保留为结构特征设计依据。 |
| `notebooks/archive/12_structural_feature_design.ipynb` | `outputs/tables/day12_structural_feature_design_table.csv` | 是 | `python scripts/10_build_structural_feature_design.py` | 记录结构特征方案设计，不训练模型。 |
| `notebooks/archive/13_structural_feature_valid_experiments.ipynb` | `outputs/metrics/day13_structural_feature_valid_threshold_metrics.csv` | 否 | `python scripts/11_structural_feature_valid_experiments.py` | Day13 valid 完整阈值网格本地保留。 |
| `notebooks/archive/15_xgb_tuning_valid_experiments.ipynb` | `outputs/metrics/day15_xgb_tuning_valid_trial_results.csv`、`outputs/metrics/day15_xgb_tuning_valid_threshold_metrics.csv` | 否 | `python scripts/13_xgb_tuning_valid_experiments.py` | 调参 trial 和完整 threshold grid 本地保留。 |
| `notebooks/archive/16_xgb_tuning_test_evaluation.ipynb` | `outputs/predictions/day16_xgb_tuning_test_predictions.csv`、Day16 summary tables | 预测明细否，summary 是 | `python scripts/14_xgb_tuning_test_evaluation.py` | 用于说明 tuned 方案没有泛化。 |
| `notebooks/archive/17_oof_recall_floor_bin_projection.ipynb` | `outputs/predictions/day17_oof_*.csv`、`outputs/metrics/day17_oof_threshold_metrics.csv` | 否 | `python scripts/15_oof_recall_floor_bin_projection.py` | OOF raw/averaged predictions 和完整 threshold grid 本地保留。 |
| `notebooks/archive/18_oof_probability_ensemble.ipynb` | `outputs/predictions/day18_oof_*.csv`、`outputs/metrics/day18_oof_*threshold_metrics.csv`、Day18 summary/overlap tables | 预测明细和 threshold grid 否，summary/overlap 多数保留 | `python scripts/16_oof_probability_ensemble.py` | OOF ensemble 用于稳健性检查，不作为最终 official test 候选。 |
| `notebooks/archive/19_sql_business_analysis.ipynb` | `outputs/sql_exports/*.csv`、`outputs/predictions/day14_structural_feature_test_predictions.csv` | SQL exports 是，预测明细否 | `python scripts/17_prepare_sql_business_tables.py` | SQL exports 继续上传；Day14 样本级预测明细本地保留，可由脚本再生成。 |

## 4. 结论

- 最终展示主线已经集中到 `notebooks/final/`，历史过程集中到 `notebooks/archive/`。
- `notebooks/final/20_sql_business_insights_and_visualization.ipynb` 和 `notebooks/final/21_model_interpretability.ipynb` 依赖的 final tables、final figures 与 sql exports 继续上传 GitHub。
- 大型预测明细、threshold grid、trial results 和 OOF 明细不再作为 GitHub 展示资产；需要复查时按表中脚本在本地重新生成。
- 本轮没有删除本地实验产物，没有移动 README 引用的 final figures，也没有修改 `data/raw/`。
