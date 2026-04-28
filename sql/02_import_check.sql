-- Day 3：CSV 导入后检查脚本
-- 本文件只提供导入后的检查查询，不负责真正导入 CSV。
-- 预期行数：raw_aps_train = 60000，raw_aps_test = 16000。
-- 原始数据共有 170 个匿名数值特征，另有 class 标签字段。

USE scania_aps_project;

-- 1. 检查 raw_aps_train 行数。
SELECT
  'train' AS dataset,
  COUNT(*) AS total_rows,
  60000 AS expected_rows
FROM raw_aps_train;

-- 2. 检查 raw_aps_test 行数。
SELECT
  'test' AS dataset,
  COUNT(*) AS total_rows,
  16000 AS expected_rows
FROM raw_aps_test;

-- 3. 检查 class 标签取值。
SELECT
  'train' AS dataset,
  `class`,
  COUNT(*) AS sample_count
FROM raw_aps_train
GROUP BY `class`
UNION ALL
SELECT
  'test' AS dataset,
  `class`,
  COUNT(*) AS sample_count
FROM raw_aps_test
GROUP BY `class`;

-- 4. 检查 train/test 标签分布和占比。
WITH label_counts AS (
  SELECT 'train' AS dataset, `class`, COUNT(*) AS sample_count
  FROM raw_aps_train
  GROUP BY `class`
  UNION ALL
  SELECT 'test' AS dataset, `class`, COUNT(*) AS sample_count
  FROM raw_aps_test
  GROUP BY `class`
),
dataset_counts AS (
  SELECT 'train' AS dataset, COUNT(*) AS total_rows FROM raw_aps_train
  UNION ALL
  SELECT 'test' AS dataset, COUNT(*) AS total_rows FROM raw_aps_test
)
SELECT
  lc.dataset,
  lc.`class`,
  lc.sample_count,
  lc.sample_count / dc.total_rows AS sample_ratio
FROM label_counts lc
JOIN dataset_counts dc
  ON lc.dataset = dc.dataset
ORDER BY lc.dataset, lc.`class`;

-- 5. 检查是否存在 NULL class。
SELECT
  'train' AS dataset,
  SUM(CASE WHEN `class` IS NULL THEN 1 ELSE 0 END) AS null_class_count
FROM raw_aps_train
UNION ALL
SELECT
  'test' AS dataset,
  SUM(CASE WHEN `class` IS NULL THEN 1 ELSE 0 END) AS null_class_count
FROM raw_aps_test;

-- 6. 检查 sample_id 是否唯一，以及是否存在 NULL。
SELECT
  'train' AS dataset,
  COUNT(*) AS total_rows,
  COUNT(DISTINCT sample_id) AS distinct_sample_id,
  SUM(CASE WHEN sample_id IS NULL THEN 1 ELSE 0 END) AS null_sample_id_count
FROM raw_aps_train
UNION ALL
SELECT
  'test' AS dataset,
  COUNT(*) AS total_rows,
  COUNT(DISTINCT sample_id) AS distinct_sample_id,
  SUM(CASE WHEN sample_id IS NULL THEN 1 ELSE 0 END) AS null_sample_id_count
FROM raw_aps_test;

-- 7. 字段数量说明：
-- raw_aps_train/raw_aps_test 应包含 sample_id、class 和 170 个匿名数值特征。
-- 如果使用 MySQL Workbench 导入 CSV，请确认原始 CSV 中的 "na" 已作为 NULL 处理。
