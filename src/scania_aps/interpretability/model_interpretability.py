"""Day21 模型解释性分析工具。

本模块只用于复现 Day14 final candidate 并解释模型评分贡献；不调参、不重新选择阈值、
不根据解释结果修改模型或特征方案。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
import yaml
from sklearn.impute import SimpleImputer
from sklearn.metrics import average_precision_score, fbeta_score

from scania_aps.config import ScaniaConfig
from scania_aps.data.clean_data import split_features_target
from scania_aps.data.load_data import load_train_test_with_target
from scania_aps.data.split_data import split_train_valid
from scania_aps.evaluation.cost_utils import calculate_aps_cost
from scania_aps.evaluation.metrics import evaluate_binary_classifier
from scania_aps.features.structural_features import (
    StructuralFeatureBuilder,
    fit_structural_feature_builder,
    transform_structural_features,
)
from scania_aps.models.structural_feature_test_evaluation import _positive_class_proba
from scania_aps.models.train_advanced import (
    build_xgboost_model,
    calculate_scale_pos_weight,
)

FINAL_CANDIDATE_STRATEGY = "median_all_structural_all"
FINAL_THRESHOLD = 0.18
EXPECTED_DAY14_FP = 398
EXPECTED_DAY14_FN = 12
EXPECTED_DAY14_TOTAL_COST = 9980
RAW_FEATURE_PATTERN = r"^[a-z]{2}_[0-9]{3}$"


@dataclass(frozen=True)
class FinalCandidateReproduction:
    """Day14 final candidate 复现结果。"""

    trained_model: Any
    X_train: pd.DataFrame
    y_train: pd.Series
    X_test: pd.DataFrame
    y_test: pd.Series
    test_predictions: pd.DataFrame
    feature_names: list[str]
    feature_metadata: dict[str, Any]
    metrics: dict[str, Any]
    structural_builder: StructuralFeatureBuilder
    reproduction_note: str


@dataclass(frozen=True)
class ShapComputationResult:
    """SHAP 计算结果；当 shap 不可用时保存失败原因。"""

    shap_values: np.ndarray | None
    base_values: np.ndarray | float | None
    sample_metadata: pd.DataFrame
    shap_available: bool
    error_message: str | None = None
    method: str = "shap.TreeExplainer"


def load_structural_config(path: str | Path) -> dict[str, Any]:
    """读取结构特征配置。"""

    with Path(path).open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def _prepare_final_candidate_features(
    train_inner_df: pd.DataFrame,
    test_df: pd.DataFrame,
    cfg: ScaniaConfig,
    structural_config: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, StructuralFeatureBuilder, dict[str, Any]]:
    """按 Day14 逻辑构造 final candidate 特征矩阵。"""

    X_train_raw, y_train = split_features_target(train_inner_df, cfg.label_column)
    X_test_raw, y_test = split_features_target(test_df, cfg.label_column)

    imputer = SimpleImputer(strategy="median")
    X_train_original = pd.DataFrame(
        imputer.fit_transform(X_train_raw),
        columns=X_train_raw.columns.tolist(),
        index=X_train_raw.index,
    )
    X_test_original = pd.DataFrame(
        imputer.transform(X_test_raw),
        columns=X_train_raw.columns.tolist(),
        index=X_test_raw.index,
    )

    builder = fit_structural_feature_builder(
        train_inner_df=train_inner_df,
        cfg=cfg,
        structural_config=structural_config,
        feature_group=FINAL_CANDIDATE_STRATEGY,
    )
    X_train_structural = transform_structural_features(train_inner_df, builder)
    X_test_structural = transform_structural_features(test_df, builder)

    X_train = pd.concat([X_train_original, X_train_structural], axis=1)
    X_test = pd.concat([X_test_original, X_test_structural], axis=1)
    metadata = {
        "candidate_group": FINAL_CANDIDATE_STRATEGY,
        "threshold": FINAL_THRESHOLD,
        "threshold_source": "day13_valid_best_summary",
        "fit_dataset": "train_inner",
        "evaluation_dataset": "official_test",
        "n_original_features": X_train_original.shape[1],
        "n_structural_features": X_train_structural.shape[1],
        "n_total_features": X_train.shape[1],
        "structural_feature_names": X_train_structural.columns.tolist(),
        "selected_missing_indicator_columns": builder.selected_missing_indicator_columns,
        "prefix_missing_groups": list(builder.prefix_missing_members.keys()),
        "prefix_zero_groups": list(builder.prefix_zero_members.keys()),
        "uses_official_test_for_selection": False,
    }
    if builder.metadata:
        metadata.update(builder.metadata)
    return X_train, X_test, y_train.copy(), y_test.copy(), builder, metadata


def _build_prediction_metadata(
    y_true: pd.Series,
    y_proba: np.ndarray,
    cfg: ScaniaConfig,
) -> pd.DataFrame:
    """生成解释性分析需要的 official test 样本 metadata。"""

    y_pred = (y_proba >= FINAL_THRESHOLD).astype(int)
    result = pd.DataFrame(
        {
            "sample_id": np.arange(1, len(y_true) + 1),
            "dataset": "official_test",
            "model_version": "day14_structural_all_final_candidate",
            "strategy": FINAL_CANDIDATE_STRATEGY,
            "threshold": FINAL_THRESHOLD,
            "y_true": y_true.to_numpy(),
            "y_proba": y_proba,
            "y_pred": y_pred,
        }
    )
    result["confusion_type"] = np.select(
        [
            (result["y_true"] == 1) & (result["y_pred"] == 1),
            (result["y_true"] == 0) & (result["y_pred"] == 1),
            (result["y_true"] == 0) & (result["y_pred"] == 0),
            (result["y_true"] == 1) & (result["y_pred"] == 0),
        ],
        ["TP", "FP", "TN", "FN"],
        default="Unknown",
    )
    result["risk_level"] = np.select(
        [
            result["y_proba"] >= 0.80,
            (result["y_proba"] >= FINAL_THRESHOLD) & (result["y_proba"] < 0.80),
            (result["y_proba"] >= 0.05) & (result["y_proba"] < FINAL_THRESHOLD),
            result["y_proba"] < 0.05,
        ],
        ["Critical", "High", "Medium", "Low"],
        default="Unknown",
    )
    result["sample_cost"] = np.select(
        [result["confusion_type"].eq("FP"), result["confusion_type"].eq("FN")],
        [cfg.false_positive_cost, cfg.false_negative_cost],
        default=0,
    )
    return result


def reproduce_final_candidate_model(
    cfg: ScaniaConfig,
    structural_config: dict[str, Any],
) -> FinalCandidateReproduction:
    """复现 Day14 final candidate，用于解释性分析。

    该函数会重新 fit 一次同配置模型，但不调参、不改阈值、不使用解释结果做选择。
    """

    train_df, test_df = load_train_test_with_target(cfg)
    train_inner_df, _valid_df = split_train_valid(train_df, cfg)
    X_train, X_test, y_train, y_test, builder, metadata = _prepare_final_candidate_features(
        train_inner_df=train_inner_df,
        test_df=test_df,
        cfg=cfg,
        structural_config=structural_config,
    )
    scale_pos_weight = calculate_scale_pos_weight(y_train)
    model = build_xgboost_model(cfg, scale_pos_weight=scale_pos_weight)
    model.fit(X_train, y_train)

    y_proba = _positive_class_proba(model, X_test)
    y_pred = (y_proba >= FINAL_THRESHOLD).astype(int)
    metrics = evaluate_binary_classifier(
        y_true=y_test,
        y_pred=y_pred,
        y_proba=y_proba,
        cfg=cfg,
        model_name="xgboost_scale_pos_weight",
        strategy=FINAL_CANDIDATE_STRATEGY,
        threshold=FINAL_THRESHOLD,
    )
    test_predictions = _build_prediction_metadata(y_test, y_proba, cfg)

    matches_expected = (
        int(metrics["fp"]) == EXPECTED_DAY14_FP
        and int(metrics["fn"]) == EXPECTED_DAY14_FN
        and int(metrics["total_cost"]) == EXPECTED_DAY14_TOTAL_COST
    )
    note = (
        "复现结果与 Day14 official test 指标一致。"
        if matches_expected
        else (
            "复现结果与 Day14 指标存在差异，可能来自 XGBoost 版本、线程或环境随机性；"
            "该模型仍只用于解释性分析。"
        )
    )
    metadata["scale_pos_weight"] = scale_pos_weight
    metadata["reproduced_fp"] = int(metrics["fp"])
    metadata["reproduced_fn"] = int(metrics["fn"])
    metadata["reproduced_total_cost"] = int(metrics["total_cost"])
    metadata["matches_expected_day14"] = matches_expected

    return FinalCandidateReproduction(
        trained_model=model,
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_test,
        test_predictions=test_predictions,
        feature_names=X_train.columns.tolist(),
        feature_metadata=metadata,
        metrics=metrics,
        structural_builder=builder,
        reproduction_note=note,
    )


def categorize_feature(feature_name: str) -> str:
    """按技术来源粗略归类特征，不解释匿名字段物理含义。"""

    feature = str(feature_name)
    if pd.Series([feature]).str.match(RAW_FEATURE_PATTERN).iloc[0]:
        return "raw_feature"
    if feature.startswith("missing_"):
        return "missing_indicator"
    if feature.startswith("sample_missing") or feature.startswith("sample_zero") or feature.startswith("sample_non_"):
        return "sample_structural_feature"
    if feature.startswith("prefix_") and "_missing_" in feature:
        return "prefix_missing_feature"
    if feature.startswith("prefix_") and "_zero_" in feature:
        return "prefix_zero_feature"
    if feature.startswith("bin_") or "_bin_" in feature or feature.endswith("_high_bin_share"):
        return "bin_projection_feature"
    if feature.startswith("prefix_") or feature.startswith("sample_"):
        return "other_structural_feature"
    return "unknown"


def _booster_score_for_feature(score: dict[str, float], feature_name: str, index: int) -> float:
    """兼容 xgboost 返回真实列名或 f0/f1 索引名的情况。"""

    return float(score.get(feature_name, score.get(f"f{index}", 0.0)))


def compute_xgb_feature_importance(model: Any, feature_names: list[str]) -> pd.DataFrame:
    """计算 XGBoost weight/gain/cover importance，主排序使用 gain。"""

    booster = model.get_booster()
    scores = {
        "weight": booster.get_score(importance_type="weight"),
        "gain": booster.get_score(importance_type="gain"),
        "cover": booster.get_score(importance_type="cover"),
    }
    rows = []
    for index, feature_name in enumerate(feature_names):
        rows.append(
            {
                "feature_name": feature_name,
                "feature_family": categorize_feature(feature_name),
                "importance_weight": _booster_score_for_feature(
                    scores["weight"],
                    feature_name,
                    index,
                ),
                "importance_gain": _booster_score_for_feature(
                    scores["gain"],
                    feature_name,
                    index,
                ),
                "importance_cover": _booster_score_for_feature(
                    scores["cover"],
                    feature_name,
                    index,
                ),
            }
        )
    result = pd.DataFrame(rows).sort_values(
        ["importance_gain", "importance_weight", "feature_name"],
        ascending=[False, False, True],
    )
    result["rank_by_gain"] = range(1, len(result) + 1)
    return result.reset_index(drop=True)


def _sample_eval_frame(
    X_eval: pd.DataFrame,
    y_eval: pd.Series,
    sample_size: int,
    random_state: int,
) -> tuple[pd.DataFrame, pd.Series]:
    if len(X_eval) <= sample_size:
        return X_eval.copy(), y_eval.copy()
    rng = np.random.default_rng(random_state)
    indices = rng.choice(np.arange(len(X_eval)), size=sample_size, replace=False)
    return X_eval.iloc[indices].copy(), y_eval.iloc[indices].copy()


def compute_permutation_importance_on_sample(
    model: Any,
    X_eval: pd.DataFrame,
    y_eval: pd.Series,
    feature_names: list[str],
    cfg: ScaniaConfig,
    top_features: Iterable[str] | None = None,
    sample_size: int = 3000,
    random_state: int = 42,
) -> pd.DataFrame:
    """在 official test 抽样子集上计算 permutation importance。"""

    selected_features = list(top_features) if top_features is not None else list(feature_names)
    X_sample, y_sample = _sample_eval_frame(X_eval, y_eval, sample_size, random_state)
    y_proba = _positive_class_proba(model, X_sample)
    y_pred = (y_proba >= FINAL_THRESHOLD).astype(int)
    baseline_ap = average_precision_score(y_sample, y_proba)
    baseline_f2 = fbeta_score(y_sample, y_pred, beta=2, zero_division=0)
    baseline_cost = calculate_aps_cost(y_sample, y_pred, cfg)["total_cost"]

    rng = np.random.default_rng(random_state)
    rows = []
    for rank, feature_name in enumerate(selected_features, start=1):
        if feature_name not in X_sample.columns:
            continue
        X_permuted = X_sample.copy()
        X_permuted[feature_name] = rng.permutation(X_permuted[feature_name].to_numpy())
        permuted_proba = _positive_class_proba(model, X_permuted)
        permuted_pred = (permuted_proba >= FINAL_THRESHOLD).astype(int)
        permuted_ap = average_precision_score(y_sample, permuted_proba)
        permuted_f2 = fbeta_score(y_sample, permuted_pred, beta=2, zero_division=0)
        permuted_cost = calculate_aps_cost(y_sample, permuted_pred, cfg)["total_cost"]
        rows.append(
            {
                "feature_name": feature_name,
                "feature_family": categorize_feature(feature_name),
                "baseline_average_precision": baseline_ap,
                "permuted_average_precision": permuted_ap,
                "average_precision_drop": baseline_ap - permuted_ap,
                "baseline_f2": baseline_f2,
                "permuted_f2": permuted_f2,
                "f2_drop": baseline_f2 - permuted_f2,
                "baseline_total_cost": baseline_cost,
                "permuted_total_cost": permuted_cost,
                "total_cost_increase": permuted_cost - baseline_cost,
                "candidate_rank_by_gain": rank,
            }
        )
    result = pd.DataFrame(rows).sort_values(
        ["average_precision_drop", "f2_drop", "total_cost_increase"],
        ascending=[False, False, False],
    )
    result["rank"] = range(1, len(result) + 1)
    return result.reset_index(drop=True)


def build_shap_sample(
    X_test: pd.DataFrame,
    test_predictions: pd.DataFrame,
    *,
    random_sample_size: int = 2000,
    top_k_high_risk: int = 100,
    high_confidence_fp_threshold: float = 0.80,
    max_sample_size: int = 3500,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """构造 SHAP 解释样本：随机样本 + 全部 FN + Top risk + 高置信 FP。"""

    metadata = test_predictions.copy().reset_index(drop=True)
    rng = np.random.default_rng(random_state)
    random_n = min(random_sample_size, len(metadata))
    random_indices = set(rng.choice(metadata.index.to_numpy(), size=random_n, replace=False))
    fn_indices = set(metadata.index[metadata["confusion_type"].eq("FN")].tolist())
    top_indices = set(
        metadata.sort_values(["y_proba", "sample_id"], ascending=[False, True])
        .head(top_k_high_risk)
        .index.tolist()
    )
    high_conf_fp_indices = set(
        metadata.index[
            metadata["confusion_type"].eq("FP")
            & metadata["y_proba"].ge(high_confidence_fp_threshold)
        ].tolist()
    )
    selected = sorted(random_indices | fn_indices | top_indices | high_conf_fp_indices)
    if len(selected) > max_sample_size:
        required = sorted(fn_indices | top_indices | high_conf_fp_indices)
        optional = [idx for idx in selected if idx not in set(required)]
        keep_optional = max(0, max_sample_size - len(required))
        selected = sorted(required + optional[:keep_optional])

    X_sample = X_test.iloc[selected].copy()
    sample_metadata = metadata.iloc[selected].copy().reset_index(drop=True)
    X_sample.index = sample_metadata.index
    return X_sample, sample_metadata


def compute_shap_values(
    model: Any,
    X_sample: pd.DataFrame,
    feature_names: list[str],
) -> ShapComputationResult:
    """使用 shap.TreeExplainer 计算 SHAP values；不可用时返回清晰错误。"""

    try:
        import shap  # type: ignore
    except Exception as exc:  # pragma: no cover - 依赖缺失时的降级路径
        return ShapComputationResult(
            shap_values=None,
            base_values=None,
            sample_metadata=pd.DataFrame(index=X_sample.index),
            shap_available=False,
            error_message=f"无法导入 shap：{exc}",
        )

    X_numeric = X_sample[feature_names].apply(pd.to_numeric, errors="coerce")
    try:
        explainer = shap.TreeExplainer(model)
        values = explainer(X_numeric)
        shap_values = np.asarray(values.values)
        if shap_values.ndim == 3:
            shap_values = shap_values[:, :, -1]
        return ShapComputationResult(
            shap_values=shap_values,
            base_values=getattr(values, "base_values", None),
            sample_metadata=pd.DataFrame(index=X_sample.index),
            shap_available=True,
            method="shap.TreeExplainer",
        )
    except Exception as exc:  # pragma: no cover - 不同 shap/xgboost 版本错误不可稳定复现
        tree_explainer_error = exc

    try:
        import xgboost as xgb

        dmatrix = xgb.DMatrix(X_numeric, feature_names=feature_names)
        contributions = model.get_booster().predict(dmatrix, pred_contribs=True)
        shap_values = np.asarray(contributions[:, :-1])
        base_values = np.asarray(contributions[:, -1])
        return ShapComputationResult(
            shap_values=shap_values,
            base_values=base_values,
            sample_metadata=pd.DataFrame(index=X_sample.index),
            shap_available=True,
            error_message=(
                "shap.TreeExplainer 失败，已使用 XGBoost pred_contribs fallback："
                f"{tree_explainer_error}"
            ),
            method="xgboost.pred_contribs",
        )
    except Exception as fallback_exc:  # pragma: no cover - 依赖环境相关
        return ShapComputationResult(
            shap_values=None,
            base_values=None,
            sample_metadata=pd.DataFrame(index=X_sample.index),
            shap_available=False,
            error_message=(
                f"SHAP 计算失败：TreeExplainer={tree_explainer_error}; "
                f"pred_contribs fallback={fallback_exc}"
            ),
        )


def summarize_shap_importance(
    shap_values: np.ndarray,
    feature_names: list[str],
) -> pd.DataFrame:
    """按 mean absolute SHAP 汇总全局重要性。"""

    mean_abs = np.abs(shap_values).mean(axis=0)
    result = pd.DataFrame(
        {
            "feature_name": feature_names,
            "feature_family": [categorize_feature(name) for name in feature_names],
            "mean_abs_shap": mean_abs,
        }
    ).sort_values(["mean_abs_shap", "feature_name"], ascending=[False, True])
    result["rank"] = range(1, len(result) + 1)
    result["direction_note"] = "正负方向需结合样本级 SHAP 和特征值查看；不解释真实物理含义。"
    return result.reset_index(drop=True)


def summarize_feature_family_importance(
    xgb_importance: pd.DataFrame,
    shap_importance: pd.DataFrame | None = None,
    permutation_importance: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """聚合 feature family 贡献，用于全局解释。"""

    rows = []
    families = sorted(set(xgb_importance["feature_family"]))
    if shap_importance is not None and not shap_importance.empty:
        families = sorted(set(families) | set(shap_importance["feature_family"]))
    if permutation_importance is not None and not permutation_importance.empty:
        families = sorted(set(families) | set(permutation_importance["feature_family"]))

    for family in families:
        xgb_family = xgb_importance[xgb_importance["feature_family"].eq(family)]
        shap_family = (
            shap_importance[shap_importance["feature_family"].eq(family)]
            if shap_importance is not None and not shap_importance.empty
            else pd.DataFrame()
        )
        perm_family = (
            permutation_importance[permutation_importance["feature_family"].eq(family)]
            if permutation_importance is not None and not permutation_importance.empty
            else pd.DataFrame()
        )
        rows.append(
            {
                "feature_family": family,
                "feature_count": int(len(xgb_family)),
                "xgb_gain_total": float(xgb_family["importance_gain"].sum()),
                "xgb_gain_share": 0.0,
                "mean_abs_shap_total": float(shap_family["mean_abs_shap"].sum())
                if not shap_family.empty
                else np.nan,
                "mean_abs_shap_share": 0.0,
                "permutation_ap_drop_total": float(
                    perm_family["average_precision_drop"].clip(lower=0).sum()
                )
                if not perm_family.empty
                else np.nan,
            }
        )
    result = pd.DataFrame(rows)
    gain_total = result["xgb_gain_total"].sum()
    if gain_total:
        result["xgb_gain_share"] = result["xgb_gain_total"] / gain_total
    if "mean_abs_shap_total" in result.columns:
        shap_total = result["mean_abs_shap_total"].fillna(0).sum()
        if shap_total:
            result["mean_abs_shap_share"] = result["mean_abs_shap_total"].fillna(0) / shap_total
    return result.sort_values(
        ["mean_abs_shap_share", "xgb_gain_share"],
        ascending=[False, False],
    ).reset_index(drop=True)


def _format_feature_contributions(
    feature_names: list[str],
    values: np.ndarray,
    *,
    positive: bool,
    top_n: int,
) -> str:
    pairs = [
        (feature, float(value))
        for feature, value in zip(feature_names, values)
        if (value > 0 if positive else value < 0)
    ]
    pairs = sorted(pairs, key=lambda item: abs(item[1]), reverse=True)[:top_n]
    return "; ".join(f"{feature}: {value:.4f}" for feature, value in pairs)


def _case_rows(
    sample_metadata: pd.DataFrame,
    shap_values: np.ndarray,
    feature_names: list[str],
    mask: pd.Series,
    note: str,
    top_n_features_per_sample: int,
    limit: int,
    include_negative: bool = True,
) -> pd.DataFrame:
    selected = sample_metadata.loc[mask].sort_values(
        ["y_proba", "sample_id"],
        ascending=[False, True],
    ).head(limit)
    rows = []
    for idx, row in selected.iterrows():
        values = shap_values[idx]
        rows.append(
            {
                "sample_id": int(row["sample_id"]),
                "y_true": int(row["y_true"]),
                "y_pred": int(row["y_pred"]),
                "y_proba": float(row["y_proba"]),
                "risk_level": row["risk_level"],
                "top_positive_shap_features": _format_feature_contributions(
                    feature_names,
                    values,
                    positive=True,
                    top_n=top_n_features_per_sample,
                ),
                "top_negative_shap_features": _format_feature_contributions(
                    feature_names,
                    values,
                    positive=False,
                    top_n=top_n_features_per_sample,
                )
                if include_negative
                else "",
                "note": note,
            }
        )
    return pd.DataFrame(rows)


def build_case_explanation_tables(
    shap_values: np.ndarray,
    X_sample: pd.DataFrame,
    sample_metadata: pd.DataFrame,
    feature_names: list[str],
    top_n_features_per_sample: int = 10,
) -> dict[str, pd.DataFrame]:
    """生成 FN、high-risk TP 和 high-confidence FP 的局部解释表。"""

    del X_sample
    metadata = sample_metadata.reset_index(drop=True)
    fn = _case_rows(
        metadata,
        shap_values,
        feature_names,
        metadata["confusion_type"].eq("FN"),
        "FN 样本：模型评分未超过固定阈值 0.18，需人工复核漏报风险。",
        top_n_features_per_sample,
        limit=50,
    )
    tp = _case_rows(
        metadata,
        shap_values,
        feature_names,
        metadata["confusion_type"].eq("TP") & metadata["risk_level"].isin(["Critical", "High"]),
        "高风险 TP 样本：这些特征在模型评分层面推高风险。",
        top_n_features_per_sample,
        limit=50,
        include_negative=False,
    )
    fp = _case_rows(
        metadata,
        shap_values,
        feature_names,
        metadata["confusion_type"].eq("FP") & metadata["risk_level"].eq("Critical"),
        "高置信 FP 样本：模型评分被推高，但真实标签为 neg；不代表真实车辆故障。",
        top_n_features_per_sample,
        limit=50,
        include_negative=False,
    )
    return {
        "fn": fn,
        "high_risk_tp": tp,
        "high_confidence_fp": fp,
    }
