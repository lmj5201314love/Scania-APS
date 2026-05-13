# 结构特征方案设计

## 1. 设计背景

前面几轮实验显示，单纯替换缺失值处理方式带来的提升有限，但缺失模式、零值模式和部分匿名字段结构确实存在统计信号。Day 10 的字段级分布诊断发现，Scania APS 数据中存在明显高缺失、高零值、偏态和长尾现象；Day 11 的前缀组分析进一步发现，真正适合做多字段前缀聚合的组主要是 `ag`、`ay`、`az`、`ba`、`cn`、`cs`、`ee`。

因此 Day 12 的重点不是继续训练模型，而是把这些结构信号整理成可执行的结构特征方案，为 Day 13 的实验做准备。

需要强调：Scania APS 字段是匿名字段，字段名和字段前缀不能解释为具体传感器、部件或物理含义。本文档中的前缀组只表示脱敏字段命名中的统计结构线索。

## 2. 设计原则

- 所有字段筛选、分位数阈值、前缀候选和 indicator 候选规则都只能在 `train_inner` 上 fit。
- `valid` 用于选择结构特征方案、模型和阈值。
- `official test` 只用于最终评估，不能反向筛选特征。
- 不使用 test 分布结果决定结构特征是否保留。
- 成本敏感指标仍然是核心，后续评估应关注 recall、F2、PR-AUC 和 total cost。
- Day 12 只做方案设计，不训练模型、不生成 processed 特征矩阵、不做阈值分析。

## 3. 特征家族 A：样本级缺失统计

设计特征：

- `sample_missing_count`
- `sample_missing_rate`
- `sample_non_missing_count`

解释：

- 表示单个样本整体数据完整性。
- 不依赖具体字段的物理含义。
- 用于验证“缺失规模”是否是 APS 故障风险信号。

实现原则：

- 统计字段集合只能来自训练流程中的数值字段列表。
- 对 train/valid/test 采用同一字段集合 transform。

## 4. 特征家族 B：样本级零值统计

设计特征：

- `sample_zero_count`
- `sample_zero_rate`
- `sample_non_zero_count`

解释：

- Day 10 发现大量字段零值率较高。
- 零值模式可能是匿名传感器数据中的结构信号。
- 是否有效必须在 Day 13 用 valid 验证。

实现原则：

- 零值定义使用 `value == 0`。
- 统计字段集合必须来自 train_inner schema，并应用到 valid/test。

## 5. 特征家族 C：前缀组缺失聚合

候选前缀：

- 高优先级：`ag`、`ay`、`cn`
- 中优先级：`az`、`cs`
- 低优先级：`ba`、`ee`

设计特征：

- `prefix_ag_missing_count`
- `prefix_ag_missing_rate`
- `prefix_ay_missing_count`
- `prefix_ay_missing_rate`
- 其他候选组类似。

说明：

- 前缀只作为匿名字段组线索。
- `ag`、`ay`、`cn` 优先级更高。
- `ba`、`ee` 当前组内信号较弱，低优先级观察。

实现原则：

- prefix membership 来自 train_inner schema 或 Day 11 成员表。
- 对 valid/test 使用同一 prefix -> feature list。

## 6. 特征家族 D：前缀组零值聚合

候选前缀：

- `ag`
- `ay`
- `cn`
- `az`
- `cs`

设计特征：

- `prefix_ag_zero_count`
- `prefix_ag_zero_rate`
- `prefix_ay_zero_count`
- `prefix_ay_zero_rate`
- `prefix_cn_zero_count`
- `prefix_cn_zero_rate`

说明：

- Day 11 显示 `ay`、`ag`、`cn` 的零值结构更明显。
- 这是 Day 13 第一轮重点验证方向。

实现原则：

- 零值定义保持为 `value == 0`。
- 分母使用该 prefix 组内字段数量。

## 7. 特征家族 E：筛选后的 missing indicators

候选来源：

- `br_000`
- `bq_000`
- `bp_000`
- `bo_000`
- `bn_000`
- 以及 Day 10 pos/neg 缺失率差异 Top 字段。

筛选原则：

- 只基于 train_inner 计算字段缺失率和 pos/neg 缺失差异。
- 候选字段应满足：
  - `missing_rate >= 0.01`
  - `abs(pos_missing_rate - neg_missing_rate) >= 0.10`
- 具体阈值写入 `config/structural_features.yaml`，Day 13 可以微调，但必须只基于 train_inner/valid。

设计特征：

- `missing_br_000`
- `missing_bq_000`
- `missing_bp_000`
- 其他满足筛选规则的字段类似。

风险：

- 单字段 indicator 可能过拟合，必须用 validation 验证。

## 8. 特征家族 F：可选异常 / 长尾统计

候选特征：

- `sample_outlier_count_p99`
- `sample_outlier_rate_p99`
- `prefix_az_outlier_count`
- `prefix_cs_outlier_count`

说明：

- Day 10 发现若干字段偏态和长尾明显。
- 异常阈值必须只从 train_inner 分位数计算。
- Day 13 第一轮可以暂不做，作为第二轮结构特征实验备选。

## 9. Day 13 实验优先级

第一轮建议只做：

- baseline：`median_all`
- A：`median_all + sample_missing_summary`
- B：`median_all + sample_zero_summary`
- C：`median_all + prefix_missing_summary`
- D：`median_all + prefix_zero_summary`
- E：`median_all + selected_missing_indicators`
- F：`median_all + A+B+C+D+E`

暂不做：

- PCA
- SVM
- 大规模 GridSearch
- SHAP
- official test 反向筛选
- 直接生成复杂异常特征作为第一轮主线

## 10. 局限

- 字段匿名，不能解释真实传感器含义。
- 前缀组只是脱敏字段命名结构，不一定对应真实系统分组。
- 结构特征可能增加噪声，必须通过 valid 验证。
- official test 只能用于最终评估，不能用于筛选结构特征方案。
