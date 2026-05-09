-- Day 5/Day 7：业务成本分析 SQL
-- 说明：
-- 1. 本文件用于在 MySQL 中复核模型预测结果对应的 FP/FN 成本。
-- 2. 成本参数在 Python 代码中来自 config/config.yaml。
-- 3. SQL 无法直接读取 YAML，因此这里使用会话变量，并在运行前人工确认与配置一致。
-- 4. 假设 Day 7 输出已导入 model_prediction_result_day7。

USE scania_aps_project;

-- 运行前请确认这两个值与 config/config.yaml 中 business_cost 保持一致。
SET @fp_cost := 10;
SET @fn_cost := 500;

-- 1. 当前候选方案的混淆矩阵和 total cost。
SELECT
  model_name,
  strategy,
  threshold,
  SUM(CASE WHEN prediction_type = 'TP' THEN 1 ELSE 0 END) AS tp,
  SUM(CASE WHEN prediction_type = 'FP' THEN 1 ELSE 0 END) AS fp,
  SUM(CASE WHEN prediction_type = 'FN' THEN 1 ELSE 0 END) AS fn,
  SUM(CASE WHEN prediction_type = 'TN' THEN 1 ELSE 0 END) AS tn,
  SUM(CASE WHEN prediction_type = 'FP' THEN 1 ELSE 0 END) * @fp_cost
    + SUM(CASE WHEN prediction_type = 'FN' THEN 1 ELSE 0 END) * @fn_cost AS total_cost
FROM model_prediction_result
GROUP BY model_name, strategy, threshold;

-- 2. naive baseline：全部预测为 neg，对应 FP=0，FN=真实 pos 数量。
SELECT
  'naive_all_negative' AS solution_name,
  0 AS fp,
  SUM(CASE WHEN y_true = 1 THEN 1 ELSE 0 END) AS fn,
  SUM(CASE WHEN y_true = 1 THEN 1 ELSE 0 END) * @fn_cost AS total_cost
FROM model_prediction_result;

-- 3. 当前方案相对 naive baseline 的成本下降。
WITH current_solution AS (
  SELECT
    SUM(CASE WHEN prediction_type = 'FP' THEN 1 ELSE 0 END) AS fp,
    SUM(CASE WHEN prediction_type = 'FN' THEN 1 ELSE 0 END) AS fn
  FROM model_prediction_result
),
naive_baseline AS (
  SELECT
    0 AS fp,
    SUM(CASE WHEN y_true = 1 THEN 1 ELSE 0 END) AS fn
  FROM model_prediction_result
)
SELECT
  current_solution.fp AS current_fp,
  current_solution.fn AS current_fn,
  current_solution.fp * @fp_cost + current_solution.fn * @fn_cost AS current_total_cost,
  naive_baseline.fp AS naive_fp,
  naive_baseline.fn AS naive_fn,
  naive_baseline.fp * @fp_cost + naive_baseline.fn * @fn_cost AS naive_total_cost,
  naive_baseline.fp * @fp_cost + naive_baseline.fn * @fn_cost
    - (current_solution.fp * @fp_cost + current_solution.fn * @fn_cost) AS cost_reduction,
  (
    naive_baseline.fp * @fp_cost + naive_baseline.fn * @fn_cost
    - (current_solution.fp * @fp_cost + current_solution.fn * @fn_cost)
  ) / NULLIF(naive_baseline.fp * @fp_cost + naive_baseline.fn * @fn_cost, 0) AS cost_reduction_rate
FROM current_solution
CROSS JOIN naive_baseline;
