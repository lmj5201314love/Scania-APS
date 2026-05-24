-- Day 19：Top-K 维修容量分析。
-- 业务问题：如果维修团队只能检查风险最高的 Top K 样本，能覆盖多少真实 APS 故障？
-- sample_id 是匿名样本编号，不是真实车辆 ID。
-- SQL 成本变量需要与 config/config.yaml 保持一致。
USE scania_aps_project;
SET @fp_cost = 10;
SET @fn_cost = 500;

WITH ranked_predictions AS (
    SELECT
        sample_id,
        y_true,
        y_proba,
        ROW_NUMBER() OVER (ORDER BY y_proba DESC, sample_id ASC) AS risk_rank
    FROM model_prediction_results
    WHERE dataset = 'official_test'
),
top_k_values AS (
    SELECT 50 AS top_k
    UNION ALL SELECT 100
    UNION ALL SELECT 200
    UNION ALL SELECT 500
    UNION ALL SELECT 1000
),
total_pos AS (
    SELECT SUM(CASE WHEN y_true = 1 THEN 1 ELSE 0 END) AS total_pos_count
    FROM model_prediction_results
    WHERE dataset = 'official_test'
)
SELECT
    k.top_k,
    COUNT(r.sample_id) AS inspected_count,
    SUM(CASE WHEN r.y_true = 1 THEN 1 ELSE 0 END) AS actual_pos_count,
    t.total_pos_count,
    SUM(CASE WHEN r.y_true = 1 THEN 1 ELSE 0 END) / COUNT(r.sample_id) AS precision_at_k,
    SUM(CASE WHEN r.y_true = 1 THEN 1 ELSE 0 END) / t.total_pos_count AS recall_at_k,
    t.total_pos_count - SUM(CASE WHEN r.y_true = 1 THEN 1 ELSE 0 END) AS missed_pos_count,
    COUNT(r.sample_id) AS estimated_workload,
    SUM(CASE WHEN r.y_true = 1 THEN 1 ELSE 0 END) * @fn_cost AS estimated_avoided_fn_cost,
    'Top-K 用于模拟维修容量约束，不用于重新选择模型阈值。' AS note
FROM top_k_values k
JOIN ranked_predictions r
    ON r.risk_rank <= k.top_k
CROSS JOIN total_pos t
GROUP BY k.top_k, t.total_pos_count
ORDER BY k.top_k;
