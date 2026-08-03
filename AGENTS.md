# Scania APS 项目协作规范

## 项目背景

本项目是面向制造业和工业数据分析方向的预测性维护项目，使用 Scania APS 重卡空气压力系统故障数据集。项目目标不是单纯追求分类分数，而是结合真实工业数据问题、业务误判成本和维修决策，输出可解释的风险分层和维修优先级建议。

## 数据说明

- 原始训练集：`data/raw/aps_failure_training_set.csv`
- 原始测试集：`data/raw/aps_failure_test_set.csv`
- 原始数据中的 `"na"` 表示缺失值，读取时使用 `na_values="na"`。
- 标签字段为 `class`。
- `class = "pos"` 表示 APS 系统相关故障，建模时映射为 `1`。
- `class = "neg"` 表示非 APS 系统相关故障，建模时映射为 `0`。

## 必须遵守

1. 不修改、覆盖、删除或重命名 `data/raw/` 下的原始数据文件。
2. 优先使用官方 train/test 划分，不把 train/test 合并后重新切分。
3. 所有缺失值填充、特征筛选、编码、标准化等规则只能在训练集上拟合，再应用到测试集，避免数据泄漏。
4. 不把真实 `.env`、数据库密码、大型 CSV、模型产物或运行输出提交到 Git。
5. 所有面向项目的注释、说明和报告优先使用中文。

## 成本设定

- False Positive，误报成本：`10`
- False Negative，漏报成本：`500`
- 总业务成本：`total_cost = FP * 10 + FN * 500`

FN 代表真实 APS 故障被漏掉，业务风险高于 FP。因此本项目不能以 accuracy 作为核心目标，应重点关注 precision、recall、F1、F2、PR-AUC 和 total cost。

## Python 编码规范

- 代码放在 `src/scania_aps/`，可执行流程放在 `scripts/`。
- 函数命名清晰，避免为了工程化而增加不必要抽象。
- 路径、成本参数和数据配置优先从 `config/config.yaml` 或环境变量读取。
- 只在必要位置添加中文注释，避免解释显而易见的代码。

## Notebook 规范

- Notebook 用于探索和记录分析过程，不在其中堆放复杂生产逻辑。
- 每个 notebook 应有清晰标题、目的、关键观察和阶段小结。
- Day 1 只做业务理解和数据读取骨架，不训练模型、不调参、不做复杂清洗。

## SQL 编写规范

- SQL 放在 `sql/` 目录，按编号顺序推进。
- SQL 用于数据导入检查、数据质量分析、标签分布、缺失情况、业务成本和模型结果复核。
- SQL 查询应保留必要中文注释，避免写入真实密码或本地私有连接信息。

## 建模阶段规范

- 建模从 baseline 开始，再进入 XGBoost 等提升模型。
- 不在测试集上选择阈值、拟合填充值或调参。
- 阈值选择必须结合 FP/FN 成本解释，不只报告模型分数。
- 输出结果应能服务风险分层和维修优先级建议。

## 当前阶段优先级

当前已完成 Day 1-21 的建模、SQL 业务分析、模型解释性、README 展示改版、outputs 清理、notebook 分层和 archive 归档说明，进入 Final Packaging Day 4.5：Final Notebook De-template Cleanup and Interview-oriented Narrative Repair 阶段。当前重点是只修复 `notebooks/final/` 的 Markdown 展示内容：不使用“分析目标 / 输入与输出 / 方法概述 / 关键结论 / 结果解释 / 注意事项”的六段式前置模板，而采用问题驱动叙事，把说明放到相关代码、表格和图表附近。`notebooks/archive/` 不需要处理，除非修复 final notebook 链接。final notebook 必须使用中文展示，保留必要英文技术名词；不写学习口吻、AI 协作痕迹或不确定表达，不把匿名字段解释成真实传感器或物理部件含义。本阶段不修改 code cell、不重新运行 notebook、不清空 outputs、不建模、不重新训练、不重新选择 threshold、不重新生成 outputs、不移动 README 引用的 final figures、不修改 raw 数据；`sample_id` 只能解释为匿名样本编号，不能说成真实车辆 ID。

## Agent skills

### Issue tracker

本项目使用 GitHub Issues 跟踪任务、缺陷和需求。详见 `docs/agents/issue-tracker.md`。

### Triage labels

本项目使用默认五类 triage 标签：`needs-triage`、`needs-info`、`ready-for-agent`、`ready-for-human`、`wontfix`。详见 `docs/agents/triage-labels.md`。

### Domain docs

本项目使用 single-context 领域文档布局：根目录 `CONTEXT.md` 和 `docs/adr/`。详见 `docs/agents/domain.md`。
