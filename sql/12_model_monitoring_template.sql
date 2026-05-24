-- Day 19：生产监控 SQL 模板。
-- 当前项目没有真实线上 batch 数据，本文件是未来上线监控模板。
-- 可以先用 model_prediction_results 模拟 reference batch，但不要声称已有生产监控结果。

-- 假设未来线上表结构如下：
-- production_prediction_batches(
--   batch_id,
--   prediction_date,
--   sample_id,
--   y_proba,
--   y_pred,
--   risk_level,
--   missing_rate,
--   model_version
-- )

-- 部分 A：每批预测数量。
SELECT
    batch_id,
    prediction_date,
    COUNT(*) AS sample_count
FROM production_prediction_batches
GROUP BY batch_id, prediction_date
ORDER BY prediction_date DESC;

-- 部分 B：每批预测阳性率。
SELECT
    batch_id,
    SUM(CASE WHEN y_pred = 1 THEN 1 ELSE 0 END) AS predicted_positive_count,
    SUM(CASE WHEN y_pred = 1 THEN 1 ELSE 0 END) / COUNT(*) AS predicted_positive_rate
FROM production_prediction_batches
GROUP BY batch_id
ORDER BY batch_id DESC;

-- 部分 C：每批风险等级占比。
SELECT
    batch_id,
    risk_level,
    COUNT(*) AS sample_count,
    COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY batch_id) AS risk_level_rate
FROM production_prediction_batches
GROUP BY batch_id, risk_level
ORDER BY batch_id DESC, FIELD(risk_level, 'Critical', 'High', 'Medium', 'Low');

-- 部分 D：预测分数分布漂移模板。
-- reference_distribution 可以由历史稳定窗口计算；这里用 official test 导出结果作为示例 reference。
WITH current_distribution AS (
    SELECT
        batch_id,
        CASE
            WHEN y_proba < 0.05 THEN '[0.00,0.05)'
            WHEN y_proba < 0.10 THEN '[0.05,0.10)'
            WHEN y_proba < 0.20 THEN '[0.10,0.20)'
            WHEN y_proba < 0.40 THEN '[0.20,0.40)'
            WHEN y_proba < 0.60 THEN '[0.40,0.60)'
            WHEN y_proba < 0.80 THEN '[0.60,0.80)'
            ELSE '[0.80,1.00]'
        END AS probability_band,
        COUNT(*) AS current_batch_count,
        COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY batch_id) AS current_batch_rate
    FROM production_prediction_batches
    GROUP BY batch_id, probability_band
),
reference_distribution AS (
    SELECT
        probability_band,
        COUNT(*) / SUM(COUNT(*)) OVER () AS reference_rate
    FROM model_prediction_results
    WHERE dataset = 'official_test'
    GROUP BY probability_band
)
SELECT
    c.batch_id,
    c.probability_band,
    c.current_batch_count,
    c.current_batch_rate,
    r.reference_rate,
    c.current_batch_rate - r.reference_rate AS rate_diff
FROM current_distribution c
LEFT JOIN reference_distribution r
    ON c.probability_band = r.probability_band;

-- 部分 E：缺失率漂移模板。
SELECT
    batch_id,
    AVG(missing_rate) AS avg_missing_rate,
    SUM(CASE WHEN missing_rate >= 0.50 THEN 1 ELSE 0 END) AS high_missing_sample_count
FROM production_prediction_batches
GROUP BY batch_id
ORDER BY batch_id DESC;

-- 部分 F：高风险样本数量变化。
SELECT
    batch_id,
    SUM(CASE WHEN risk_level = 'Critical' THEN 1 ELSE 0 END) AS critical_count,
    SUM(CASE WHEN risk_level = 'High' THEN 1 ELSE 0 END) AS high_count,
    SUM(CASE WHEN risk_level IN ('Critical', 'High') THEN 1 ELSE 0 END) / COUNT(*) AS critical_high_rate
FROM production_prediction_batches
GROUP BY batch_id
ORDER BY batch_id DESC;
