# README Presentation Audit for Day22

本审计不重写 README，只为 Day22 最终 README 改版提供具体方案。

## 1. 当前 README 主要问题

- 核心结果仍容易让读者先看到 Day6 test 回溯的 8640，应该把它移到 historical / sensitivity observation。
- Day14 final candidate 的主结果已经补充，但还需要在 README 顶部形成唯一主结果块。
- Day20 final figures 已插入 preview，但最终 README 需要把图放到对应业务章节，而不是集中堆放。
- 早期表格和历史过程较长，阅读路径偏 day-by-day 日志，面试官不一定能快速抓住最终结论。
- 失败实验和未采纳方案需要更清晰地集中说明，例如 Day16 tuned 未泛化、Day18 ensemble 未通过 OOF 筛选。
- How to Run 目前偏早期脚本，需要补一个简洁版主线入口。
- 缺少最终目录导航：数据、配置、脚本、notebooks、reports、outputs 分别看哪里。

## 2. 与 jvirico README 的差距

- 对方 README 的 problem definition 更靠前，读者能更快知道业务目标和成本函数。
- process structure 更清晰，不只是按日期堆过程。
- 每个实验阶段有 conclusions / notes，便于判断为什么采用或放弃某个方法。
- 图片嵌入在对应章节，而不是只在输出目录说明里出现。
- 最终采用方案与尝试过但未采用的方法边界更清楚。

## 3. Day22 README 建议结构

1. Project Overview
2. Business Problem
3. Dataset & Cost Setting
4. Final Result
5. Why Not Accuracy
6. Methodology
7. Key Experiments and Model Selection Discipline
8. Business Insights
9. Interpretability
10. SQL Analysis
11. How to Run
12. Project Structure
13. Limitations
14. Resume Highlights

## 4. README 图表放置建议

- Final Result：`outputs/figures/final/final_cost_policy_comparison.png`
- Business Insights：`outputs/figures/final/final_topk_maintenance_capacity.png`
- Business Insights：`outputs/figures/final/final_risk_level_workload.png`
- Business Insights：`outputs/figures/final/final_decile_lift_gain.png`
- Threshold Strategy：`outputs/figures/final/final_threshold_sensitivity.png`
- Interpretability：`outputs/figures/final/final_shap_bar_top20.png`
- Interpretability：`outputs/figures/final/final_feature_family_importance.png`

## 5. OOF / Ensemble 应如何写

- 不放在核心结果。
- 放在 robustness checks。
- 写清楚：OOF ensemble 最低 cost 略有下降，但 FN 增加，不符合补漏目标。
- 因此 Day18 未进入 official test。
- 不要把 OOF cost 与 official test cost 直接横向比较。

## 6. 需要删除或迁移的内容

- Day6 回溯结果从核心位置移走，迁移到 historical sensitivity observation。
- 大量过程表格移到 `reports/summary.md`。
- Notebook 列表不要占 README 过多空间，只保留主线 notebook 和完整索引链接。
- 中间 outputs 不要全部放 README，详细清单保留在 `outputs/README_outputs.md`。
- raw data 是否应从 Git tracking 中移除，留到 Day22 cleanup 处理；如保留，需说明数据来源和文件大小。
