-- Day 3：CSV 导入后快速检查
-- 只确认 raw 表是否成功导入，不做深入数据分析。
-- 预期行数：raw_aps_train = 60000，raw_aps_test = 16000。
-- 原始数据共有 170 个匿名数值特征，另有 class 标签字段。
USE scania_aps_project;

-- 1. train/test 行数检查
SELECT
  'train' AS dataset,
  COUNT(*) AS total_rows,
  60000 AS expected_rows,
  COUNT(*) - 60000 AS row_diff
FROM raw_aps_train
UNION ALL
SELECT
  'test' AS dataset,
  COUNT(*) AS total_rows,
  16000 AS expected_rows,
  COUNT(*) - 16000 AS row_diff
FROM raw_aps_test;


-- 2. class 取值检查
SELECT
  dataset,
  `class`,
  sample_count
FROM (
  SELECT 'train' AS dataset, `class`, COUNT(*) AS sample_count
  FROM raw_aps_train
  GROUP BY `class`

  UNION ALL

  SELECT 'test' AS dataset, `class`, COUNT(*) AS sample_count
  FROM raw_aps_test
  GROUP BY `class`
) t
ORDER BY dataset, `class`;


-- 3. class 空值检查
SELECT
  'train' AS dataset,
  SUM(CASE WHEN `class` IS NULL THEN 1 ELSE 0 END) AS null_class_count
FROM raw_aps_train
UNION ALL
SELECT
  'test' AS dataset,
  SUM(CASE WHEN `class` IS NULL THEN 1 ELSE 0 END) AS null_class_count
FROM raw_aps_test;


-- 4. sample_id 完整性检查
SELECT
  'train' AS dataset,
  COUNT(*) AS total_rows,
  COUNT(DISTINCT sample_id) AS distinct_sample_id,
  SUM(CASE WHEN sample_id IS NULL THEN 1 ELSE 0 END) AS null_sample_id_count,
  COUNT(*) - COUNT(DISTINCT sample_id) AS duplicate_sample_id_count
FROM raw_aps_train
UNION ALL
SELECT
  'test' AS dataset,
  COUNT(*) AS total_rows,
  COUNT(DISTINCT sample_id) AS distinct_sample_id,
  SUM(CASE WHEN sample_id IS NULL THEN 1 ELSE 0 END) AS null_sample_id_count,
  COUNT(*) - COUNT(DISTINCT sample_id) AS duplicate_sample_id_count
FROM raw_aps_test;