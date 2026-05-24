-- Day 19：业务成本策略对比。
-- 业务问题：不同策略的 FP / FN / total cost 差异是什么？
-- 注意：OOF 结果是 official train 内部 OOF 口径，不应与 official test 结果直接横向比较。

-- official test 策略与 naive_all_negative 的成本对比。
SELECT
    policy_name,
    dataset,
    threshold,
    fp,
    fn,
    fp_cost_total,
    fn_cost_total,
    total_cost,
    baseline_total_cost,
    cost_reduction,
    cost_reduction_rate,
    note
FROM model_policy_comparison
WHERE dataset = 'official_test'
ORDER BY total_cost ASC;

-- OOF 策略单独列出，避免混淆不同评估口径。
SELECT
    policy_name,
    dataset,
    threshold,
    fp,
    fn,
    fp_cost_total,
    fn_cost_total,
    total_cost,
    baseline_total_cost,
    cost_reduction,
    cost_reduction_rate,
    note
FROM model_policy_comparison
WHERE dataset = 'oof_train'
ORDER BY total_cost ASC;

-- 单独展示当前最终候选方案。
SELECT
    policy_name,
    dataset,
    threshold,
    fp,
    fn,
    total_cost,
    cost_reduction,
    cost_reduction_rate,
    note
FROM model_policy_comparison
WHERE policy_name = 'day14_structural_all_final_candidate';
