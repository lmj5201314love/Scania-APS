# Scania APS 预测性维护项目

## 项目概述

本项目基于 Scania APS 重卡空气压力系统故障数据集，构建面向制造业/工业数据分析场景的预测性维护分析流程。目标不是单纯追求模型分数，而是结合真实工业数据中的缺失值、类别极不平衡和误判成本差异，输出维修优先级和风险分层建议。

APS 系统相关故障如果被漏掉，可能导致车辆 breakdown、停机和更高维修成本；误报则主要带来不必要检查。项目采用数据集给定的业务成本设定：False Positive = 10，False Negative = 500。代码中的成本参数统一从 `config/config.yaml` 读取。

## 核心结果

当前候选方案来自测试集回溯分析：

```text
XGBoost + median_all + threshold 0.20
precision = 0.4692
recall = 0.9760
F2 = 0.8026
FP = 414
FN = 9
total cost = 8640
```

这不是生产环境最终阈值。更严谨的生产流程应使用验证集选择阈值，再在测试集上做最终评估。

| 方案 | 阈值 | Precision | Recall | F2 | FP | FN | Total Cost |
|---|---:|---:|---:|---:|---:|---:|---:|
| Naive baseline，全预测 neg | - | 0.0000 | 0.0000 | 0.0000 | 0 | 375 | 187500 |
| Logistic + drop_high_missing_median | 0.50 | 0.4860 | 0.9280 | 0.7852 | 368 | 27 | 17180 |
| XGBoost + median_all 默认阈值 | 0.50 | 0.6357 | 0.9120 | 0.8391 | 196 | 33 | 18460 |
| XGBoost + median_all 低成本阈值 | 0.20 | 0.4692 | 0.9760 | 0.8026 | 414 | 9 | 8640 |

## 业务成本对比

Naive baseline 将全部样本预测为 `neg`，会漏掉全部 375 个 APS 故障样本，total cost 为 187,500。

当前候选方案将 FN 降到 9，虽然 FP 增加到 414，但由于 FN 成本远高于 FP，总成本降到 8,640：

```text
cost_reduction = 187500 - 8640 = 178860
cost_reduction_rate = 95.39%
```

## 阈值优化结果

默认 0.5 阈值不一定适合 APS 成本场景。Day 6 基于已有预测概率做阈值敏感性分析，发现 XGBoost + `median_all` 在阈值 0.20 下总成本最低。

这说明模型的概率排序能力需要通过业务成本阈值转化为维修决策，而不是直接使用默认阈值。

## 风险分层和维修建议

基于 XGBoost + `median_all` 的预测概率和 Day 6 回溯分析阈值 0.20，当前项目将测试集样本划分为四类：

| Risk Level | 车辆数 | 实际 APS 故障数 | TP | FP | FN | TN | 建议动作 |
|---|---:|---:|---:|---:|---:|---:|---|
| Critical | 411 | 324 | 324 | 87 | 0 | 0 | 立即检修 |
| High | 369 | 42 | 42 | 327 | 0 | 0 | 优先检修 |
| Medium | 415 | 6 | 0 | 0 | 6 | 409 | 观察复查 |
| Low | 14805 | 3 | 0 | 0 | 3 | 14802 | 暂不处理 |

风险分层的作用是把模型概率转化为维修资源排序：高风险车辆优先进入检查队列，低风险车辆暂缓处理，中间风险车辆用于观察复查。

## Key Findings

1. 默认 0.5 阈值不适合 APS 成本场景。FN 成本远高于 FP，降低阈值可以显著减少漏报并降低 total cost。
2. XGBoost 的 PR-AUC 高于 Logistic baseline，说明概率排序能力更好；通过阈值调整，这种排序能力可以转化为更低业务成本。
3. 高缺失字段不能只按缺失率机械删除。Day 4/Day 5 对比显示，缺失处理策略需要结合模型表现和业务成本验证。
4. accuracy 不适合作为核心指标。类别极不平衡下，全预测多数类也可能看似稳定，但会漏掉关键故障样本。

## 项目阶段

- Day 1：项目初始化与业务理解。
- Day 2：基础数据质量与缺失值分析。
- Day 3：SQL 数据质量分析支持。
- Day 4：Dummy / Logistic baseline。
- Day 5：Random Forest / XGBoost 提升模型对比。
- Day 6：阈值成本敏感性分析。
- Day 7：风险分层、维修优先级建议和项目交付整理。

## 技术栈

- Python：pandas、numpy、scikit-learn、xgboost
- 可视化：matplotlib、seaborn
- SQL：MySQL 分析脚本
- 配置：PyYAML、python-dotenv
- 项目结构：`src/` 模块化代码、`scripts/` 可执行脚本、`notebooks/` 分析过程、`reports/` 交付文档

## 如何运行

1. 安装依赖：

```powershell
pip install -r requirements.txt
```

2. 运行 baseline：

```powershell
python scripts/02_train_baseline.py
```

3. 运行提升模型：

```powershell
python scripts/03_train_advanced_models.py
```

4. 运行阈值成本分析：

```powershell
python scripts/04_evaluate_thresholds.py
```

5. 生成风险分层和维修优先级表：

```powershell
python scripts/05_export_predictions_to_mysql.py
```

主要输出：

- `outputs/metrics/day6_best_threshold_summary.csv`
- `outputs/tables/day7_maintenance_priority_list.csv`
- `outputs/tables/day7_risk_level_summary.csv`
- `outputs/tables/day7_business_result_summary.csv`

## 项目局限

1. 数据集较老，不能代表当前车队传感器系统的最新状态。
2. 特征已匿名，无法解释具体传感器或部件的物理含义。
3. 数据没有时间戳，无法构建真实时序预测或提前预警窗口。
4. 当前阈值来自测试集回溯敏感性分析，不是生产环境最终阈值。
5. 缺少真实车辆 ID、维修记录和生产环境验证，无法直接评估上线效果。

## 简历表达建议

> Scania APS 预测性维护项目：基于 60,000 条训练样本和 16,000 条测试样本，处理高维匿名工业特征、结构性缺失和极度类别不平衡问题；构建 Logistic / Random Forest / XGBoost 模型，并基于 FP=10、FN=500 的业务成本进行阈值优化，将测试集回溯 total cost 从 naive baseline 的 187,500 降至 8,640，同时输出风险分层和维修优先级建议。
