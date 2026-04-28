-- Day 3：基础数据质量分析 SQL
-- 目标：用 SQL 复核 Day 2 的数据规模、标签分布、class 空值和 target 映射。
-- 预期行数：train = 60000，test = 16000。
-- 本文件不做缺失值填充、字段删除、特征工程或建模。

USE scania_aps_project;

-- 1. 数据集概览。
WITH dataset_rows AS (
  SELECT 'train' AS dataset, COUNT(*) AS total_rows FROM raw_aps_train
  UNION ALL
  SELECT 'test' AS dataset, COUNT(*) AS total_rows FROM raw_aps_test
)
SELECT
  dataset,
  total_rows,
  170 AS feature_count,
  1 AS label_column_exists
FROM dataset_rows
ORDER BY dataset;

-- 2. 标签分布：dataset、class、count、ratio。
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

-- 3. class 空值检查。
SELECT
  'train' AS dataset,
  SUM(CASE WHEN `class` IS NULL THEN 1 ELSE 0 END) AS null_class_count
FROM raw_aps_train
UNION ALL
SELECT
  'test' AS dataset,
  SUM(CASE WHEN `class` IS NULL THEN 1 ELSE 0 END) AS null_class_count
FROM raw_aps_test;

-- 4. target 映射检查：pos -> 1，neg -> 0。
SELECT
  'train' AS dataset,
  `class`,
  CASE
    WHEN `class` = 'pos' THEN 1
    WHEN `class` = 'neg' THEN 0
    ELSE NULL
  END AS target,
  COUNT(*) AS sample_count
FROM raw_aps_train
GROUP BY
  `class`,
  CASE
    WHEN `class` = 'pos' THEN 1
    WHEN `class` = 'neg' THEN 0
    ELSE NULL
  END
UNION ALL
SELECT
  'test' AS dataset,
  `class`,
  CASE
    WHEN `class` = 'pos' THEN 1
    WHEN `class` = 'neg' THEN 0
    ELSE NULL
  END AS target,
  COUNT(*) AS sample_count
FROM raw_aps_test
GROUP BY
  `class`,
  CASE
    WHEN `class` = 'pos' THEN 1
    WHEN `class` = 'neg' THEN 0
    ELSE NULL
  END;

-- 5. sample_id 主键完整性检查。
SELECT
  'train' AS dataset,
  COUNT(*) AS total_rows,
  COUNT(DISTINCT sample_id) AS distinct_sample_id,
  COUNT(*) - COUNT(DISTINCT sample_id) AS duplicate_sample_id_count
FROM raw_aps_train
UNION ALL
SELECT
  'test' AS dataset,
  COUNT(*) AS total_rows,
  COUNT(DISTINCT sample_id) AS distinct_sample_id,
  COUNT(*) - COUNT(DISTINCT sample_id) AS duplicate_sample_id_count
FROM raw_aps_test;
