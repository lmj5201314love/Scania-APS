-- Day 19：阈值敏感性分析。
-- 业务问题：阈值变化时，维修工作量、漏报和业务成本如何变化？
-- 本表只用于策略敏感性展示，不用于修改最终方案 threshold=0.18。

-- 完整阈值曲线。
SELECT
    threshold,
    predicted_positive_count,
    workload_rate,
    fp,
    fn,
    precision_score,
    recall_score,
    f2_score,
    total_cost
FROM threshold_sensitivity_results
ORDER BY threshold ASC;

-- 成本最低的 Top 10 threshold。
SELECT
    threshold,
    predicted_positive_count,
    workload_rate,
    fp,
    fn,
    precision_score,
    recall_score,
    f2_score,
    total_cost
FROM threshold_sensitivity_results
ORDER BY total_cost ASC, fn ASC, recall_score DESC
LIMIT 10;

-- recall >= 0.96 时成本最低的 threshold。
SELECT
    threshold,
    predicted_positive_count,
    workload_rate,
    fp,
    fn,
    precision_score,
    recall_score,
    f2_score,
    total_cost
FROM threshold_sensitivity_results
WHERE recall_score >= 0.96
ORDER BY total_cost ASC, fn ASC
LIMIT 10;

-- FN <= 15 时成本最低的 threshold。
SELECT
    threshold,
    predicted_positive_count,
    workload_rate,
    fp,
    fn,
    precision_score,
    recall_score,
    f2_score,
    total_cost
FROM threshold_sensitivity_results
WHERE fn <= 15
ORDER BY total_cost ASC, fn ASC
LIMIT 10;

-- 当前最终阈值 0.18 对应的指标。
SELECT
    threshold,
    predicted_positive_count,
    workload_rate,
    fp,
    fn,
    precision_score,
    recall_score,
    f2_score,
    total_cost
FROM threshold_sensitivity_results
WHERE ABS(threshold - 0.18) < 0.000001;
