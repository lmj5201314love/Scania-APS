-- Day 7：风险分层与维修优先级 SQL 复核脚本
-- 假设 outputs/tables/day7_maintenance_priority_list.csv
-- 已导入 MySQL 表 model_prediction_result_day7。
--
-- 建议字段：
-- sample_id, model_name, strategy, y_true, y_proba, threshold, y_pred,
-- prediction_type, risk_level, suggested_action
--
-- 本脚本只写分析查询，不负责导入数据，不写真实数据库密码。
-- 如果你导入时使用了旧表名 model_prediction_result，请把下方表名统一替换。

USE scania_aps_project;

-- SQL 无法直接读取 config/config.yaml。
-- 运行前请确认这里的会话变量与 cfg.business_cost 保持一致。
SET @fp_cost := 10;
SET @fn_cost := 500;

-- 1. 各风险等级车辆数量：用于估算维修工作量。
SELECT
  risk_level,
  COUNT(*) AS sample_count
FROM model_prediction_result
GROUP BY risk_level
ORDER BY FIELD(risk_level, 'Critical', 'High', 'Medium', 'Low');

-- 2. 各风险等级实际故障数量和实际故障率：评估风险分层是否有业务区分度。
SELECT
  risk_level,
  COUNT(*) AS sample_count,
  SUM(CASE WHEN y_true = 1 THEN 1 ELSE 0 END) AS actual_pos_count,
  SUM(CASE WHEN y_true = 1 THEN 1 ELSE 0 END) / COUNT(*) AS actual_pos_rate
FROM model_prediction_result
GROUP BY risk_level
ORDER BY FIELD(risk_level, 'Critical', 'High', 'Medium', 'Low');

-- 3. 各风险等级平均预测概率：复核风险等级是否随概率单调下降。
SELECT
  risk_level,
  AVG(y_proba) AS avg_y_proba,
  MIN(y_proba) AS min_y_proba,
  MAX(y_proba) AS max_y_proba
FROM model_prediction_result
GROUP BY risk_level
ORDER BY FIELD(risk_level, 'Critical', 'High', 'Medium', 'Low');

-- 4. 各风险等级 TP / FP / TN / FN 数量：复核预测错误集中在哪些风险层。
SELECT
  risk_level,
  SUM(CASE WHEN prediction_type = 'TP' THEN 1 ELSE 0 END) AS tp,
  SUM(CASE WHEN prediction_type = 'FP' THEN 1 ELSE 0 END) AS fp,
  SUM(CASE WHEN prediction_type = 'TN' THEN 1 ELSE 0 END) AS tn,
  SUM(CASE WHEN prediction_type = 'FN' THEN 1 ELSE 0 END) AS fn
FROM model_prediction_result
GROUP BY risk_level
ORDER BY FIELD(risk_level, 'Critical', 'High', 'Medium', 'Low');

-- 5. Top 20 高风险车辆：用于维修团队优先排查清单。
SELECT
  sample_id,
  model_name,
  strategy,
  y_true,
  y_proba,
  threshold,
  y_pred,
  prediction_type,
  risk_level,
  suggested_action
FROM model_prediction_result
ORDER BY y_proba DESC
LIMIT 20;

-- 6. 高风险车辆中实际故障占比：Critical + High 的命中情况。
SELECT
  COUNT(*) AS high_risk_count,
  SUM(CASE WHEN y_true = 1 THEN 1 ELSE 0 END) AS actual_pos_count,
  SUM(CASE WHEN y_true = 1 THEN 1 ELSE 0 END) / COUNT(*) AS actual_pos_rate
FROM model_prediction_result
WHERE risk_level IN ('Critical', 'High');

-- 7. 按 suggested_action 汇总维修工作量：将模型结果转化为业务动作。
SELECT
  suggested_action,
  COUNT(*) AS sample_count,
  SUM(CASE WHEN y_true = 1 THEN 1 ELSE 0 END) AS actual_pos_count,
  AVG(y_proba) AS avg_y_proba
FROM model_prediction_result
GROUP BY suggested_action
ORDER BY FIELD(suggested_action, '立即检修', '优先检修', '观察复查', '暂不处理');

-- 8. 当前方案与 naive baseline 的 total cost 对比。
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
  'current_threshold_solution' AS solution_name,
  current_solution.fp,
  current_solution.fn,
  current_solution.fp * @fp_cost + current_solution.fn * @fn_cost AS total_cost
FROM current_solution
UNION ALL
SELECT
  'naive_all_negative' AS solution_name,
  naive_baseline.fp,
  naive_baseline.fn,
  naive_baseline.fp * @fp_cost + naive_baseline.fn * @fn_cost AS total_cost
FROM naive_baseline;

-- 9. 当前方案与默认阈值 0.5 的 total cost 对比。
-- 这里使用 y_proba 在 SQL 中回放默认阈值，不需要重新导入默认预测表。
WITH current_solution AS (
  SELECT
    SUM(CASE WHEN prediction_type = 'FP' THEN 1 ELSE 0 END) AS fp,
    SUM(CASE WHEN prediction_type = 'FN' THEN 1 ELSE 0 END) AS fn
  FROM model_prediction_result
),
default_threshold AS (
  SELECT
    SUM(CASE WHEN y_true = 0 AND y_proba >= 0.5 THEN 1 ELSE 0 END) AS fp,
    SUM(CASE WHEN y_true = 1 AND y_proba < 0.5 THEN 1 ELSE 0 END) AS fn
  FROM model_prediction_result
)
SELECT
  'current_threshold_solution' AS solution_name,
  current_solution.fp,
  current_solution.fn,
  current_solution.fp * @fp_cost + current_solution.fn * @fn_cost AS total_cost
FROM current_solution
UNION ALL
SELECT
  'default_threshold_0_5' AS solution_name,
  default_threshold.fp,
  default_threshold.fn,
  default_threshold.fp * @fp_cost + default_threshold.fn * @fn_cost AS total_cost
FROM default_threshold;
