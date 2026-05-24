-- Day 19：Decile / Lift / Gain 排序能力分析。
-- 业务问题：最高风险分位是否显著集中真实 APS 故障？
-- decile = 1 表示预测概率最高的 10% 样本。

WITH decile_stats AS (
    SELECT
        decile,
        COUNT(*) AS sample_count,
        SUM(CASE WHEN y_true = 1 THEN 1 ELSE 0 END) AS actual_pos_count
    FROM model_prediction_results
    WHERE dataset = 'official_test'
    GROUP BY decile
),
overall AS (
    SELECT
        COUNT(*) AS total_sample_count,
        SUM(CASE WHEN y_true = 1 THEN 1 ELSE 0 END) AS total_pos_count,
        SUM(CASE WHEN y_true = 1 THEN 1 ELSE 0 END) / COUNT(*) AS overall_pos_rate
    FROM model_prediction_results
    WHERE dataset = 'official_test'
),
gain_table AS (
    SELECT
        d.decile,
        d.sample_count,
        d.actual_pos_count,
        d.actual_pos_count / d.sample_count AS pos_rate,
        SUM(d.sample_count) OVER (ORDER BY d.decile ASC) AS cumulative_sample_count,
        SUM(d.actual_pos_count) OVER (ORDER BY d.decile ASC) AS cumulative_pos_count,
        o.total_pos_count,
        o.overall_pos_rate
    FROM decile_stats d
    CROSS JOIN overall o
)
SELECT
    decile,
    sample_count,
    actual_pos_count,
    pos_rate,
    cumulative_sample_count,
    cumulative_pos_count,
    cumulative_pos_count / total_pos_count AS cumulative_recall,
    overall_pos_rate,
    pos_rate / overall_pos_rate AS lift
FROM gain_table
ORDER BY decile ASC;
