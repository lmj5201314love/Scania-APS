-- Day 3：自动生成的宽表缺失率 SQL
-- 本文件由 scripts/generate_sql_missing_analysis.py 生成。
-- 只用于 MySQL 导入 raw_aps_train/raw_aps_test 后复核缺失率，不做填充、删列或建模。

USE scania_aps_project;

-- 1. train/test 每个字段整体缺失率。
-- 可直接查询，也可以将结果 INSERT INTO feature_missing_summary。
WITH overall_missing AS (
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'aa_000' AS feature_name,
  SUM(CASE WHEN `aa_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `aa_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'aa_000' AS feature_name,
  SUM(CASE WHEN `aa_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `aa_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ab_000' AS feature_name,
  SUM(CASE WHEN `ab_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ab_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ab_000' AS feature_name,
  SUM(CASE WHEN `ab_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ab_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ac_000' AS feature_name,
  SUM(CASE WHEN `ac_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ac_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ac_000' AS feature_name,
  SUM(CASE WHEN `ac_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ac_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ad_000' AS feature_name,
  SUM(CASE WHEN `ad_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ad_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ad_000' AS feature_name,
  SUM(CASE WHEN `ad_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ad_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ae_000' AS feature_name,
  SUM(CASE WHEN `ae_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ae_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ae_000' AS feature_name,
  SUM(CASE WHEN `ae_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ae_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'af_000' AS feature_name,
  SUM(CASE WHEN `af_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `af_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'af_000' AS feature_name,
  SUM(CASE WHEN `af_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `af_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ag_000' AS feature_name,
  SUM(CASE WHEN `ag_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ag_000' AS feature_name,
  SUM(CASE WHEN `ag_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ag_001' AS feature_name,
  SUM(CASE WHEN `ag_001` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_001` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ag_001' AS feature_name,
  SUM(CASE WHEN `ag_001` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_001` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ag_002' AS feature_name,
  SUM(CASE WHEN `ag_002` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_002` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ag_002' AS feature_name,
  SUM(CASE WHEN `ag_002` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_002` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ag_003' AS feature_name,
  SUM(CASE WHEN `ag_003` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_003` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ag_003' AS feature_name,
  SUM(CASE WHEN `ag_003` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_003` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ag_004' AS feature_name,
  SUM(CASE WHEN `ag_004` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_004` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ag_004' AS feature_name,
  SUM(CASE WHEN `ag_004` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_004` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ag_005' AS feature_name,
  SUM(CASE WHEN `ag_005` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_005` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ag_005' AS feature_name,
  SUM(CASE WHEN `ag_005` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_005` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ag_006' AS feature_name,
  SUM(CASE WHEN `ag_006` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_006` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ag_006' AS feature_name,
  SUM(CASE WHEN `ag_006` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_006` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ag_007' AS feature_name,
  SUM(CASE WHEN `ag_007` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_007` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ag_007' AS feature_name,
  SUM(CASE WHEN `ag_007` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_007` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ag_008' AS feature_name,
  SUM(CASE WHEN `ag_008` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_008` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ag_008' AS feature_name,
  SUM(CASE WHEN `ag_008` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_008` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ag_009' AS feature_name,
  SUM(CASE WHEN `ag_009` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_009` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ag_009' AS feature_name,
  SUM(CASE WHEN `ag_009` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_009` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ah_000' AS feature_name,
  SUM(CASE WHEN `ah_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ah_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ah_000' AS feature_name,
  SUM(CASE WHEN `ah_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ah_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ai_000' AS feature_name,
  SUM(CASE WHEN `ai_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ai_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ai_000' AS feature_name,
  SUM(CASE WHEN `ai_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ai_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'aj_000' AS feature_name,
  SUM(CASE WHEN `aj_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `aj_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'aj_000' AS feature_name,
  SUM(CASE WHEN `aj_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `aj_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ak_000' AS feature_name,
  SUM(CASE WHEN `ak_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ak_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ak_000' AS feature_name,
  SUM(CASE WHEN `ak_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ak_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'al_000' AS feature_name,
  SUM(CASE WHEN `al_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `al_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'al_000' AS feature_name,
  SUM(CASE WHEN `al_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `al_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'am_0' AS feature_name,
  SUM(CASE WHEN `am_0` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `am_0` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'am_0' AS feature_name,
  SUM(CASE WHEN `am_0` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `am_0` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'an_000' AS feature_name,
  SUM(CASE WHEN `an_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `an_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'an_000' AS feature_name,
  SUM(CASE WHEN `an_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `an_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ao_000' AS feature_name,
  SUM(CASE WHEN `ao_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ao_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ao_000' AS feature_name,
  SUM(CASE WHEN `ao_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ao_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ap_000' AS feature_name,
  SUM(CASE WHEN `ap_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ap_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ap_000' AS feature_name,
  SUM(CASE WHEN `ap_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ap_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'aq_000' AS feature_name,
  SUM(CASE WHEN `aq_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `aq_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'aq_000' AS feature_name,
  SUM(CASE WHEN `aq_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `aq_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ar_000' AS feature_name,
  SUM(CASE WHEN `ar_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ar_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ar_000' AS feature_name,
  SUM(CASE WHEN `ar_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ar_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'as_000' AS feature_name,
  SUM(CASE WHEN `as_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `as_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'as_000' AS feature_name,
  SUM(CASE WHEN `as_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `as_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'at_000' AS feature_name,
  SUM(CASE WHEN `at_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `at_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'at_000' AS feature_name,
  SUM(CASE WHEN `at_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `at_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'au_000' AS feature_name,
  SUM(CASE WHEN `au_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `au_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'au_000' AS feature_name,
  SUM(CASE WHEN `au_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `au_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'av_000' AS feature_name,
  SUM(CASE WHEN `av_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `av_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'av_000' AS feature_name,
  SUM(CASE WHEN `av_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `av_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ax_000' AS feature_name,
  SUM(CASE WHEN `ax_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ax_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ax_000' AS feature_name,
  SUM(CASE WHEN `ax_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ax_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ay_000' AS feature_name,
  SUM(CASE WHEN `ay_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ay_000' AS feature_name,
  SUM(CASE WHEN `ay_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ay_001' AS feature_name,
  SUM(CASE WHEN `ay_001` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_001` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ay_001' AS feature_name,
  SUM(CASE WHEN `ay_001` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_001` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ay_002' AS feature_name,
  SUM(CASE WHEN `ay_002` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_002` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ay_002' AS feature_name,
  SUM(CASE WHEN `ay_002` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_002` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ay_003' AS feature_name,
  SUM(CASE WHEN `ay_003` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_003` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ay_003' AS feature_name,
  SUM(CASE WHEN `ay_003` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_003` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ay_004' AS feature_name,
  SUM(CASE WHEN `ay_004` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_004` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ay_004' AS feature_name,
  SUM(CASE WHEN `ay_004` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_004` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ay_005' AS feature_name,
  SUM(CASE WHEN `ay_005` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_005` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ay_005' AS feature_name,
  SUM(CASE WHEN `ay_005` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_005` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ay_006' AS feature_name,
  SUM(CASE WHEN `ay_006` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_006` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ay_006' AS feature_name,
  SUM(CASE WHEN `ay_006` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_006` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ay_007' AS feature_name,
  SUM(CASE WHEN `ay_007` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_007` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ay_007' AS feature_name,
  SUM(CASE WHEN `ay_007` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_007` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ay_008' AS feature_name,
  SUM(CASE WHEN `ay_008` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_008` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ay_008' AS feature_name,
  SUM(CASE WHEN `ay_008` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_008` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ay_009' AS feature_name,
  SUM(CASE WHEN `ay_009` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_009` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ay_009' AS feature_name,
  SUM(CASE WHEN `ay_009` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_009` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'az_000' AS feature_name,
  SUM(CASE WHEN `az_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'az_000' AS feature_name,
  SUM(CASE WHEN `az_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'az_001' AS feature_name,
  SUM(CASE WHEN `az_001` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_001` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'az_001' AS feature_name,
  SUM(CASE WHEN `az_001` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_001` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'az_002' AS feature_name,
  SUM(CASE WHEN `az_002` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_002` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'az_002' AS feature_name,
  SUM(CASE WHEN `az_002` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_002` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'az_003' AS feature_name,
  SUM(CASE WHEN `az_003` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_003` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'az_003' AS feature_name,
  SUM(CASE WHEN `az_003` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_003` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'az_004' AS feature_name,
  SUM(CASE WHEN `az_004` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_004` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'az_004' AS feature_name,
  SUM(CASE WHEN `az_004` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_004` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'az_005' AS feature_name,
  SUM(CASE WHEN `az_005` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_005` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'az_005' AS feature_name,
  SUM(CASE WHEN `az_005` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_005` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'az_006' AS feature_name,
  SUM(CASE WHEN `az_006` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_006` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'az_006' AS feature_name,
  SUM(CASE WHEN `az_006` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_006` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'az_007' AS feature_name,
  SUM(CASE WHEN `az_007` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_007` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'az_007' AS feature_name,
  SUM(CASE WHEN `az_007` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_007` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'az_008' AS feature_name,
  SUM(CASE WHEN `az_008` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_008` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'az_008' AS feature_name,
  SUM(CASE WHEN `az_008` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_008` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'az_009' AS feature_name,
  SUM(CASE WHEN `az_009` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_009` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'az_009' AS feature_name,
  SUM(CASE WHEN `az_009` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_009` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ba_000' AS feature_name,
  SUM(CASE WHEN `ba_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ba_000' AS feature_name,
  SUM(CASE WHEN `ba_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ba_001' AS feature_name,
  SUM(CASE WHEN `ba_001` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_001` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ba_001' AS feature_name,
  SUM(CASE WHEN `ba_001` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_001` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ba_002' AS feature_name,
  SUM(CASE WHEN `ba_002` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_002` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ba_002' AS feature_name,
  SUM(CASE WHEN `ba_002` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_002` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ba_003' AS feature_name,
  SUM(CASE WHEN `ba_003` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_003` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ba_003' AS feature_name,
  SUM(CASE WHEN `ba_003` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_003` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ba_004' AS feature_name,
  SUM(CASE WHEN `ba_004` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_004` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ba_004' AS feature_name,
  SUM(CASE WHEN `ba_004` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_004` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ba_005' AS feature_name,
  SUM(CASE WHEN `ba_005` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_005` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ba_005' AS feature_name,
  SUM(CASE WHEN `ba_005` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_005` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ba_006' AS feature_name,
  SUM(CASE WHEN `ba_006` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_006` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ba_006' AS feature_name,
  SUM(CASE WHEN `ba_006` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_006` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ba_007' AS feature_name,
  SUM(CASE WHEN `ba_007` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_007` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ba_007' AS feature_name,
  SUM(CASE WHEN `ba_007` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_007` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ba_008' AS feature_name,
  SUM(CASE WHEN `ba_008` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_008` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ba_008' AS feature_name,
  SUM(CASE WHEN `ba_008` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_008` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ba_009' AS feature_name,
  SUM(CASE WHEN `ba_009` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_009` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ba_009' AS feature_name,
  SUM(CASE WHEN `ba_009` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_009` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bb_000' AS feature_name,
  SUM(CASE WHEN `bb_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bb_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bb_000' AS feature_name,
  SUM(CASE WHEN `bb_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bb_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bc_000' AS feature_name,
  SUM(CASE WHEN `bc_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bc_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bc_000' AS feature_name,
  SUM(CASE WHEN `bc_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bc_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bd_000' AS feature_name,
  SUM(CASE WHEN `bd_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bd_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bd_000' AS feature_name,
  SUM(CASE WHEN `bd_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bd_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'be_000' AS feature_name,
  SUM(CASE WHEN `be_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `be_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'be_000' AS feature_name,
  SUM(CASE WHEN `be_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `be_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bf_000' AS feature_name,
  SUM(CASE WHEN `bf_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bf_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bf_000' AS feature_name,
  SUM(CASE WHEN `bf_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bf_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bg_000' AS feature_name,
  SUM(CASE WHEN `bg_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bg_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bg_000' AS feature_name,
  SUM(CASE WHEN `bg_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bg_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bh_000' AS feature_name,
  SUM(CASE WHEN `bh_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bh_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bh_000' AS feature_name,
  SUM(CASE WHEN `bh_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bh_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bi_000' AS feature_name,
  SUM(CASE WHEN `bi_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bi_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bi_000' AS feature_name,
  SUM(CASE WHEN `bi_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bi_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bj_000' AS feature_name,
  SUM(CASE WHEN `bj_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bj_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bj_000' AS feature_name,
  SUM(CASE WHEN `bj_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bj_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bk_000' AS feature_name,
  SUM(CASE WHEN `bk_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bk_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bk_000' AS feature_name,
  SUM(CASE WHEN `bk_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bk_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bl_000' AS feature_name,
  SUM(CASE WHEN `bl_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bl_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bl_000' AS feature_name,
  SUM(CASE WHEN `bl_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bl_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bm_000' AS feature_name,
  SUM(CASE WHEN `bm_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bm_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bm_000' AS feature_name,
  SUM(CASE WHEN `bm_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bm_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bn_000' AS feature_name,
  SUM(CASE WHEN `bn_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bn_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bn_000' AS feature_name,
  SUM(CASE WHEN `bn_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bn_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bo_000' AS feature_name,
  SUM(CASE WHEN `bo_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bo_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bo_000' AS feature_name,
  SUM(CASE WHEN `bo_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bo_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bp_000' AS feature_name,
  SUM(CASE WHEN `bp_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bp_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bp_000' AS feature_name,
  SUM(CASE WHEN `bp_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bp_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bq_000' AS feature_name,
  SUM(CASE WHEN `bq_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bq_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bq_000' AS feature_name,
  SUM(CASE WHEN `bq_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bq_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'br_000' AS feature_name,
  SUM(CASE WHEN `br_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `br_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'br_000' AS feature_name,
  SUM(CASE WHEN `br_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `br_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bs_000' AS feature_name,
  SUM(CASE WHEN `bs_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bs_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bs_000' AS feature_name,
  SUM(CASE WHEN `bs_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bs_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bt_000' AS feature_name,
  SUM(CASE WHEN `bt_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bt_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bt_000' AS feature_name,
  SUM(CASE WHEN `bt_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bt_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bu_000' AS feature_name,
  SUM(CASE WHEN `bu_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bu_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bu_000' AS feature_name,
  SUM(CASE WHEN `bu_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bu_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bv_000' AS feature_name,
  SUM(CASE WHEN `bv_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bv_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bv_000' AS feature_name,
  SUM(CASE WHEN `bv_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bv_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bx_000' AS feature_name,
  SUM(CASE WHEN `bx_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bx_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bx_000' AS feature_name,
  SUM(CASE WHEN `bx_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bx_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'by_000' AS feature_name,
  SUM(CASE WHEN `by_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `by_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'by_000' AS feature_name,
  SUM(CASE WHEN `by_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `by_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bz_000' AS feature_name,
  SUM(CASE WHEN `bz_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bz_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'bz_000' AS feature_name,
  SUM(CASE WHEN `bz_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bz_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ca_000' AS feature_name,
  SUM(CASE WHEN `ca_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ca_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ca_000' AS feature_name,
  SUM(CASE WHEN `ca_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ca_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cb_000' AS feature_name,
  SUM(CASE WHEN `cb_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cb_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cb_000' AS feature_name,
  SUM(CASE WHEN `cb_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cb_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cc_000' AS feature_name,
  SUM(CASE WHEN `cc_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cc_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cc_000' AS feature_name,
  SUM(CASE WHEN `cc_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cc_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cd_000' AS feature_name,
  SUM(CASE WHEN `cd_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cd_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cd_000' AS feature_name,
  SUM(CASE WHEN `cd_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cd_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ce_000' AS feature_name,
  SUM(CASE WHEN `ce_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ce_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ce_000' AS feature_name,
  SUM(CASE WHEN `ce_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ce_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cf_000' AS feature_name,
  SUM(CASE WHEN `cf_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cf_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cf_000' AS feature_name,
  SUM(CASE WHEN `cf_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cf_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cg_000' AS feature_name,
  SUM(CASE WHEN `cg_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cg_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cg_000' AS feature_name,
  SUM(CASE WHEN `cg_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cg_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ch_000' AS feature_name,
  SUM(CASE WHEN `ch_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ch_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ch_000' AS feature_name,
  SUM(CASE WHEN `ch_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ch_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ci_000' AS feature_name,
  SUM(CASE WHEN `ci_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ci_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ci_000' AS feature_name,
  SUM(CASE WHEN `ci_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ci_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cj_000' AS feature_name,
  SUM(CASE WHEN `cj_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cj_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cj_000' AS feature_name,
  SUM(CASE WHEN `cj_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cj_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ck_000' AS feature_name,
  SUM(CASE WHEN `ck_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ck_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ck_000' AS feature_name,
  SUM(CASE WHEN `ck_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ck_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cl_000' AS feature_name,
  SUM(CASE WHEN `cl_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cl_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cl_000' AS feature_name,
  SUM(CASE WHEN `cl_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cl_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cm_000' AS feature_name,
  SUM(CASE WHEN `cm_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cm_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cm_000' AS feature_name,
  SUM(CASE WHEN `cm_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cm_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cn_000' AS feature_name,
  SUM(CASE WHEN `cn_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cn_000' AS feature_name,
  SUM(CASE WHEN `cn_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cn_001' AS feature_name,
  SUM(CASE WHEN `cn_001` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_001` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cn_001' AS feature_name,
  SUM(CASE WHEN `cn_001` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_001` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cn_002' AS feature_name,
  SUM(CASE WHEN `cn_002` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_002` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cn_002' AS feature_name,
  SUM(CASE WHEN `cn_002` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_002` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cn_003' AS feature_name,
  SUM(CASE WHEN `cn_003` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_003` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cn_003' AS feature_name,
  SUM(CASE WHEN `cn_003` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_003` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cn_004' AS feature_name,
  SUM(CASE WHEN `cn_004` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_004` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cn_004' AS feature_name,
  SUM(CASE WHEN `cn_004` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_004` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cn_005' AS feature_name,
  SUM(CASE WHEN `cn_005` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_005` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cn_005' AS feature_name,
  SUM(CASE WHEN `cn_005` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_005` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cn_006' AS feature_name,
  SUM(CASE WHEN `cn_006` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_006` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cn_006' AS feature_name,
  SUM(CASE WHEN `cn_006` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_006` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cn_007' AS feature_name,
  SUM(CASE WHEN `cn_007` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_007` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cn_007' AS feature_name,
  SUM(CASE WHEN `cn_007` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_007` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cn_008' AS feature_name,
  SUM(CASE WHEN `cn_008` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_008` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cn_008' AS feature_name,
  SUM(CASE WHEN `cn_008` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_008` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cn_009' AS feature_name,
  SUM(CASE WHEN `cn_009` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_009` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cn_009' AS feature_name,
  SUM(CASE WHEN `cn_009` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_009` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'co_000' AS feature_name,
  SUM(CASE WHEN `co_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `co_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'co_000' AS feature_name,
  SUM(CASE WHEN `co_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `co_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cp_000' AS feature_name,
  SUM(CASE WHEN `cp_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cp_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cp_000' AS feature_name,
  SUM(CASE WHEN `cp_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cp_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cq_000' AS feature_name,
  SUM(CASE WHEN `cq_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cq_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cq_000' AS feature_name,
  SUM(CASE WHEN `cq_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cq_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cr_000' AS feature_name,
  SUM(CASE WHEN `cr_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cr_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cr_000' AS feature_name,
  SUM(CASE WHEN `cr_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cr_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cs_000' AS feature_name,
  SUM(CASE WHEN `cs_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cs_000' AS feature_name,
  SUM(CASE WHEN `cs_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cs_001' AS feature_name,
  SUM(CASE WHEN `cs_001` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_001` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cs_001' AS feature_name,
  SUM(CASE WHEN `cs_001` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_001` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cs_002' AS feature_name,
  SUM(CASE WHEN `cs_002` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_002` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cs_002' AS feature_name,
  SUM(CASE WHEN `cs_002` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_002` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cs_003' AS feature_name,
  SUM(CASE WHEN `cs_003` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_003` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cs_003' AS feature_name,
  SUM(CASE WHEN `cs_003` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_003` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cs_004' AS feature_name,
  SUM(CASE WHEN `cs_004` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_004` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cs_004' AS feature_name,
  SUM(CASE WHEN `cs_004` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_004` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cs_005' AS feature_name,
  SUM(CASE WHEN `cs_005` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_005` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cs_005' AS feature_name,
  SUM(CASE WHEN `cs_005` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_005` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cs_006' AS feature_name,
  SUM(CASE WHEN `cs_006` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_006` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cs_006' AS feature_name,
  SUM(CASE WHEN `cs_006` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_006` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cs_007' AS feature_name,
  SUM(CASE WHEN `cs_007` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_007` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cs_007' AS feature_name,
  SUM(CASE WHEN `cs_007` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_007` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cs_008' AS feature_name,
  SUM(CASE WHEN `cs_008` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_008` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cs_008' AS feature_name,
  SUM(CASE WHEN `cs_008` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_008` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cs_009' AS feature_name,
  SUM(CASE WHEN `cs_009` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_009` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cs_009' AS feature_name,
  SUM(CASE WHEN `cs_009` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_009` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ct_000' AS feature_name,
  SUM(CASE WHEN `ct_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ct_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ct_000' AS feature_name,
  SUM(CASE WHEN `ct_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ct_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cu_000' AS feature_name,
  SUM(CASE WHEN `cu_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cu_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cu_000' AS feature_name,
  SUM(CASE WHEN `cu_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cu_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cv_000' AS feature_name,
  SUM(CASE WHEN `cv_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cv_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cv_000' AS feature_name,
  SUM(CASE WHEN `cv_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cv_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cx_000' AS feature_name,
  SUM(CASE WHEN `cx_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cx_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cx_000' AS feature_name,
  SUM(CASE WHEN `cx_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cx_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cy_000' AS feature_name,
  SUM(CASE WHEN `cy_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cy_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cy_000' AS feature_name,
  SUM(CASE WHEN `cy_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cy_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cz_000' AS feature_name,
  SUM(CASE WHEN `cz_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cz_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'cz_000' AS feature_name,
  SUM(CASE WHEN `cz_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cz_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'da_000' AS feature_name,
  SUM(CASE WHEN `da_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `da_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'da_000' AS feature_name,
  SUM(CASE WHEN `da_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `da_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'db_000' AS feature_name,
  SUM(CASE WHEN `db_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `db_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'db_000' AS feature_name,
  SUM(CASE WHEN `db_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `db_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dc_000' AS feature_name,
  SUM(CASE WHEN `dc_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dc_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dc_000' AS feature_name,
  SUM(CASE WHEN `dc_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dc_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dd_000' AS feature_name,
  SUM(CASE WHEN `dd_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dd_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dd_000' AS feature_name,
  SUM(CASE WHEN `dd_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dd_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'de_000' AS feature_name,
  SUM(CASE WHEN `de_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `de_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'de_000' AS feature_name,
  SUM(CASE WHEN `de_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `de_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'df_000' AS feature_name,
  SUM(CASE WHEN `df_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `df_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'df_000' AS feature_name,
  SUM(CASE WHEN `df_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `df_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dg_000' AS feature_name,
  SUM(CASE WHEN `dg_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dg_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dg_000' AS feature_name,
  SUM(CASE WHEN `dg_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dg_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dh_000' AS feature_name,
  SUM(CASE WHEN `dh_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dh_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dh_000' AS feature_name,
  SUM(CASE WHEN `dh_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dh_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'di_000' AS feature_name,
  SUM(CASE WHEN `di_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `di_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'di_000' AS feature_name,
  SUM(CASE WHEN `di_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `di_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dj_000' AS feature_name,
  SUM(CASE WHEN `dj_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dj_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dj_000' AS feature_name,
  SUM(CASE WHEN `dj_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dj_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dk_000' AS feature_name,
  SUM(CASE WHEN `dk_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dk_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dk_000' AS feature_name,
  SUM(CASE WHEN `dk_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dk_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dl_000' AS feature_name,
  SUM(CASE WHEN `dl_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dl_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dl_000' AS feature_name,
  SUM(CASE WHEN `dl_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dl_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dm_000' AS feature_name,
  SUM(CASE WHEN `dm_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dm_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dm_000' AS feature_name,
  SUM(CASE WHEN `dm_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dm_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dn_000' AS feature_name,
  SUM(CASE WHEN `dn_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dn_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dn_000' AS feature_name,
  SUM(CASE WHEN `dn_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dn_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'do_000' AS feature_name,
  SUM(CASE WHEN `do_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `do_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'do_000' AS feature_name,
  SUM(CASE WHEN `do_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `do_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dp_000' AS feature_name,
  SUM(CASE WHEN `dp_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dp_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dp_000' AS feature_name,
  SUM(CASE WHEN `dp_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dp_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dq_000' AS feature_name,
  SUM(CASE WHEN `dq_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dq_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dq_000' AS feature_name,
  SUM(CASE WHEN `dq_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dq_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dr_000' AS feature_name,
  SUM(CASE WHEN `dr_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dr_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dr_000' AS feature_name,
  SUM(CASE WHEN `dr_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dr_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ds_000' AS feature_name,
  SUM(CASE WHEN `ds_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ds_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ds_000' AS feature_name,
  SUM(CASE WHEN `ds_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ds_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dt_000' AS feature_name,
  SUM(CASE WHEN `dt_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dt_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dt_000' AS feature_name,
  SUM(CASE WHEN `dt_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dt_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'du_000' AS feature_name,
  SUM(CASE WHEN `du_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `du_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'du_000' AS feature_name,
  SUM(CASE WHEN `du_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `du_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dv_000' AS feature_name,
  SUM(CASE WHEN `dv_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dv_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dv_000' AS feature_name,
  SUM(CASE WHEN `dv_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dv_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dx_000' AS feature_name,
  SUM(CASE WHEN `dx_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dx_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dx_000' AS feature_name,
  SUM(CASE WHEN `dx_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dx_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dy_000' AS feature_name,
  SUM(CASE WHEN `dy_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dy_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dy_000' AS feature_name,
  SUM(CASE WHEN `dy_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dy_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dz_000' AS feature_name,
  SUM(CASE WHEN `dz_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dz_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'dz_000' AS feature_name,
  SUM(CASE WHEN `dz_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dz_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ea_000' AS feature_name,
  SUM(CASE WHEN `ea_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ea_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ea_000' AS feature_name,
  SUM(CASE WHEN `ea_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ea_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'eb_000' AS feature_name,
  SUM(CASE WHEN `eb_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `eb_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'eb_000' AS feature_name,
  SUM(CASE WHEN `eb_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `eb_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ec_00' AS feature_name,
  SUM(CASE WHEN `ec_00` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ec_00` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ec_00' AS feature_name,
  SUM(CASE WHEN `ec_00` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ec_00` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ed_000' AS feature_name,
  SUM(CASE WHEN `ed_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ed_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ed_000' AS feature_name,
  SUM(CASE WHEN `ed_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ed_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ee_000' AS feature_name,
  SUM(CASE WHEN `ee_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ee_000' AS feature_name,
  SUM(CASE WHEN `ee_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ee_001' AS feature_name,
  SUM(CASE WHEN `ee_001` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_001` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ee_001' AS feature_name,
  SUM(CASE WHEN `ee_001` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_001` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ee_002' AS feature_name,
  SUM(CASE WHEN `ee_002` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_002` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ee_002' AS feature_name,
  SUM(CASE WHEN `ee_002` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_002` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ee_003' AS feature_name,
  SUM(CASE WHEN `ee_003` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_003` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ee_003' AS feature_name,
  SUM(CASE WHEN `ee_003` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_003` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ee_004' AS feature_name,
  SUM(CASE WHEN `ee_004` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_004` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ee_004' AS feature_name,
  SUM(CASE WHEN `ee_004` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_004` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ee_005' AS feature_name,
  SUM(CASE WHEN `ee_005` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_005` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ee_005' AS feature_name,
  SUM(CASE WHEN `ee_005` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_005` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ee_006' AS feature_name,
  SUM(CASE WHEN `ee_006` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_006` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ee_006' AS feature_name,
  SUM(CASE WHEN `ee_006` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_006` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ee_007' AS feature_name,
  SUM(CASE WHEN `ee_007` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_007` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ee_007' AS feature_name,
  SUM(CASE WHEN `ee_007` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_007` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ee_008' AS feature_name,
  SUM(CASE WHEN `ee_008` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_008` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ee_008' AS feature_name,
  SUM(CASE WHEN `ee_008` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_008` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ee_009' AS feature_name,
  SUM(CASE WHEN `ee_009` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_009` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ee_009' AS feature_name,
  SUM(CASE WHEN `ee_009` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_009` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ef_000' AS feature_name,
  SUM(CASE WHEN `ef_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ef_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'ef_000' AS feature_name,
  SUM(CASE WHEN `ef_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ef_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
UNION ALL
SELECT
  'train' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'eg_000' AS feature_name,
  SUM(CASE WHEN `eg_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `eg_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
UNION ALL
SELECT
  'test' AS dataset,
  'overall' AS summary_scope,
  'all' AS class_label,
  'eg_000' AS feature_name,
  SUM(CASE WHEN `eg_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `eg_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_test`
)
SELECT *
FROM overall_missing
ORDER BY dataset, missing_rate DESC, feature_name;

-- 2. 训练集 pos/neg 样本每个字段缺失率。
WITH class_missing AS (
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'aa_000' AS feature_name,
  SUM(CASE WHEN `aa_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `aa_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ab_000' AS feature_name,
  SUM(CASE WHEN `ab_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ab_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ac_000' AS feature_name,
  SUM(CASE WHEN `ac_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ac_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ad_000' AS feature_name,
  SUM(CASE WHEN `ad_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ad_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ae_000' AS feature_name,
  SUM(CASE WHEN `ae_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ae_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'af_000' AS feature_name,
  SUM(CASE WHEN `af_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `af_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ag_000' AS feature_name,
  SUM(CASE WHEN `ag_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ag_001' AS feature_name,
  SUM(CASE WHEN `ag_001` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_001` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ag_002' AS feature_name,
  SUM(CASE WHEN `ag_002` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_002` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ag_003' AS feature_name,
  SUM(CASE WHEN `ag_003` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_003` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ag_004' AS feature_name,
  SUM(CASE WHEN `ag_004` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_004` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ag_005' AS feature_name,
  SUM(CASE WHEN `ag_005` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_005` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ag_006' AS feature_name,
  SUM(CASE WHEN `ag_006` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_006` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ag_007' AS feature_name,
  SUM(CASE WHEN `ag_007` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_007` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ag_008' AS feature_name,
  SUM(CASE WHEN `ag_008` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_008` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ag_009' AS feature_name,
  SUM(CASE WHEN `ag_009` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ag_009` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ah_000' AS feature_name,
  SUM(CASE WHEN `ah_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ah_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ai_000' AS feature_name,
  SUM(CASE WHEN `ai_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ai_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'aj_000' AS feature_name,
  SUM(CASE WHEN `aj_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `aj_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ak_000' AS feature_name,
  SUM(CASE WHEN `ak_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ak_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'al_000' AS feature_name,
  SUM(CASE WHEN `al_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `al_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'am_0' AS feature_name,
  SUM(CASE WHEN `am_0` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `am_0` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'an_000' AS feature_name,
  SUM(CASE WHEN `an_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `an_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ao_000' AS feature_name,
  SUM(CASE WHEN `ao_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ao_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ap_000' AS feature_name,
  SUM(CASE WHEN `ap_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ap_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'aq_000' AS feature_name,
  SUM(CASE WHEN `aq_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `aq_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ar_000' AS feature_name,
  SUM(CASE WHEN `ar_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ar_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'as_000' AS feature_name,
  SUM(CASE WHEN `as_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `as_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'at_000' AS feature_name,
  SUM(CASE WHEN `at_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `at_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'au_000' AS feature_name,
  SUM(CASE WHEN `au_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `au_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'av_000' AS feature_name,
  SUM(CASE WHEN `av_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `av_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ax_000' AS feature_name,
  SUM(CASE WHEN `ax_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ax_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ay_000' AS feature_name,
  SUM(CASE WHEN `ay_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ay_001' AS feature_name,
  SUM(CASE WHEN `ay_001` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_001` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ay_002' AS feature_name,
  SUM(CASE WHEN `ay_002` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_002` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ay_003' AS feature_name,
  SUM(CASE WHEN `ay_003` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_003` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ay_004' AS feature_name,
  SUM(CASE WHEN `ay_004` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_004` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ay_005' AS feature_name,
  SUM(CASE WHEN `ay_005` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_005` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ay_006' AS feature_name,
  SUM(CASE WHEN `ay_006` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_006` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ay_007' AS feature_name,
  SUM(CASE WHEN `ay_007` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_007` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ay_008' AS feature_name,
  SUM(CASE WHEN `ay_008` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_008` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ay_009' AS feature_name,
  SUM(CASE WHEN `ay_009` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ay_009` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'az_000' AS feature_name,
  SUM(CASE WHEN `az_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'az_001' AS feature_name,
  SUM(CASE WHEN `az_001` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_001` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'az_002' AS feature_name,
  SUM(CASE WHEN `az_002` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_002` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'az_003' AS feature_name,
  SUM(CASE WHEN `az_003` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_003` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'az_004' AS feature_name,
  SUM(CASE WHEN `az_004` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_004` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'az_005' AS feature_name,
  SUM(CASE WHEN `az_005` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_005` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'az_006' AS feature_name,
  SUM(CASE WHEN `az_006` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_006` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'az_007' AS feature_name,
  SUM(CASE WHEN `az_007` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_007` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'az_008' AS feature_name,
  SUM(CASE WHEN `az_008` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_008` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'az_009' AS feature_name,
  SUM(CASE WHEN `az_009` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `az_009` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ba_000' AS feature_name,
  SUM(CASE WHEN `ba_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ba_001' AS feature_name,
  SUM(CASE WHEN `ba_001` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_001` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ba_002' AS feature_name,
  SUM(CASE WHEN `ba_002` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_002` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ba_003' AS feature_name,
  SUM(CASE WHEN `ba_003` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_003` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ba_004' AS feature_name,
  SUM(CASE WHEN `ba_004` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_004` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ba_005' AS feature_name,
  SUM(CASE WHEN `ba_005` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_005` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ba_006' AS feature_name,
  SUM(CASE WHEN `ba_006` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_006` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ba_007' AS feature_name,
  SUM(CASE WHEN `ba_007` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_007` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ba_008' AS feature_name,
  SUM(CASE WHEN `ba_008` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_008` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ba_009' AS feature_name,
  SUM(CASE WHEN `ba_009` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ba_009` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'bb_000' AS feature_name,
  SUM(CASE WHEN `bb_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bb_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'bc_000' AS feature_name,
  SUM(CASE WHEN `bc_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bc_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'bd_000' AS feature_name,
  SUM(CASE WHEN `bd_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bd_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'be_000' AS feature_name,
  SUM(CASE WHEN `be_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `be_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'bf_000' AS feature_name,
  SUM(CASE WHEN `bf_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bf_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'bg_000' AS feature_name,
  SUM(CASE WHEN `bg_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bg_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'bh_000' AS feature_name,
  SUM(CASE WHEN `bh_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bh_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'bi_000' AS feature_name,
  SUM(CASE WHEN `bi_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bi_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'bj_000' AS feature_name,
  SUM(CASE WHEN `bj_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bj_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'bk_000' AS feature_name,
  SUM(CASE WHEN `bk_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bk_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'bl_000' AS feature_name,
  SUM(CASE WHEN `bl_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bl_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'bm_000' AS feature_name,
  SUM(CASE WHEN `bm_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bm_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'bn_000' AS feature_name,
  SUM(CASE WHEN `bn_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bn_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'bo_000' AS feature_name,
  SUM(CASE WHEN `bo_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bo_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'bp_000' AS feature_name,
  SUM(CASE WHEN `bp_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bp_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'bq_000' AS feature_name,
  SUM(CASE WHEN `bq_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bq_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'br_000' AS feature_name,
  SUM(CASE WHEN `br_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `br_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'bs_000' AS feature_name,
  SUM(CASE WHEN `bs_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bs_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'bt_000' AS feature_name,
  SUM(CASE WHEN `bt_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bt_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'bu_000' AS feature_name,
  SUM(CASE WHEN `bu_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bu_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'bv_000' AS feature_name,
  SUM(CASE WHEN `bv_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bv_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'bx_000' AS feature_name,
  SUM(CASE WHEN `bx_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bx_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'by_000' AS feature_name,
  SUM(CASE WHEN `by_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `by_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'bz_000' AS feature_name,
  SUM(CASE WHEN `bz_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `bz_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ca_000' AS feature_name,
  SUM(CASE WHEN `ca_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ca_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cb_000' AS feature_name,
  SUM(CASE WHEN `cb_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cb_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cc_000' AS feature_name,
  SUM(CASE WHEN `cc_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cc_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cd_000' AS feature_name,
  SUM(CASE WHEN `cd_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cd_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ce_000' AS feature_name,
  SUM(CASE WHEN `ce_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ce_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cf_000' AS feature_name,
  SUM(CASE WHEN `cf_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cf_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cg_000' AS feature_name,
  SUM(CASE WHEN `cg_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cg_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ch_000' AS feature_name,
  SUM(CASE WHEN `ch_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ch_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ci_000' AS feature_name,
  SUM(CASE WHEN `ci_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ci_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cj_000' AS feature_name,
  SUM(CASE WHEN `cj_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cj_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ck_000' AS feature_name,
  SUM(CASE WHEN `ck_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ck_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cl_000' AS feature_name,
  SUM(CASE WHEN `cl_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cl_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cm_000' AS feature_name,
  SUM(CASE WHEN `cm_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cm_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cn_000' AS feature_name,
  SUM(CASE WHEN `cn_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cn_001' AS feature_name,
  SUM(CASE WHEN `cn_001` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_001` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cn_002' AS feature_name,
  SUM(CASE WHEN `cn_002` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_002` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cn_003' AS feature_name,
  SUM(CASE WHEN `cn_003` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_003` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cn_004' AS feature_name,
  SUM(CASE WHEN `cn_004` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_004` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cn_005' AS feature_name,
  SUM(CASE WHEN `cn_005` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_005` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cn_006' AS feature_name,
  SUM(CASE WHEN `cn_006` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_006` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cn_007' AS feature_name,
  SUM(CASE WHEN `cn_007` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_007` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cn_008' AS feature_name,
  SUM(CASE WHEN `cn_008` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_008` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cn_009' AS feature_name,
  SUM(CASE WHEN `cn_009` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cn_009` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'co_000' AS feature_name,
  SUM(CASE WHEN `co_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `co_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cp_000' AS feature_name,
  SUM(CASE WHEN `cp_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cp_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cq_000' AS feature_name,
  SUM(CASE WHEN `cq_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cq_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cr_000' AS feature_name,
  SUM(CASE WHEN `cr_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cr_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cs_000' AS feature_name,
  SUM(CASE WHEN `cs_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cs_001' AS feature_name,
  SUM(CASE WHEN `cs_001` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_001` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cs_002' AS feature_name,
  SUM(CASE WHEN `cs_002` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_002` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cs_003' AS feature_name,
  SUM(CASE WHEN `cs_003` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_003` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cs_004' AS feature_name,
  SUM(CASE WHEN `cs_004` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_004` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cs_005' AS feature_name,
  SUM(CASE WHEN `cs_005` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_005` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cs_006' AS feature_name,
  SUM(CASE WHEN `cs_006` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_006` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cs_007' AS feature_name,
  SUM(CASE WHEN `cs_007` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_007` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cs_008' AS feature_name,
  SUM(CASE WHEN `cs_008` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_008` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cs_009' AS feature_name,
  SUM(CASE WHEN `cs_009` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cs_009` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ct_000' AS feature_name,
  SUM(CASE WHEN `ct_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ct_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cu_000' AS feature_name,
  SUM(CASE WHEN `cu_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cu_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cv_000' AS feature_name,
  SUM(CASE WHEN `cv_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cv_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cx_000' AS feature_name,
  SUM(CASE WHEN `cx_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cx_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cy_000' AS feature_name,
  SUM(CASE WHEN `cy_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cy_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'cz_000' AS feature_name,
  SUM(CASE WHEN `cz_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `cz_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'da_000' AS feature_name,
  SUM(CASE WHEN `da_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `da_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'db_000' AS feature_name,
  SUM(CASE WHEN `db_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `db_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'dc_000' AS feature_name,
  SUM(CASE WHEN `dc_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dc_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'dd_000' AS feature_name,
  SUM(CASE WHEN `dd_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dd_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'de_000' AS feature_name,
  SUM(CASE WHEN `de_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `de_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'df_000' AS feature_name,
  SUM(CASE WHEN `df_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `df_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'dg_000' AS feature_name,
  SUM(CASE WHEN `dg_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dg_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'dh_000' AS feature_name,
  SUM(CASE WHEN `dh_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dh_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'di_000' AS feature_name,
  SUM(CASE WHEN `di_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `di_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'dj_000' AS feature_name,
  SUM(CASE WHEN `dj_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dj_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'dk_000' AS feature_name,
  SUM(CASE WHEN `dk_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dk_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'dl_000' AS feature_name,
  SUM(CASE WHEN `dl_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dl_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'dm_000' AS feature_name,
  SUM(CASE WHEN `dm_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dm_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'dn_000' AS feature_name,
  SUM(CASE WHEN `dn_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dn_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'do_000' AS feature_name,
  SUM(CASE WHEN `do_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `do_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'dp_000' AS feature_name,
  SUM(CASE WHEN `dp_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dp_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'dq_000' AS feature_name,
  SUM(CASE WHEN `dq_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dq_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'dr_000' AS feature_name,
  SUM(CASE WHEN `dr_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dr_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ds_000' AS feature_name,
  SUM(CASE WHEN `ds_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ds_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'dt_000' AS feature_name,
  SUM(CASE WHEN `dt_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dt_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'du_000' AS feature_name,
  SUM(CASE WHEN `du_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `du_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'dv_000' AS feature_name,
  SUM(CASE WHEN `dv_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dv_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'dx_000' AS feature_name,
  SUM(CASE WHEN `dx_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dx_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'dy_000' AS feature_name,
  SUM(CASE WHEN `dy_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dy_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'dz_000' AS feature_name,
  SUM(CASE WHEN `dz_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `dz_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ea_000' AS feature_name,
  SUM(CASE WHEN `ea_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ea_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'eb_000' AS feature_name,
  SUM(CASE WHEN `eb_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `eb_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ec_00' AS feature_name,
  SUM(CASE WHEN `ec_00` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ec_00` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ed_000' AS feature_name,
  SUM(CASE WHEN `ed_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ed_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ee_000' AS feature_name,
  SUM(CASE WHEN `ee_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ee_001' AS feature_name,
  SUM(CASE WHEN `ee_001` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_001` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ee_002' AS feature_name,
  SUM(CASE WHEN `ee_002` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_002` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ee_003' AS feature_name,
  SUM(CASE WHEN `ee_003` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_003` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ee_004' AS feature_name,
  SUM(CASE WHEN `ee_004` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_004` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ee_005' AS feature_name,
  SUM(CASE WHEN `ee_005` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_005` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ee_006' AS feature_name,
  SUM(CASE WHEN `ee_006` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_006` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ee_007' AS feature_name,
  SUM(CASE WHEN `ee_007` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_007` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ee_008' AS feature_name,
  SUM(CASE WHEN `ee_008` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_008` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ee_009' AS feature_name,
  SUM(CASE WHEN `ee_009` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ee_009` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'ef_000' AS feature_name,
  SUM(CASE WHEN `ef_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `ef_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
UNION ALL
SELECT
  'train' AS dataset,
  'by_class' AS summary_scope,
  `class` AS class_label,
  'eg_000' AS feature_name,
  SUM(CASE WHEN `eg_000` IS NULL THEN 1 ELSE 0 END) AS missing_count,
  COUNT(*) AS total_count,
  SUM(CASE WHEN `eg_000` IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_rate
FROM `raw_aps_train`
GROUP BY `class`
)
SELECT *
FROM class_missing
ORDER BY feature_name, class_label;
