-- Day 6/Day 7：模型预测结果分析 SQL
-- 说明：
-- 1. 本文件用于复核已导入的 Day 7 预测结果。
-- 2. 不重新训练模型，不重新搜索阈值，只基于 y_proba 回放默认阈值和当前阈值。
-- 3. 成本参数在代码中来自 config/config.yaml；SQL 中使用会话变量并要求运行前人工确认。

USE scania_aps_project;

SET @fp_cost := 10;
SET @fn_cost := 500;
SET @default_threshold := 0.5;

-- 1. 当前导入预测结果概览。
SELECT
  model_name,
  strategy,
  threshold,
  COUNT(*) AS sample_count,
  AVG(y_proba) AS avg_y_proba,
  MIN(y_proba) AS min_y_proba,
  MAX(y_proba) AS max_y_proba
FROM model_prediction_result
GROUP BY model_name, strategy, threshold;

-- 2. 当前阈值下的 precision / recall / cost。
WITH cm AS (
  SELECT
    SUM(CASE WHEN y_true = 1 AND y_pred = 1 THEN 1 ELSE 0 END) AS tp,
    SUM(CASE WHEN y_true = 0 AND y_pred = 1 THEN 1 ELSE 0 END) AS fp,
    SUM(CASE WHEN y_true = 1 AND y_pred = 0 THEN 1 ELSE 0 END) AS fn,
    SUM(CASE WHEN y_true = 0 AND y_pred = 0 THEN 1 ELSE 0 END) AS tn
  FROM model_prediction_result
)
SELECT
  tp,
  fp,
  fn,
  tn,
  tp / NULLIF(tp + fp, 0) AS precision_value,
  tp / NULLIF(tp + fn, 0) AS recall_value,
  fp * @fp_cost + fn * @fn_cost AS total_cost
FROM cm;

-- 3. 使用 y_proba 回放默认阈值 0.5，便于和当前低成本阈值对比。
WITH cm_default AS (
  SELECT
    SUM(CASE WHEN y_true = 1 AND y_proba >= @default_threshold THEN 1 ELSE 0 END) AS tp,
    SUM(CASE WHEN y_true = 0 AND y_proba >= @default_threshold THEN 1 ELSE 0 END) AS fp,
    SUM(CASE WHEN y_true = 1 AND y_proba < @default_threshold THEN 1 ELSE 0 END) AS fn,
    SUM(CASE WHEN y_true = 0 AND y_proba < @default_threshold THEN 1 ELSE 0 END) AS tn
  FROM model_prediction_result
)
SELECT
  @default_threshold AS threshold,
  tp,
  fp,
  fn,
  tn,
  tp / NULLIF(tp + fp, 0) AS precision_value,
  tp / NULLIF(tp + fn, 0) AS recall_value,
  fp * @fp_cost + fn * @fn_cost AS total_cost
FROM cm_default;

-- 4. 预测概率分桶：观察模型排序结果是否集中在高概率区域。
SELECT
  CASE
    WHEN y_proba >= 0.80 THEN '0.80-1.00'
    WHEN y_proba >= 0.50 THEN '0.50-0.80'
    WHEN y_proba >= 0.20 THEN '0.20-0.50'
    WHEN y_proba >= 0.05 THEN '0.05-0.20'
    ELSE '0.00-0.05'
  END AS probability_bucket,
  COUNT(*) AS sample_count,
  SUM(CASE WHEN y_true = 1 THEN 1 ELSE 0 END) AS actual_pos_count,
  SUM(CASE WHEN y_true = 1 THEN 1 ELSE 0 END) / COUNT(*) AS actual_pos_rate
FROM model_prediction_result
GROUP BY probability_bucket
ORDER BY FIELD(probability_bucket, '0.80-1.00', '0.50-0.80', '0.20-0.50', '0.05-0.20', '0.00-0.05');
