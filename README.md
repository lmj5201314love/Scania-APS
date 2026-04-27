# Scania APS 预测性维护项目

## 项目背景

本项目基于 Scania APS 重卡空气压力系统故障数据集，面向制造业和工业数据分析场景，目标是在真实工业数据条件下预测 APS 系统相关故障，并结合维修业务成本给出更合理的检修决策。

这不是一个单纯追求模型分数的分类练习。项目重点是理解工业故障数据中的高维特征、缺失值、类别极不平衡和误判成本差异，并把数据分析、SQL 质量检查、机器学习评估和维修优先级建议连接起来。

## 数据集说明

原始数据位于：

- `data/raw/aps_failure_training_set.csv`
- `data/raw/aps_failure_test_set.csv`

数据集包含 Scania 重卡运行过程中采集的匿名传感器和系统特征。字段名经过脱敏处理，标签字段为 `class`：

- `pos`：APS 系统相关故障，后续建模时映射为 `1`
- `neg`：非 APS 系统相关故障，后续建模时映射为 `0`

原始 CSV 中的 `"na"` 表示缺失值，读取时需要显式设置 `na_values="na"`。项目默认使用数据集官方提供的 train/test 划分，不在 Day 1 合并后重新切分。

## 业务问题

APS 系统故障如果没有被及时识别，可能导致车辆 breakdown、维修延迟和更高停机成本。另一方面，把正常车辆误判为 APS 故障也会带来不必要检查，但代价相对较低。

因此，本项目需要回答的问题不是“模型 accuracy 是否最高”，而是：

- 如何识别更可能发生 APS 故障的车辆；
- 如何在漏报和误报之间做业务上可解释的权衡；
- 如何根据预测概率输出风险分层和维修优先级；
- 如何用总业务成本衡量阈值选择是否合理。

## 项目目标

1. 完成 Scania APS 数据的业务理解和数据理解。
2. 分析缺失值、标签分布和类别不平衡问题。
3. 使用 SQL 支持数据质量分析和结果复核。
4. 构建基线模型和提升模型，但避免数据泄漏。
5. 使用 precision、recall、F1、F2、PR-AUC 和 total cost 评估模型。
6. 基于阈值优化输出维修优先级和风险分层建议。

## 成本敏感评估

本项目采用 Scania APS 数据集中的业务成本设定：

- False Positive，误报成本：`10`
- False Negative，漏报成本：`500`

总业务成本定义为：

```text
total_cost = FP * 10 + FN * 500
```

FN 成本远高于 FP，意味着漏掉真实 APS 故障比多做一次检查更严重。因此后续评估会重点关注 recall、F2、PR-AUC 和 total cost，而不是把 accuracy 作为核心目标。

## 技术栈

- Python：pandas、numpy、scikit-learn、xgboost
- 可视化：matplotlib、seaborn
- Notebook：Jupyter / Notebook
- SQL：MySQL、SQLAlchemy、PyMySQL
- 配置与复现：pyyaml、python-dotenv、joblib

## 项目目录结构

```text
scania_aps_predictive_maintenance/
├─ AGENTS.md
├─ README.md
├─ requirements.txt
├─ .gitignore
├─ .env.example
├─ config/
├─ data/
│  ├─ raw/
│  ├─ interim/
│  └─ processed/
├─ notebooks/
├─ sql/
├─ src/
├─ scripts/
├─ models/
├─ outputs/
├─ reports/
└─ tests/
```

## 当前阶段

当前处于 Day 1：项目初始化和业务理解。

本阶段只完成项目结构、基础说明、业务成本设定、原始数据路径确认和数据理解 notebook 骨架，不进行模型训练、调参、复杂清洗或特征工程。

## 后续计划

- Day 2：读取原始数据，完成字段规模、缺失值、标签分布和基础数据质量分析。
- Day 3：补充 SQL 数据质量分析，形成可复核的数据分析脚本。
- Day 4：建立 baseline 模型，明确不平衡分类的初始评估方式。
- Day 5：训练提升模型，并比较不同评估指标。
- Day 6：进行阈值优化和成本敏感评估。
- Day 7：整理项目报告、风险分层建议和简历表述。
