"""
Error Detection — Upgraded to use the AI anomaly detector ensemble.

Changes from original:
- detect_errors_and_issues() now calls detect_anomalies_ensemble() instead of IQR only
- Anomaly results include scores, per-column breakdown, and LLM explanation hooks
- Outlier results are richer (score-based, not just count-based)
- All original functionality preserved; AI layer is additive
"""

import pandas as pd
import numpy as np
import logging
from utils.data_utils import infer_column_types
from services.cleaning import PLACEHOLDER_VALUES

# ── NEW: AI anomaly detector ──────────────────────────────────────────────────
try:
    from ai.anomaly_detector import detect_anomalies_ensemble
    _AI_AVAILABLE = True
except ImportError:
    _AI_AVAILABLE = False
# ─────────────────────────────────────────────────────────────────────────────

logger = logging.getLogger(__name__)


def detect_placeholder_values(df: pd.DataFrame) -> dict:
    """Detect placeholder values that should be treated as missing."""
    results = {"total_found": 0, "by_column": {}, "by_value": {}}

    for col in df.columns:
        col_placeholders = {}
        for idx, value in df[col].items():
            if pd.isna(value):
                continue
            str_value = str(value).strip()
            if str_value in PLACEHOLDER_VALUES:
                if str_value not in col_placeholders:
                    col_placeholders[str_value] = {"count": 0, "rows": []}
                col_placeholders[str_value]["count"] += 1
                col_placeholders[str_value]["rows"].append(idx)
                if str_value not in results["by_value"]:
                    results["by_value"][str_value] = 0
                results["by_value"][str_value] += 1
                results["total_found"] += 1
        if col_placeholders:
            results["by_column"][col] = col_placeholders

    return results


def detect_errors_and_issues(df: pd.DataFrame, use_ai: bool = True) -> dict:
    """
    Detect various data quality issues in the dataframe.

    Args:
        df: Input dataframe
        use_ai: If True, use ML ensemble for outlier detection (recommended)

    Returns:
        Dictionary containing detected issues by category.
        Outlier entries now include 'ai_result' key with full ensemble output.
    """
    issues = {
        "missing_values": {},
        "placeholder_values": {},
        "duplicates": {},
        "outliers": {},
        "inconsistencies": {},
        "format_issues": {},
        "ai_anomaly_result": None,   # ← NEW: full ML result stored here
    }

    # ── Missing values ────────────────────────────────────────────────────────
    for col in df.columns:
        missing_count = df[col].isnull().sum()
        if missing_count > 0:
            issues["missing_values"][col] = {
                "count": int(missing_count),
                "percentage": round(float(missing_count) / len(df) * 100, 2),
            }

    # ── Placeholder values ───────────────────────────────────────────────────
    placeholder_results = detect_placeholder_values(df)
    if placeholder_results["total_found"] > 0:
        issues["placeholder_values"] = placeholder_results

    # ── Duplicates ───────────────────────────────────────────────────────────
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        issues["duplicates"]["exact"] = int(dup_count)

    # ── Outlier / Anomaly Detection ──────────────────────────────────────────
    col_types = infer_column_types(df)
    numeric_cols = [c for c, t in col_types.items() if t == "numeric"]

    if numeric_cols:
        if use_ai and _AI_AVAILABLE:
            # ── AI ENSEMBLE PATH (IsolationForest + LOF) ──────────────────
            try:
                ai_result = detect_anomalies_ensemble(df, numeric_cols)
                issues["ai_anomaly_result"] = ai_result

                # Back-fill the per-column outlier counts for UI compatibility
                for col, info in ai_result.get("per_column_outliers", {}).items():
                    issues["outliers"][col] = info["extreme_count"]

                # Also store total anomaly count at top level for summary views
                issues["outliers"]["__ai_total__"] = ai_result["anomaly_count"]
                issues["outliers"]["__ai_method__"] = ai_result["method"]

            except Exception as e:
                logger.warning(f"AI anomaly detection failed, falling back to IQR: {e}")
                _iqr_fallback(df, numeric_cols, issues)
        else:
            # ── IQR FALLBACK PATH ─────────────────────────────────────────
            _iqr_fallback(df, numeric_cols, issues)

    # ── Format inconsistencies ───────────────────────────────────────────────
    for col in df.columns:
        try:
            if df[col].dtype == object:
                non_null = df[col].dropna()
                if len(non_null) > 0:
                    str_vals = non_null.astype(str)
                    has_leading = int(str_vals.str.startswith(" ").sum())
                    has_trailing = int(str_vals.str.endswith(" ").sum())
                    if has_leading > 0 or has_trailing > 0:
                        issues["format_issues"][col] = {
                            "leading_spaces": has_leading,
                            "trailing_spaces": has_trailing,
                        }
        except Exception as e:
            logger.error(f"Error processing column '{col}': {e}")
            issues["format_issues"][col] = {"error": "Unexpected error during analysis."}

    return issues


def _iqr_fallback(df: pd.DataFrame, numeric_cols: list, issues: dict):
    """Original IQR-based outlier detection as a fallback."""
    for col in numeric_cols:
        try:
            data = df[col].dropna()
            if len(data) > 0:
                Q1 = float(data.quantile(0.25))
                Q3 = float(data.quantile(0.75))
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                outlier_count = int(((data < lower) | (data > upper)).sum())
                if outlier_count > 0:
                    issues["outliers"][col] = outlier_count
        except Exception:
            continue
