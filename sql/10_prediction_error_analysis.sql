-- Day 19：预测错误分析。
-- 业务问题：模型的误报和漏报集中在哪里？
-- 注意：这些查询用于复盘 final candidate，不用于反向修改阈值或模型。

-- 部分 A：混淆矩阵汇总。
SELECT
    confusion_type,
    COUNT(*) AS sample_count,
    AVG(y_proba) AS avg_probability,
    SUM(sample_cost) AS total_sample_cost
FROM model_prediction_results
WHERE dataset = 'official_test'
GROUP BY confusion_type
ORDER BY FIELD(confusion_type, 'TP', 'FP', 'FN', 'TN');

-- 部分 B：按风险等级统计 FP / FN。
SELECT
    confusion_type,
    risk_level,
    COUNT(*) AS sample_count,
    AVG(y_proba) AS avg_probability,
    SUM(sample_cost) AS total_sample_cost
FROM model_prediction_results
WHERE dataset = 'official_test'
  AND confusion_type IN ('FP', 'FN')
GROUP BY confusion_type, risk_level
ORDER BY confusion_type, FIELD(risk_level, 'Critical', 'High', 'Medium', 'Low');

-- 部分 C：按概率区间统计 FP / FN。
SELECT
    confusion_type,
    probability_band,
    COUNT(*) AS sample_count,
    AVG(y_proba) AS avg_probability,
    SUM(sample_cost) AS total_sample_cost
FROM model_prediction_results
WHERE dataset = 'official_test'
  AND confusion_type IN ('FP', 'FN')
GROUP BY confusion_type, probability_band
ORDER BY confusion_type, probability_band;

-- 部分 D：漏报样本清单。
-- 按 y_proba DESC 排序，用于优先查看最接近阈值却被漏掉的正类样本。
SELECT
    sample_id,
    y_true,
    y_proba,
    y_pred,
    risk_level,
    probability_band,
    sample_cost
FROM model_prediction_results
WHERE dataset = 'official_test'
  AND confusion_type = 'FN'
ORDER BY y_proba DESC, sample_id ASC;

-- 部分 E：高置信误报样本清单。
SELECT
    sample_id,
    y_true,
    y_proba,
    y_pred,
    risk_level,
    probability_band,
    sample_cost
FROM model_prediction_results
WHERE dataset = 'official_test'
  AND confusion_type = 'FP'
  AND y_proba >= 0.80
ORDER BY y_proba DESC, sample_id ASC;
