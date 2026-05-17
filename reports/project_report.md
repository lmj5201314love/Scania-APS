# Scania APS 预测性维护项目报告

## 1. 项目背景

本项目使用 Scania APS 重卡空气压力系统故障数据集，模拟制造业和车队运维中的预测性维护问题。业务目标不是简单判断样本属于 `pos` 或 `neg`，而是将模型结果转化为维修优先级和风险分层建议，帮助有限维修资源优先处理高风险车辆。

在该业务中，误报会带来不必要检查，漏报则可能导致车辆 breakdown、停机和更高维修成本。因此项目采用成本敏感评估：FP 成本为 10，FN 成本为 500。代码中成本参数统一从 `config/config.yaml` 读取。

## 2. 数据问题

Scania APS 数据集具有典型工业数据特征：

- 训练集 60,000 行，测试集 16,000 行。
- 除标签列外包含 170 个匿名数值特征。
- 原始数据中 `"na"` 表示缺失值。
- 正类 `pos` 极少，训练集正类占比约 1.67%，测试集正类占比约 2.34%。
- 特征匿名，无法解释具体传感器物理含义。
- 缺失值具有结构性，pos/neg 缺失模式存在明显差异。

这些问题决定了项目不能以 accuracy 作为核心指标，而应关注 recall、F2、PR-AUC 和 total cost。

## 3. 方法流程

项目按阶段推进：

1. Day 1：业务理解和项目初始化。
2. Day 2：数据质量、缺失值和标签分布分析。
3. Day 3：SQL 数据质量分析支持。
4. Day 4：Dummy / Logistic baseline。
5. Day 5：Random Forest / XGBoost 提升模型对比。
6. Day 6：阈值成本敏感性分析。
7. Day 7：风险分层、维修优先级建议和交付文档整理。
8. Enhancement：validation-based model selection。

## 4. 缺失值处理策略

项目初始阶段没有直接删除高缺失字段，而是保留可验证空间。Day 4 / Day 5 主要比较：

- `median_all`：保留全部特征，使用训练集 median 填充。
- `drop_high_missing_median`：仅基于训练集识别缺失率大于等于 80% 的字段，删除后再做 median 填充。
- `median_with_indicator`：加入缺失指示变量，主要用于部分模型对比。

缺失值处理规则只在训练侧拟合，再应用到验证集或测试集，避免数据泄漏。

## 5. 模型对比

默认阈值 0.5 下，Day 4 / Day 5 的主要结果包括：

- Dummy baseline 漏报全部 375 个测试集正类，total cost = 187,500。
- Logistic + `drop_high_missing_median`：recall = 0.9280，FN = 27，total cost = 17,180。
- XGBoost + `median_all`：PR-AUC 更高，说明概率排序能力更好，但默认阈值下 total cost = 18,460，不一定成本最低。

这说明模型概率排序能力和最终业务成本之间需要通过阈值选择连接起来。

## 6. 阈值成本分析

Day 6 不重新训练模型，只读取已有预测概率，对阈值 0.01 到 0.99 做测试集回溯敏感性分析。

最低成本组合为：

| 方案 | 阈值 | Precision | Recall | F2 | FP | FN | Total Cost |
|---|---:|---:|---:|---:|---:|---:|---:|
| XGBoost + median_all | 0.20 | 0.4692 | 0.9760 | 0.8026 | 414 | 9 | 8640 |

与默认阈值 0.5 相比，阈值 0.20 的 FP 从 196 增加到 414，但 FN 从 33 降到 9。由于 FN 成本远高于 FP，total cost 从 18,460 降到 8,640。

需要强调：Day 6 结果属于测试集回溯敏感性分析，不是生产环境最终阈值。

## 7. 风险分层

基于 XGBoost + `median_all` 的预测概率和阈值 0.20，Day 7 输出四级风险分层：

| Risk Level | 车辆数 | 实际 APS 故障数 | TP | FP | FN | TN | 建议动作 |
|---|---:|---:|---:|---:|---:|---:|---|
| Critical | 411 | 324 | 324 | 87 | 0 | 0 | 立即检修 |
| High | 369 | 42 | 42 | 327 | 0 | 0 | 优先检修 |
| Medium | 415 | 6 | 0 | 0 | 6 | 409 | 观察复查 |
| Low | 14805 | 3 | 0 | 0 | 3 | 14802 | 暂不处理 |

风险分层将概率输出转化为维修队列，使维修团队可以优先处理 Critical 和 High 样本。

## 8. 严谨性增强：Validation-based selection

Day 6 / Day 7 的阈值来自官方 test 上的回溯敏感性分析。为了降低测试集回溯选择阈值带来的乐观偏差，本轮增强从官方 training set 中划分出 `train_inner` 和 `valid`：

| dataset | row_count | pos_count | neg_count | pos_rate |
|---|---:|---:|---:|---:|
| official_train | 60000 | 1000 | 59000 | 0.0167 |
| train_inner | 48000 | 800 | 47200 | 0.0167 |
| valid | 12000 | 200 | 11800 | 0.0167 |

流程为：在 `train_inner` 上训练 Logistic Regression 和 XGBoost，在 `valid` 上选择模型、缺失处理策略和阈值，最后在 official test 上只做一次最终评估。

valid 上的最佳组合为：

```text
XGBoost + drop_high_missing_median + threshold 0.14
```

official test 最终评估结果为：

| 选择方式 | 模型 | 缺失策略 | 阈值 | Precision | Recall | F2 | FP | FN | Total Cost |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| valid 选择后 test 评估 | XGBoost | drop_high_missing_median | 0.14 | 0.4370 | 0.9707 | 0.7801 | 469 | 11 | 10190 |
| Day 6 test 回溯最优 | XGBoost | median_all | 0.20 | 0.4692 | 0.9760 | 0.8026 | 414 | 9 | 8640 |

相比 Day 6 test 回溯最优，valid-based 流程在 official test 上 total cost 高出 1,550，FP 增加 55，FN 增加 2。这说明 Day 6 结果存在一定测试集回溯乐观偏差；同时，valid 选择出的 XGBoost 方案仍然保持较高 recall 和较低业务成本，整体方向是稳定的。

## 9. 缺失值与特征工程消融实验

在 validation-based 流程基础上，本轮进一步比较缺失值处理和基础特征工程策略。实验仍然只在 `valid` 上选择策略和阈值，official test 只用于最终评估，避免用测试集反向选择方案。

本轮覆盖的主要策略包括：

- `median_all`：保留全部字段并做 median 填充。
- `drop_80_missing_median`：删除 train_inner 中缺失率大于等于 80% 的字段。
- `drop_50_missing_median`：删除 train_inner 中缺失率大于等于 50% 的字段。
- `median_with_indicator`：median 填充并加入缺失指示变量。
- `xgb_native_missing`：仅用于 XGBoost，保留 NaN，由模型原生处理缺失。
- `missing_indicator_only`：只使用每个字段是否缺失的 0/1 指示变量。
- `low_variance_filter`、`high_correlation_filter`、`l1_feature_selection`：基础特征筛选对照实验。

关键结果如下：

| 策略 | 模型 | valid best threshold | official test total cost | Recall | F2 | FP | FN | 结论 |
|---|---|---:|---:|---:|---:|---:|---:|---|
| drop_50_missing_median | XGBoost | 0.14 | 10820 | 0.9680 | 0.7740 | 482 | 12 | valid 成本最低，但 test 不如 drop_80 稳定 |
| drop_80_missing_median | XGBoost | 0.14 | 10190 | 0.9707 | 0.7801 | 469 | 11 | 删除极高缺失字段较稳，是 validation 基准方案 |
| median_all | XGBoost | 0.16 | 10820 | 0.9653 | 0.7890 | 432 | 13 | 保留全部字段表现稳定，但成本不最低 |
| median_with_indicator | XGBoost | 0.10 | 10060 | 0.9760 | 0.7556 | 556 | 9 | test 观察成本最低，说明缺失指示有信息 |
| xgb_native_missing | XGBoost | 0.18 | 11180 | 0.9600 | 0.8079 | 368 | 15 | F2 和 precision 较好，但 FN 增加导致成本不占优 |
| missing_indicator_only | XGBoost | 0.78 | 27570 | 0.8987 | 0.6255 | 857 | 38 | 缺失模式有信号，但不能单独替代原始数值 |
| high_correlation_filter | XGBoost | 0.13 | 12410 | 0.9600 | 0.7656 | 491 | 15 | 当前不建议作为主线 |
| l1_feature_selection | Logistic | 0.35 | 16780 | 0.9360 | 0.7535 | 478 | 24 | 可作线性模型解释辅助，但不是最优 |

本轮最重要的结论不是“某个复杂策略一定更好”，而是：

1. `missing_indicator_only` 的 AP 明显高于正类基准率，说明缺失模式本身确实携带预测信号。
2. `median_with_indicator` 在 official test 观察中成本最低，但由于 test 不参与策略选择，只能把它视为值得后续验证的方向，而不是最终方案。
3. `drop_50_missing_median` 在 valid 上 total cost 最低，但 official test 上不如 `drop_80_missing_median` 稳定，说明高缺失字段不能只凭缺失率机械删除。
4. `xgb_native_missing` 没有在 total cost 上胜出，但 F2 较高，可以在后续轻量调参中继续保留观察。
5. 高相关过滤和 L1 特征选择有助于理解特征冗余或线性模型行为，但当前不适合作为主线方案。

## 10. 字段级分布诊断

Day 10 不做建模和调参，而是对 170 个匿名数值字段进行分布诊断，目的是为后续结构特征设计提供依据。本轮输出了字段级分布统计、缺失/零值统计、pos/neg 分布差异、train/valid/test 漂移统计和 Top 诊断清单。

核心观察如下：

- 高缺失字段集中在 `br_000`、`bq_000`、`bp_000`、`bo_000`、`ab_000`、`cr_000`、`bn_000`、`bm_000`。其中 train_inner 中缺失率大于等于 50% 的字段有 8 个，大于等于 80% 的字段有 2 个。
- 高零值字段非常明显。train_inner 中零值率大于等于 90% 的字段有 29 个，大于等于 50% 的字段有 53 个；Top 字段包括 `as_000`、`au_000`、`ag_000`、`ay_009`、`ay_000`、`ag_001`。
- 多个字段偏态和长尾极端，例如 `cs_009`、`cf_000`、`co_000`、`ad_000`、`dh_000`。这解释了为什么均值类处理不稳，也支持继续使用中位数填充、树模型或稳健缩放。
- pos/neg 缺失率差异最大的字段仍然集中在高缺失字段，例如 `br_000`、`bq_000`、`bp_000`、`bo_000`、`bn_000`。这与前面“缺失模式存在预测信号”的结论一致。
- pos/neg 数值分布差异明显的字段包括 `ah_000`、`bg_000`、`ci_000`、`bu_000`、`cq_000`、`bv_000`、`bb_000`、`an_000`。这些只能被解释为匿名字段上的统计差异，不能虚构具体传感器物理含义。
- train/test 缺失率差异整体较小，最大缺失率差异约为 0.5 个百分点；但 `eb_000`、`du_000`、`bu_000`、`bv_000`、`cq_000` 等字段的 p99 差异较大，说明长尾字段存在一定泛化风险。

这些观察支持后续做结构特征设计，例如样本级缺失计数、零值计数、前缀组统计、长尾截断或稳健变换对照。不过这些特征设计必须继续遵守 validation-based 流程：结构特征和阈值在 valid 上选择，official test 只用于最终评估。

## 11. 前缀组结构信号分析

Day 11 在 Day 10 字段级诊断基础上，进一步按字段名前缀进行匿名结构分组分析。前缀只作为统计结构线索，不代表任何具体传感器或部件含义。

本轮共识别出 107 个字段前缀组，其中 100 个是单字段前缀，真正包含多个字段、适合做“前缀组聚合”的只有 7 组：

| prefix | feature_count | avg_missing_rate | avg_zero_rate | avg_abs_pos_neg_zero_diff | avg_abs_skew |
|---|---:|---:|---:|---:|---:|
| ag | 10 | 0.0110 | 0.5117 | 0.2266 | 47.6380 |
| ay | 10 | 0.0109 | 0.6809 | 0.0861 | 53.4566 |
| cn | 10 | 0.0112 | 0.3277 | 0.2049 | 30.6079 |
| az | 10 | 0.0109 | 0.2881 | 0.0861 | 59.0042 |
| cs | 10 | 0.0109 | 0.1395 | 0.0559 | 60.8494 |
| ba | 10 | 0.0113 | 0.1358 | 0.0953 | 18.7601 |
| ee | 10 | 0.0109 | 0.1186 | 0.0482 | 15.5997 |

平均缺失率最高的前缀组主要是单字段前缀，例如 `br`、`bq`、`bp`、`bo`、`cr`、`ab`、`bn`、`bm`。这些字段缺失信号强，但不适合作为前缀组聚合主线，更适合在单字段缺失指示或稳健处理时观察。

平均零值率最高的前缀组同样多为单字段前缀，例如 `as`、`au`、`ef`、`dz`、`eg`。多字段组中，`ay` 的平均零值率最高，`ag` 次之，说明它们适合进入 Day 12 的组内 zero-count / zero-rate 候选。

pos/neg 缺失率差异最高的前缀组仍然集中在单字段高缺失字段，例如 `br`、`bq`、`bp`、`bo`、`bn`。pos/neg 零值差异较高的单字段前缀包括 `ai`、`al`、`am`、`ar`、`df`。多字段组中，`ag` 和 `cn` 的平均 pos/neg 零值差异相对更明显。

train/test drift 风险较高的前缀包括 `cl`、`du`、`ec`、`dq`、`ed` 等，多数也是单字段前缀；多字段组整体 drift 风险处于中等水平。后续如果使用 `ay`、`ag`、`cn`、`az`、`cs` 等组聚合特征，仍需在 validation 流程中验证，official test 只做最终评估。

Day 12 建议优先观察：

1. `ag`：零值率较高，pos/neg 零值差异相对明显。
2. `ay`：平均零值率最高，偏态明显。
3. `cn`：零值率和 pos/neg 零值差异较明显。
4. `az`、`cs`：偏态较高，可作为长尾结构候选。
5. `ba`、`ee`：组内信号较弱，作为低优先级备选。

## 12. 结构特征方案设计

Day 12 不训练模型，也不生成 processed 特征矩阵，而是把 Day 10 / Day 11 的结构信号整理为可执行的结构特征方案。设计结果写入 `docs/structural_feature_design.md`、`config/structural_features.yaml` 和 `outputs/tables/day12_structural_feature_design_table.csv`。

本轮设计了六类结构特征家族：

1. 样本级缺失统计：`sample_missing_count`、`sample_missing_rate`、`sample_non_missing_count`。
2. 样本级零值统计：`sample_zero_count`、`sample_zero_rate`、`sample_non_zero_count`。
3. 前缀组缺失聚合：对 `ag`、`ay`、`cn`、`az`、`cs`、`ba`、`ee` 生成 prefix missing count/rate。
4. 前缀组零值聚合：重点对 `ag`、`ay`、`cn`、`az`、`cs` 生成 prefix zero count/rate。
5. 筛选后的 missing indicators：只基于 train_inner 的缺失率和 pos/neg 缺失率差异筛选候选字段。
6. 可选异常/长尾统计：例如 p99 outlier count/rate，暂不进入 Day 13 第一轮。

结构特征设计表共 64 行，其中 60 行进入 Day 13 第一轮，4 行异常/长尾统计作为第二轮备选。设计表中 selected missing indicators 候选数为 30，Top 字段包括 `br_000`、`bq_000`、`bp_000`、`bo_000`、`bn_000`、`bm_000`、`di_000`、`dh_000`、`dj_000`、`dk_000`。

Day 13 第一轮建议实验矩阵为：

- `median_all`
- `median_all_sample_missing`
- `median_all_sample_zero`
- `median_all_prefix_missing`
- `median_all_prefix_zero`
- `median_all_selected_missing_indicators`
- `median_all_structural_all`

暂不做 PCA、SVM、大规模 GridSearch、SHAP，也不使用 official test 反向筛选结构特征。所有字段列表、prefix membership、indicator 候选和异常阈值都必须只在 train_inner 上 fit，valid 用于选择方案和阈值，official test 只用于最终评估。

## 13. 业务建议

如果强调 Day 7 业务交付，可以继续展示 XGBoost + `median_all` + threshold 0.20 的风险分层结果，但必须说明其阈值来自测试集回溯分析。

如果强调方法严谨性，应优先引用 validation-based 流程下的候选方案：

```text
XGBoost + drop_high_missing_median + threshold 0.14
```

该方案在 official test 上 FN = 11、total cost = 10,190，虽然不如 test 回溯最优低，但更接近真实模型选择流程。

## 14. 项目局限

1. 数据集较老，不代表最新车辆系统。
2. 特征匿名，无法解释具体传感器物理含义。
3. 数据没有时间戳，无法构建真实时序预测。
4. Day 7 风险分层阈值来自测试集回溯敏感性分析，不是生产最终阈值。
5. validation-based 流程仍然是单次划分，尚未做时间切分或交叉验证。
6. 缺少真实车辆 ID、维修记录和生产环境验证。

## 15. 后续改进方向

- 引入时间窗口和车辆 ID，构建真实提前预警任务。
- 与维修容量结合，设计 Top-K 检修策略。
- 基于 Day 12 设计表实现结构特征实验，并坚持 train_inner/valid/test 的严格边界。
- 做轻量级调参，但阈值和参数选择必须基于 validation，而不是 official test。
- 补充模型解释，例如特征重要性和 SHAP，但不虚构匿名特征物理含义。

## 16. 结构特征 valid 实验

在 Day 12 完成结构特征方案设计后，项目进入 Day 13 第一轮结构特征实验。本轮不使用 official test，而是在 official training set 内部划分出的 `train_inner / valid` 上完成结构特征方案和阈值选择。

本轮实验收窄为 XGBoost + median_all 基线，并按结构信号来源分组验证：样本级缺失率、筛选后的 missing indicators、前缀组零值率、核心结构组合以及全部结构特征上限方案。实验结果显示，`median_all_structural_all` 在 valid 上成本最低，但由于特征数量最多，只能视为上限观察；`median_all_selected_missing_indicators_top30` 更窄、更适合进入 Day 14 做 official test 最终观察。

| 实验组 | valid best threshold | valid total cost | Recall | F2 | FP | FN | 解释 |
|---|---:|---:|---:|---:|---:|---:|---|
| baseline_median_all | 0.16 | 6460 | 0.9700 | 0.7239 | 346 | 6 | 不加结构特征 |
| median_all_sample_missing_rate | 0.15 | 6250 | 0.9750 | 0.7117 | 375 | 5 | 样本整体缺失程度有一定信号 |
| median_all_selected_missing_indicators_top30 | 0.30 | 6050 | 0.9650 | 0.7732 | 255 | 7 | 更窄的 missing indicator 候选方案 |
| median_all_prefix_zero_rate | 0.09 | 6240 | 0.9850 | 0.6696 | 474 | 3 | 前缀组零值率可减少 FN，但 FP 较高 |
| median_all_structural_core | 0.16 | 6540 | 0.9700 | 0.7196 | 354 | 6 | 核心结构组合暂未优于 baseline |
| median_all_structural_all | 0.18 | 5850 | 0.9750 | 0.7331 | 335 | 5 | 上限观察，需警惕冗余和过拟合 |

这些结果只代表 valid 阶段的候选结论。Day 14 应选择 `median_all_structural_all` 和 `median_all_selected_missing_indicators_top30` 进入 official test 最终观察，不能把 valid 最优方案直接写成最终方案。

