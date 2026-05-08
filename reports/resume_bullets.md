# Scania APS 项目简历表达

## 版本 A：简洁版

- 基于 Scania APS 重卡空气压力系统故障数据集完成预测性维护项目，处理 60,000 条训练样本、16,000 条测试样本和 170 个匿名工业特征。
- 针对缺失值、类别极不平衡和 FP=10 / FN=500 的业务成本差异，构建 Logistic Regression、Random Forest 和 XGBoost 模型，并使用 recall、F2、PR-AUC 和 total cost 评估。
- 基于 XGBoost 预测概率进行阈值成本敏感性分析，将测试集回溯 total cost 从 naive baseline 的 187,500 降至 8,640，FN 从 375 降至 9。
- 输出风险分层和维修优先级建议，将车辆划分为 Critical / High / Medium / Low 四类，支持检修资源排序。

## 版本 B：详细版

- 独立完成 Scania APS 预测性维护项目，围绕重卡空气压力系统故障识别构建端到端分析流程，覆盖数据质量分析、SQL 复核、建模、阈值优化、成本敏感评估和风险分层交付。
- 在数据理解阶段分析 60,000/16,000 官方 train/test 数据，识别类别极不平衡问题：训练集正类仅 1.67%，测试集正类 2.34%；同时分析 170 个匿名工业特征的缺失模式和高缺失字段。
- 使用 Python / pandas / scikit-learn / XGBoost 构建 Logistic Regression、Random Forest 和 XGBoost 对比实验，避免在测试集上拟合缺失填充、字段筛选或模型参数。
- 结合 Scania 业务成本设定 FP=10、FN=500，避免以 accuracy 作为核心指标，重点评估 recall、F2、PR-AUC 和 total cost。
- 通过阈值成本敏感性分析发现 XGBoost + median_all 在阈值 0.20 下的回溯成本最低：precision=0.4692、recall=0.9760、F2=0.8026、FP=414、FN=9、total cost=8,640。
- 将模型预测概率转化为 Critical / High / Medium / Low 风险等级，并输出维修动作建议：立即检修、优先检修、观察复查、暂不处理。
- 使用 SQL 脚本支持数据质量复核和风险分层结果分析，使项目不仅停留在 notebook，而是具备业务分析和数据库复核能力。
