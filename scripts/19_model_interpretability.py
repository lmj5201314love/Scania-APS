"""Day21：模型解释性、SHAP 分析和展示审计。

本脚本只复现 Day14 final candidate 用于解释，不调参、不重新选择阈值、
不根据解释结果修改模型，也不修改 data/raw/。
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from scania_aps.config import get_config
from scania_aps.interpretability.model_interpretability import (
    EXPECTED_DAY14_FN,
    EXPECTED_DAY14_FP,
    EXPECTED_DAY14_TOTAL_COST,
    FINAL_THRESHOLD,
    build_case_explanation_tables,
    build_shap_sample,
    compute_permutation_importance_on_sample,
    compute_shap_values,
    compute_xgb_feature_importance,
    load_structural_config,
    reproduce_final_candidate_model,
    summarize_feature_family_importance,
    summarize_shap_importance,
)


def _ensure_dirs(*paths: Path) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def _save_table(table: pd.DataFrame, path: Path) -> None:
    table.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"[TABLE] {path} shape={table.shape}")


def _save_figure(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=180, bbox_inches="tight")
    plt.close()
    print(f"[FIGURE] {path}")


def _barh_top(
    df: pd.DataFrame,
    *,
    value_col: str,
    label_col: str,
    title: str,
    xlabel: str,
    output_path: Path,
    top_n: int = 20,
    color: str = "#4c78a8",
) -> None:
    plot_df = df.head(top_n).iloc[::-1].copy()
    plt.figure(figsize=(9, 6))
    plt.barh(plot_df[label_col], plot_df[value_col], color=color)
    plt.xlabel(xlabel)
    plt.title(title)
    plt.grid(axis="x", alpha=0.25)
    _save_figure(output_path)


def plot_xgb_gain_importance(importance: pd.DataFrame, figure_dir: Path) -> None:
    _barh_top(
        importance,
        value_col="importance_gain",
        label_col="feature_name",
        title="XGBoost Gain Importance Top 20",
        xlabel="Gain importance",
        output_path=figure_dir / "final_xgb_gain_importance_top20.png",
        color="#4c78a8",
    )


def plot_permutation_importance(importance: pd.DataFrame, figure_dir: Path) -> None:
    _barh_top(
        importance,
        value_col="average_precision_drop",
        label_col="feature_name",
        title="Permutation Importance Top 20",
        xlabel="Average precision drop",
        output_path=figure_dir / "final_permutation_importance_top20.png",
        color="#d97706",
    )


def plot_shap_bar(shap_importance: pd.DataFrame, figure_dir: Path) -> None:
    _barh_top(
        shap_importance,
        value_col="mean_abs_shap",
        label_col="feature_name",
        title="SHAP Mean Absolute Value Top 20",
        xlabel="Mean |SHAP value|",
        output_path=figure_dir / "final_shap_bar_top20.png",
        color="#2f855a",
    )


def plot_shap_summary(
    shap_values: np.ndarray,
    X_sample: pd.DataFrame,
    shap_importance: pd.DataFrame,
    figure_dir: Path,
) -> None:
    try:
        import shap  # type: ignore
    except Exception as exc:
        _plot_placeholder(
            figure_dir / "final_shap_summary_top20.png",
            f"SHAP summary plot unavailable: {exc}",
        )
        return

    top_features = shap_importance.head(20)["feature_name"].tolist()
    indices = [X_sample.columns.get_loc(feature) for feature in top_features]
    plt.figure(figsize=(9, 6))
    shap.summary_plot(
        shap_values[:, indices],
        X_sample[top_features],
        feature_names=top_features,
        show=False,
        max_display=20,
    )
    plt.title("SHAP Summary Top 20")
    _save_figure(figure_dir / "final_shap_summary_top20.png")


def plot_feature_family_importance(family_summary: pd.DataFrame, figure_dir: Path) -> None:
    plot_df = family_summary.sort_values("mean_abs_shap_share", ascending=True).copy()
    value_col = (
        "mean_abs_shap_share"
        if plot_df["mean_abs_shap_share"].fillna(0).sum() > 0
        else "xgb_gain_share"
    )
    plt.figure(figsize=(8, 5))
    plt.barh(plot_df["feature_family"], plot_df[value_col], color="#6b7280")
    plt.xlabel("Importance share")
    plt.title("Feature Family Importance")
    plt.grid(axis="x", alpha=0.25)
    _save_figure(figure_dir / "final_feature_family_importance.png")


def _plot_placeholder(path: Path, message: str) -> None:
    plt.figure(figsize=(8, 4))
    plt.text(0.5, 0.5, message, ha="center", va="center", wrap=True)
    plt.axis("off")
    _save_figure(path)


def _top_feature_names(df: pd.DataFrame, value_col: str, top_n: int = 10) -> str:
    return ", ".join(df.head(top_n)["feature_name"].tolist())


def _family_lines(family_summary: pd.DataFrame) -> list[str]:
    lines = []
    for row in family_summary.head(8).itertuples():
        shap_share = (
            "NA"
            if pd.isna(row.mean_abs_shap_share)
            else f"{row.mean_abs_shap_share:.2%}"
        )
        lines.append(
            f"- {row.feature_family}: feature_count={int(row.feature_count)}, "
            f"xgb_gain_share={row.xgb_gain_share:.2%}, mean_abs_shap_share={shap_share}."
        )
    return lines


def _case_observation(case_table: pd.DataFrame, label: str) -> str:
    if case_table.empty:
        return f"- {label}: no samples in the selected SHAP sample."
    top_features = (
        case_table["top_positive_shap_features"]
        .str.split("; ")
        .explode()
        .dropna()
        .str.split(":")
        .str[0]
        .value_counts()
        .head(5)
        .index.tolist()
    )
    return (
        f"- {label}: selected {len(case_table)} cases; frequent positive contributors include "
        f"{', '.join(top_features)}."
    )


def build_model_interpretability_report(
    *,
    reproduction_metrics: dict[str, Any],
    reproduction_note: str,
    xgb_importance: pd.DataFrame,
    permutation_importance: pd.DataFrame,
    shap_importance: pd.DataFrame,
    family_summary: pd.DataFrame,
    case_tables: dict[str, pd.DataFrame],
    shap_available: bool,
    shap_error: str | None,
) -> str:
    raw_top20 = xgb_importance.head(20)
    raw_count = int(raw_top20["feature_family"].eq("raw_feature").sum())
    structural_count = int(len(raw_top20) - raw_count)
    structural_names = raw_top20.loc[
        ~raw_top20["feature_family"].eq("raw_feature"),
        "feature_name",
    ].tolist()

    shap_section = (
        [
            "SHAP 已成功执行，以下结论来自抽样 official test 样本、全部 FN、Top 100 高风险样本和高置信 FP 的合并样本。",
            "",
            f"- SHAP mean_abs Top 10: {_top_feature_names(shap_importance, 'mean_abs_shap', 10)}.",
            f"- SHAP method note: {shap_error or 'shap.TreeExplainer'}",
        ]
        if shap_available
        else [
            "SHAP 未成功执行。",
            "",
            f"- 原因：{shap_error}",
            "- 已保留 XGBoost gain importance 和 permutation importance 作为解释性降级输出。",
        ]
    )

    lines = [
        "# Model Interpretability for Scania APS Predictive Maintenance",
        "",
        "本报告解释当前最终候选 Day14 `structural_all / median_all_structural_all`。本轮解释性分析不改变模型、不改变阈值，也不使用解释结果做模型选择。",
        "",
        "## 1. 解释对象",
        "",
        "- final candidate: Day14 `structural_all / median_all_structural_all`",
        f"- threshold: {FINAL_THRESHOLD:.2f}",
        f"- official test FP/FN/total_cost: {int(reproduction_metrics['fp'])} / {int(reproduction_metrics['fn'])} / {int(reproduction_metrics['total_cost'])}",
        f"- Day14 expected FP/FN/total_cost: {EXPECTED_DAY14_FP} / {EXPECTED_DAY14_FN} / {EXPECTED_DAY14_TOTAL_COST}",
        f"- reproduction note: {reproduction_note}",
        "",
        "## 2. 全局特征重要性：XGBoost Gain",
        "",
        f"- Top 20 gain importance features: {_top_feature_names(xgb_importance, 'importance_gain', 20)}.",
        f"- Top 20 中 raw features 数量：{raw_count}。",
        f"- Top 20 中 structural / indicator features 数量：{structural_count}。",
        f"- 进入前列的结构特征：{', '.join(structural_names) if structural_names else 'none'}。",
        "- 注意：匿名原始字段和前缀只表示脱敏字段名，不解释为真实传感器或物理部件。",
        "",
        "![XGBoost gain importance](../outputs/figures/final/final_xgb_gain_importance_top20.png)",
        "",
        "## 3. Permutation Importance",
        "",
        f"- AP drop Top 10: {_top_feature_names(permutation_importance, 'average_precision_drop', 10)}.",
        "- 如果 permutation importance 与 gain importance 不完全一致，常见原因包括特征相关性、树模型 split 偏好和匿名字段冗余。",
        "- permutation 只用于解释模型对特征扰动的敏感性，不用于筛特征或改模型。",
        "",
        "![Permutation importance](../outputs/figures/final/final_permutation_importance_top20.png)",
        "",
        "## 4. SHAP 全局解释",
        "",
        *shap_section,
        "",
        "SHAP 只解释模型评分贡献，不解释匿名字段的真实物理含义。",
        "",
        "![SHAP bar](../outputs/figures/final/final_shap_bar_top20.png)",
        "",
        "![SHAP summary](../outputs/figures/final/final_shap_summary_top20.png)",
        "",
        "## 5. Feature Family 贡献",
        "",
        *_family_lines(family_summary),
        "",
        "整体上可以用 feature family 判断模型主要依赖原始匿名数值字段，还是依赖 Day10-Day14 设计的结构特征。结构特征若进入重要性前列，说明缺失/零值/前缀聚合信号确实被模型利用；但这仍是统计解释，不是物理因果解释。",
        "",
        "![Feature family importance](../outputs/figures/final/final_feature_family_importance.png)",
        "",
        "## 6. FN / FP / TP case analysis",
        "",
        _case_observation(case_tables["fn"], "FN case analysis"),
        _case_observation(case_tables["high_risk_tp"], "High-risk TP case analysis"),
        _case_observation(case_tables["high_confidence_fp"], "High-confidence FP case analysis"),
        "",
        "局部解释表用于人工复核：`sample_id` 是匿名样本编号，不是真实车辆 ID；top SHAP features 是模型评分层面的贡献，不代表真实物理故障原因。",
        "",
        "相关表：",
        "",
        "- `outputs/tables/final/final_fn_shap_case_analysis.csv`",
        "- `outputs/tables/final/final_high_risk_tp_shap_case_analysis.csv`",
        "- `outputs/tables/final/final_high_confidence_fp_shap_case_analysis.csv`",
        "",
        "## 7. 面试可讲结论",
        "",
        "- 模型不是完全黑箱：XGBoost gain、permutation 和 SHAP 可以解释模型评分依赖哪些匿名字段和结构特征。",
        "- 字段匿名限制了物理解释，所以只能讲“模型评分贡献”和“统计结构信号”，不能讲真实传感器含义。",
        "- 结构特征的重要性可以验证 Day10-Day14 的缺失/零值/前缀聚合分析是否被模型实际利用。",
        "- SQL / Top-K 业务分析仍然必要，因为解释性告诉我们模型为何打分，业务分析告诉维修团队如何排队检查。",
        "- FN 和高置信 FP 的局部解释可以支持人工复核和后续诊断，但不能反向改阈值或模型。",
        "",
    ]
    return "\n".join(lines)


def build_readme_presentation_audit() -> str:
    return "\n".join(
        [
            "# README Presentation Audit for Day22",
            "",
            "本审计不重写 README，只为 Day22 最终 README 改版提供具体方案。",
            "",
            "## 1. 当前 README 主要问题",
            "",
            "- 核心结果仍容易让读者先看到 Day6 test 回溯的 8640，应该把它移到 historical / sensitivity observation。",
            "- Day14 final candidate 的主结果已经补充，但还需要在 README 顶部形成唯一主结果块。",
            "- Day20 final figures 已插入 preview，但最终 README 需要把图放到对应业务章节，而不是集中堆放。",
            "- 早期表格和历史过程较长，阅读路径偏 day-by-day 日志，面试官不一定能快速抓住最终结论。",
            "- 失败实验和未采纳方案需要更清晰地集中说明，例如 Day16 tuned 未泛化、Day18 ensemble 未通过 OOF 筛选。",
            "- How to Run 目前偏早期脚本，需要补一个简洁版主线入口。",
            "- 缺少最终目录导航：数据、配置、脚本、notebooks、reports、outputs 分别看哪里。",
            "",
            "## 2. 与 jvirico README 的差距",
            "",
            "- 对方 README 的 problem definition 更靠前，读者能更快知道业务目标和成本函数。",
            "- process structure 更清晰，不只是按日期堆过程。",
            "- 每个实验阶段有 conclusions / notes，便于判断为什么采用或放弃某个方法。",
            "- 图片嵌入在对应章节，而不是只在输出目录说明里出现。",
            "- 最终采用方案与尝试过但未采用的方法边界更清楚。",
            "",
            "## 3. Day22 README 建议结构",
            "",
            "1. Project Overview",
            "2. Business Problem",
            "3. Dataset & Cost Setting",
            "4. Final Result",
            "5. Why Not Accuracy",
            "6. Methodology",
            "7. Key Experiments and Model Selection Discipline",
            "8. Business Insights",
            "9. Interpretability",
            "10. SQL Analysis",
            "11. How to Run",
            "12. Project Structure",
            "13. Limitations",
            "14. Resume Highlights",
            "",
            "## 4. README 图表放置建议",
            "",
            "- Final Result：`outputs/figures/final/final_cost_policy_comparison.png`",
            "- Business Insights：`outputs/figures/final/final_topk_maintenance_capacity.png`",
            "- Business Insights：`outputs/figures/final/final_risk_level_workload.png`",
            "- Business Insights：`outputs/figures/final/final_decile_lift_gain.png`",
            "- Threshold Strategy：`outputs/figures/final/final_threshold_sensitivity.png`",
            "- Interpretability：`outputs/figures/final/final_shap_bar_top20.png`",
            "- Interpretability：`outputs/figures/final/final_feature_family_importance.png`",
            "",
            "## 5. OOF / Ensemble 应如何写",
            "",
            "- 不放在核心结果。",
            "- 放在 robustness checks。",
            "- 写清楚：OOF ensemble 最低 cost 略有下降，但 FN 增加，不符合补漏目标。",
            "- 因此 Day18 未进入 official test。",
            "- 不要把 OOF cost 与 official test cost 直接横向比较。",
            "",
            "## 6. 需要删除或迁移的内容",
            "",
            "- Day6 回溯结果从核心位置移走，迁移到 historical sensitivity observation。",
            "- 大量过程表格移到 `reports/summary.md`。",
            "- Notebook 列表不要占 README 过多空间，只保留主线 notebook 和完整索引链接。",
            "- 中间 outputs 不要全部放 README，详细清单保留在 `outputs/README_outputs.md`。",
            "- raw data 是否应从 Git tracking 中移除，留到 Day22 cleanup 处理；如保留，需说明数据来源和文件大小。",
            "",
        ]
    )


def save_reports(
    report_dir: Path,
    *,
    reproduction_metrics: dict[str, Any],
    reproduction_note: str,
    xgb_importance: pd.DataFrame,
    permutation_importance: pd.DataFrame,
    shap_importance: pd.DataFrame,
    family_summary: pd.DataFrame,
    case_tables: dict[str, pd.DataFrame],
    shap_available: bool,
    shap_error: str | None,
) -> None:
    model_report = build_model_interpretability_report(
        reproduction_metrics=reproduction_metrics,
        reproduction_note=reproduction_note,
        xgb_importance=xgb_importance,
        permutation_importance=permutation_importance,
        shap_importance=shap_importance,
        family_summary=family_summary,
        case_tables=case_tables,
        shap_available=shap_available,
        shap_error=shap_error,
    )
    model_report_path = report_dir / "model_interpretability.md"
    model_report_path.write_text(model_report, encoding="utf-8")
    print(f"[REPORT] {model_report_path}")

    audit_path = report_dir / "readme_presentation_audit.md"
    audit_path.write_text(build_readme_presentation_audit(), encoding="utf-8")
    print(f"[REPORT] {audit_path}")


def _empty_shap_importance(feature_names: list[str]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "feature_name": feature_names,
            "feature_family": ["unknown"] * len(feature_names),
            "mean_abs_shap": [0.0] * len(feature_names),
            "rank": range(1, len(feature_names) + 1),
            "direction_note": ["SHAP 未执行。"] * len(feature_names),
        }
    )


def main() -> None:
    cfg = get_config(PROJECT_ROOT / "config" / "config.yaml")
    structural_config = load_structural_config(PROJECT_ROOT / "config" / "structural_features.yaml")
    table_dir = cfg.tables_dir / "final"
    figure_dir = cfg.figures_dir / "final"
    _ensure_dirs(table_dir, figure_dir, cfg.reports_dir)

    reproduction = reproduce_final_candidate_model(cfg, structural_config)
    print("[INFO]", reproduction.reproduction_note)
    print(
        "[INFO] reproduced metrics:",
        {
            key: reproduction.metrics[key]
            for key in ["fp", "fn", "tp", "tn", "total_cost", "average_precision"]
        },
    )

    xgb_importance = compute_xgb_feature_importance(
        reproduction.trained_model,
        reproduction.feature_names,
    )
    top30_features = xgb_importance.head(30)["feature_name"].tolist()
    permutation_importance = compute_permutation_importance_on_sample(
        reproduction.trained_model,
        reproduction.X_test,
        reproduction.y_test,
        reproduction.feature_names,
        cfg,
        top_features=top30_features,
        sample_size=3000,
        random_state=cfg.random_state,
    )

    X_shap_sample, shap_metadata = build_shap_sample(
        reproduction.X_test,
        reproduction.test_predictions,
        random_state=cfg.random_state,
    )
    shap_result = compute_shap_values(
        reproduction.trained_model,
        X_shap_sample,
        reproduction.feature_names,
    )
    if shap_result.shap_available and shap_result.shap_values is not None:
        shap_importance = summarize_shap_importance(
            shap_result.shap_values,
            reproduction.feature_names,
        )
        case_tables = build_case_explanation_tables(
            shap_result.shap_values,
            X_shap_sample,
            shap_metadata,
            reproduction.feature_names,
        )
    else:
        shap_importance = _empty_shap_importance(reproduction.feature_names)
        empty_case_columns = [
            "sample_id",
            "y_true",
            "y_pred",
            "y_proba",
            "risk_level",
            "top_positive_shap_features",
            "top_negative_shap_features",
            "note",
        ]
        case_tables = {
            "fn": pd.DataFrame(columns=empty_case_columns),
            "high_risk_tp": pd.DataFrame(columns=empty_case_columns),
            "high_confidence_fp": pd.DataFrame(columns=empty_case_columns),
        }

    family_summary = summarize_feature_family_importance(
        xgb_importance,
        shap_importance if shap_result.shap_available else None,
        permutation_importance,
    )

    _save_table(
        xgb_importance.head(50),
        table_dir / "final_xgb_feature_importance_top50.csv",
    )
    _save_table(
        permutation_importance.head(30),
        table_dir / "final_permutation_importance_top30.csv",
    )
    _save_table(
        shap_importance.head(50),
        table_dir / "final_shap_mean_abs_top50.csv",
    )
    _save_table(
        family_summary,
        table_dir / "final_feature_family_importance_summary.csv",
    )
    _save_table(
        case_tables["fn"],
        table_dir / "final_fn_shap_case_analysis.csv",
    )
    _save_table(
        case_tables["high_risk_tp"],
        table_dir / "final_high_risk_tp_shap_case_analysis.csv",
    )
    _save_table(
        case_tables["high_confidence_fp"],
        table_dir / "final_high_confidence_fp_shap_case_analysis.csv",
    )

    plot_xgb_gain_importance(xgb_importance, figure_dir)
    plot_permutation_importance(permutation_importance, figure_dir)
    if shap_result.shap_available and shap_result.shap_values is not None:
        plot_shap_bar(shap_importance, figure_dir)
        plot_shap_summary(shap_result.shap_values, X_shap_sample, shap_importance, figure_dir)
    else:
        message = shap_result.error_message or "SHAP 未执行。"
        _plot_placeholder(figure_dir / "final_shap_bar_top20.png", message)
        _plot_placeholder(figure_dir / "final_shap_summary_top20.png", message)
    plot_feature_family_importance(family_summary, figure_dir)

    save_reports(
        cfg.reports_dir,
        reproduction_metrics=reproduction.metrics,
        reproduction_note=reproduction.reproduction_note,
        xgb_importance=xgb_importance,
        permutation_importance=permutation_importance,
        shap_importance=shap_importance,
        family_summary=family_summary,
        case_tables=case_tables,
        shap_available=shap_result.shap_available,
        shap_error=shap_result.error_message or shap_result.method,
    )

    print("Day21 interpretability outputs generated.")
    print("No hyperparameter tuning, threshold reselection, or raw data edit was performed.")


if __name__ == "__main__":
    main()
