-- Day 19：风险等级人口与业务队列分析。
-- 业务问题：不同风险等级对应多少样本、多少真实故障、多少 APS 检查与复核工作？
-- risk_level 来自 Python 导出逻辑，字段前缀和 sample_id 都不能解释为真实车辆或真实传感器含义。

SELECT
    risk_level,
    suggested_action,
    COUNT(*) AS tier_population,
    SUM(CASE WHEN y_true = 1 THEN 1 ELSE 0 END) AS actual_pos_count,
    SUM(CASE WHEN y_pred = 1 THEN 1 ELSE 0 END) AS predicted_pos_count,
    SUM(CASE WHEN y_true = 1 THEN 1 ELSE 0 END) / COUNT(*) AS actual_pos_rate,
    SUM(CASE WHEN y_pred = 1 THEN 1 ELSE 0 END) / COUNT(*) AS predicted_pos_rate,
    AVG(y_proba) AS avg_risk_score,
    SUM(CASE WHEN confusion_type = 'TP' THEN 1 ELSE 0 END) AS tp_count,
    SUM(CASE WHEN confusion_type = 'FP' THEN 1 ELSE 0 END) AS fp_count,
    SUM(CASE WHEN confusion_type = 'FN' THEN 1 ELSE 0 END) AS fn_count,
    SUM(CASE WHEN y_pred = 1 THEN 1 ELSE 0 END) AS aps_inspection_queue_count,
    CASE
        WHEN risk_level = 'Medium' THEN COUNT(*)
        ELSE 0
    END AS recheck_queue_count,
    CASE risk_level
        WHEN 'Critical' THEN 1
        WHEN 'High' THEN 2
        WHEN 'Medium' THEN 3
        WHEN 'Low' THEN 4
        ELSE 99
    END AS priority_order
FROM model_prediction_results
WHERE dataset = 'official_test'
GROUP BY risk_level, suggested_action
ORDER BY priority_order;

-- 按建议动作维度汇总样本分布与业务成本。
SELECT
    suggested_action,
    COUNT(*) AS sample_count,
    SUM(CASE WHEN y_true = 1 THEN 1 ELSE 0 END) AS actual_pos_count,
    AVG(y_proba) AS avg_risk_score,
    SUM(sample_cost) AS total_sample_cost
FROM model_prediction_results
WHERE dataset = 'official_test'
GROUP BY suggested_action
ORDER BY sample_count DESC;
