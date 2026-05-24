-- Day 19：Scania APS 预测结果业务分析建表脚本。
-- 本文件用于创建 Day19 业务分析相关表，配合手动导入 outputs/sql_exports/ 下的 CSV。
-- 注意：SQL 无法直接读取 config/config.yaml，导出的 CSV 已经固化了当前成本字段。
-- 如果后续在 SQL 中设置 @fp_cost / @fn_cost，需要人工保持与 config/config.yaml 一致。

USE scania_aps_project;

CREATE TABLE IF NOT EXISTS model_prediction_results (
    sample_id INT,
    dataset VARCHAR(50),
    model_version VARCHAR(100),
    strategy VARCHAR(100),
    threshold DECIMAL(10,6),
    y_true TINYINT,
    y_proba DECIMAL(12,8),
    y_pred TINYINT,
    risk_level VARCHAR(20),
    suggested_action VARCHAR(50),
    confusion_type VARCHAR(5),
    fp_cost INT,
    fn_cost INT,
    sample_cost INT,
    probability_band VARCHAR(30),
    decile INT,
    created_at VARCHAR(30),
    INDEX idx_strategy(strategy),
    INDEX idx_risk_level(risk_level),
    INDEX idx_confusion_type(confusion_type),
    INDEX idx_decile(decile),
    INDEX idx_y_proba(y_proba)
);

CREATE TABLE IF NOT EXISTS model_policy_comparison (
    policy_name VARCHAR(120),
    dataset VARCHAR(50),
    threshold DECIMAL(10,6),
    fp INT,
    fn INT,
    tp INT,
    tn INT,
    fp_cost INT,
    fn_cost INT,
    fp_cost_total INT,
    fn_cost_total INT,
    total_cost INT,
    baseline_total_cost INT,
    cost_reduction INT,
    cost_reduction_rate DECIMAL(12,6),
    source_file VARCHAR(255),
    note TEXT,
    INDEX idx_policy_name(policy_name),
    INDEX idx_dataset(dataset)
);

CREATE TABLE IF NOT EXISTS threshold_sensitivity_results (
    threshold DECIMAL(10,6),
    predicted_positive_count INT,
    predicted_negative_count INT,
    tp INT,
    fp INT,
    tn INT,
    fn INT,
    precision_score DECIMAL(12,8),
    recall_score DECIMAL(12,8),
    f1_score DECIMAL(12,8),
    f2_score DECIMAL(12,8),
    fp_cost INT,
    fn_cost INT,
    total_cost INT,
    workload_rate DECIMAL(12,8),
    INDEX idx_threshold(threshold),
    INDEX idx_total_cost(total_cost)
);

-- 导入后建议检查：
-- SELECT COUNT(*) FROM model_prediction_results;
-- SELECT COUNT(*) FROM model_policy_comparison;
-- SELECT COUNT(*) FROM threshold_sensitivity_results;
