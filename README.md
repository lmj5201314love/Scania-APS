# Scania APS 预测性维护项目

本项目基于 Scania APS 重卡空气压力系统故障数据集，构建一个面向制造业/工业数据分析场景的预测性维护分析流程。

项目重点不是单纯追求分类分数，而是围绕真实工业数据问题展开：高维匿名特征、结构性缺失、极度类别不平衡，以及误报和漏报成本不对称。最终输出不仅包括模型结果，还包括阈值成本分析、风险分层和维修优先级建议。

## 业务背景

APS，即 Air Pressure System，空气压力系统，是重卡运行中的关键系统之一。APS 相关故障如果被漏报，可能导致车辆 breakdown、停机和更高维修成本；误报则主要带来额外检查和维修资源占用。

数据集给定的业务成本设定为：

- False Positive，误报成本：`10`
- False Negative，漏报成本：`500`

因此本项目不以 accuracy 作为核心指标，而重点关注：

- precision
- recall
- F1 / F2
- PR-AUC
- total cost

代码中的成本参数统一从 `config/config.yaml` 读取，避免在 Python 评估逻辑中写死业务参数。

## 核心结果

当前测试集回溯分析中的候选方案为：

```text
XGBoost + median_all + threshold 0.20
```

该方案不是生产环境最终阈值。更严谨的生产流程应使用验证集选择阈值，再在测试集上做最终评估。

| 方案 | 阈值 | Precision | Recall | F2 | FP | FN | Total Cost |
|---|---:|---:|---:|---:|---:|---:|---:|
| Naive baseline，全预测 neg | - | 0.0000 | 0.0000 | 0.0000 | 0 | 375 | 187500 |
| Logistic + drop_high_missing_median | 0.50 | 0.4860 | 0.9280 | 0.7852 | 368 | 27 | 17180 |
| XGBoost + median_all 默认阈值 | 0.50 | 0.6357 | 0.9120 | 0.8391 | 196 | 33 | 18460 |
| XGBoost + median_all 低成本阈值 | 0.20 | 0.4692 | 0.9760 | 0.8026 | 414 | 9 | 8640 |

相对 naive baseline，当前候选方案将 total cost 从 `187500` 降到 `8640`：

```text
cost_reduction = 178860
cost_reduction_rate = 95.39%
```

## 风险分层和维修建议

基于 XGBoost + `median_all` 的预测概率和 Day 6 回溯分析阈值 `0.20`，项目将测试集样本划分为四类风险等级：

| Risk Level | 车辆数 | 实际 APS 故障数 | TP | FP | FN | TN | 建议动作 |
|---|---:|---:|---:|---:|---:|---:|---|
| Critical | 411 | 324 | 324 | 87 | 0 | 0 | 立即检修 |
| High | 369 | 42 | 42 | 327 | 0 | 0 | 优先检修 |
| Medium | 415 | 6 | 0 | 0 | 6 | 409 | 观察复查 |
| Low | 14805 | 3 | 0 | 0 | 3 | 14802 | 暂不处理 |

风险分层的目的，是把模型概率转化为维修资源排序：高风险车辆优先进入检查队列，中等风险车辆复查观察，低风险车辆暂缓处理。

## Key Findings

1. 默认 `0.5` 阈值不适合 APS 成本场景。FN 成本远高于 FP，适当降低阈值可以显著减少漏报并降低 total cost。
2. XGBoost 的概率排序能力需要通过业务阈值转化为维修决策，而不是直接使用默认分类阈值。
3. 高缺失字段不能只按缺失率机械删除，需要结合模型表现和业务成本验证。
4. accuracy 不适合作为核心指标。类别极不平衡场景下，全预测多数类也可能看起来准确，但业务上会漏掉关键故障样本。

## 严谨性增强：Validation-based 阈值选择

原 Day 6 的阈值成本分析是在官方 test 预测概率上做回溯敏感性分析，适合解释“不同阈值会怎样影响成本”，但不适合作为严格的模型选择流程。

本轮增强从官方 training set 内部划分：

- `train_inner`：48,000 行，正类 800，负类 47,200。
- `valid`：12,000 行，正类 200，负类 11,800。
- `official test`：16,000 行，只用于最终评估。

validation 流程只在 `valid` 上选择模型、缺失处理策略和阈值，official test 不参与选择。

| 选择方式 | 模型 | 缺失策略 | 阈值 | Precision | Recall | F2 | FP | FN | Total Cost |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| valid 选择后 test 评估 | XGBoost | drop_high_missing_median | 0.14 | 0.4370 | 0.9707 | 0.7801 | 469 | 11 | 10190 |
| Day 6 test 回溯最优 | XGBoost | median_all | 0.20 | 0.4692 | 0.9760 | 0.8026 | 414 | 9 | 8640 |
| 差异 | - | - | - | -0.0323 | -0.0053 | -0.0225 | +55 | +2 | +1550 |

结果说明：valid-based 流程下 official test 成本从 Day 6 回溯最优的 `8640` 上升到 `10190`，说明原 test 回溯阈值存在一定乐观偏差；但 XGBoost 仍然保持高 recall 和较低 total cost，策略整体没有失效。

## 项目阶段

- Day 1：项目初始化与业务理解。
- Day 2：基础数据质量与缺失值分析。
- Day 3：SQL 数据质量分析支持。
- Day 4：Dummy / Logistic baseline。
- Day 5：Random Forest / XGBoost 提升模型对比。
- Day 6：阈值成本敏感性分析。
- Day 7：风险分层、维修优先级建议和项目交付整理。
- Cleanup：项目结构清理、空文件处理、SQL 成本说明和结构文档补充。
- Enhancement 1：Validation-based model selection，在 valid 上选择模型和阈值，再在 official test 上评估。

## 技术栈

- Python：pandas、numpy、scikit-learn、xgboost
- 可视化：matplotlib、seaborn
- SQL：MySQL 分析脚本
- 配置：PyYAML、python-dotenv
- 项目结构：`src/` 模块化代码、`scripts/` 可执行脚本、`notebooks/` 分析过程、`reports/` 交付文档

## 如何运行

安装依赖：

```powershell
pip install -r requirements.txt
```

运行 baseline：

```powershell
python scripts/02_train_baseline.py
```

运行提升模型：

```powershell
python scripts/03_train_advanced_models.py
```

运行阈值成本分析：

```powershell
python scripts/04_evaluate_thresholds.py
```

生成风险分层和维修优先级表：

```powershell
python scripts/05_build_risk_tables.py
```

运行 validation-based model selection：

```powershell
python scripts/06_validation_model_selection.py
```

主要输出：

- `outputs/metrics/day6_best_threshold_summary.csv`
- `outputs/metrics/final_test_evaluation_from_valid_selection.csv`
- `outputs/metrics/validation_vs_day6_backtest_compare.csv`
- `outputs/tables/day7_maintenance_priority_list.csv`
- `outputs/tables/day7_risk_level_summary.csv`
- `outputs/tables/day7_business_result_summary.csv`

## 项目结构

完整目录说明见：

```text
docs/project_structure.md
```

## 项目局限

1. 数据集较老，不能代表当前车辆传感器系统的最新状态。
2. 特征已经匿名化，无法解释具体传感器或部件的物理含义。
3. 数据没有时间戳，无法构建真实时序预测或提前预警窗口。
4. 当前低成本阈值来自测试集回溯敏感性分析，不是生产环境最终阈值。
5. 缺少真实车辆 ID、维修记录和生产环境验证，无法直接评估上线效果。

## 后续增强方向

1. 做缺失值策略和特征工程消融实验：`drop_50_missing_median`、`median_with_indicator`、`xgb_native_missing`、低方差过滤、高相关过滤和 L1 选择。
2. 做轻量级 XGBoost 调参，但避免把项目变成纯调参项目。
3. 深化 SQL 业务分析，例如 Top-K 检修容量、不同风险等级实际故障率和维修工作量评估。
4. 补充模型解释，例如特征重要性和 SHAP，但不虚构匿名特征的物理含义。

## 简历表达建议

> Scania APS 预测性维护项目：基于 60,000 条训练样本和 16,000 条测试样本，处理高维匿名工业特征、结构性缺失和极度类别不平衡问题；
> 构建 Logistic / Random Forest / XGBoost 模型，并基于 FP=10、FN=500 的业务成本进行阈值优化；
> 将测试集回溯 total cost 从 naive baseline 的 187,500 降至 8,640，同时输出风险分层和维修优先级建议。
