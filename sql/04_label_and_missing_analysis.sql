-- Day 3：标签与缺失值 SQL 分析
-- 目标：用 SQL 复核 Day 2 的标签分布、缺失率分层、高缺失字段、
-- train/test 缺失模式差异，以及 pos/neg 缺失模式差异。
-- 宽表逐列缺失率 SQL 由 scripts/generate_sql_missing_analysis.py 生成到
-- sql/generated_missing_rate_analysis.sql。
-- 也可以将 Day 2 产物 missing_summary_train.csv / missing_summary_test.csv
-- 导入 feature_missing_summary 后执行本文件中的汇总查询。

USE scania_aps_project;

-- 1. 标签分布 SQL。
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

-- 2. 缺失率分层统计。
-- 依赖 feature_missing_summary 中 summary_scope = 'overall' 的记录。
SELECT
  dataset,
  CASE
    WHEN missing_rate = 0 THEN '0%'
    WHEN missing_rate <= 0.05 THEN '0-5%'
    WHEN missing_rate <= 0.20 THEN '5-20%'
    WHEN missing_rate <= 0.50 THEN '20-50%'
    WHEN missing_rate <= 0.80 THEN '50-80%'
    ELSE '80-100%'
  END AS missing_level,
  COUNT(*) AS feature_count
FROM feature_missing_summary
WHERE summary_scope = 'overall'
GROUP BY
  dataset,
  CASE
    WHEN missing_rate = 0 THEN '0%'
    WHEN missing_rate <= 0.05 THEN '0-5%'
    WHEN missing_rate <= 0.20 THEN '5-20%'
    WHEN missing_rate <= 0.50 THEN '20-50%'
    WHEN missing_rate <= 0.80 THEN '50-80%'
    ELSE '80-100%'
  END
ORDER BY dataset, MIN(missing_rate);

-- 3. 高缺失字段：只识别，不删除。
SELECT
  dataset,
  feature_name,
  missing_count,
  total_count,
  missing_rate,
  CASE WHEN missing_rate >= 0.50 THEN 1 ELSE 0 END AS is_missing_ge_50,
  CASE WHEN missing_rate >= 0.80 THEN 1 ELSE 0 END AS is_missing_ge_80,
  CASE WHEN missing_rate = 1.00 THEN 1 ELSE 0 END AS is_missing_eq_100
FROM feature_missing_summary
WHERE summary_scope = 'overall'
  AND missing_rate >= 0.50
ORDER BY dataset, missing_rate DESC, feature_name;

-- 4. train/test 缺失率差异。
WITH train_missing AS (
  SELECT feature_name, missing_rate AS train_missing_rate
  FROM feature_missing_summary
  WHERE dataset = 'train'
    AND summary_scope = 'overall'
),
test_missing AS (
  SELECT feature_name, missing_rate AS test_missing_rate
  FROM feature_missing_summary
  WHERE dataset = 'test'
    AND summary_scope = 'overall'
)
SELECT
  t.feature_name,
  t.train_missing_rate,
  s.test_missing_rate,
  ABS(t.train_missing_rate - s.test_missing_rate) AS missing_rate_diff_abs
FROM train_missing t
JOIN test_missing s
  ON t.feature_name = s.feature_name
ORDER BY missing_rate_diff_abs DESC, t.feature_name;

-- 5. pos/neg 缺失率差异。
-- 依赖 feature_missing_summary 中 summary_scope = 'by_class' 的训练集记录。
WITH neg_missing AS (
  SELECT feature_name, missing_rate AS neg_missing_rate
  FROM feature_missing_summary
  WHERE dataset = 'train'
    AND summary_scope = 'by_class'
    AND class_label = 'neg'
),
pos_missing AS (
  SELECT feature_name, missing_rate AS pos_missing_rate
  FROM feature_missing_summary
  WHERE dataset = 'train'
    AND summary_scope = 'by_class'
    AND class_label = 'pos'
)
SELECT
  n.feature_name,
  n.neg_missing_rate,
  p.pos_missing_rate,
  ABS(n.neg_missing_rate - p.pos_missing_rate) AS missing_rate_diff_abs
FROM neg_missing n
JOIN pos_missing p
  ON n.feature_name = p.feature_name
ORDER BY missing_rate_diff_abs DESC, n.feature_name;

-- 6. Day 2 发现复核说明：
-- - 训练集 pos 占比很低，属于类别极不平衡问题。
-- - br_000、bq_000、bp_000、bo_000、ab_000、cr_000、bn_000、bm_000
--   是 Day 2 识别出的高缺失字段，SQL 复核时应重点检查。
-- - train/test 缺失模式整体接近，pos/neg 缺失模式差异较明显。
-- - 本文件只复核和观察，不做填充、删列或建模判断。
