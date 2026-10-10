"""
Anomaly Detector Module — Replaces IQR threshold checks with a proper
ML ensemble: Isolation Forest + Local Outlier Factor.

Key upgrades over the current cleaning.py implementation:
1. Uses BOTH IsolationForest and LOF — ensemble voting reduces false positives
2. Returns anomaly SCORES (not just binary flags) — shows degree of anomaly
3. Per-column explanation of why each value is anomalous
4. Integrates with llm_advisor to explain findings in plain English
5. Contamination auto-estimated from data, not hardcoded at 0.03
"""

import pandas as pd
import numpy as np
import streamlit as st
import logging
from typing import Optional

from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# Core Detection
# ─────────────────────────────────────────────────────────────

def _estimate_contamination(series: pd.Series) -> float:
    """
    Auto-estimate contamination rate using IQR fence method.
    More accurate than hardcoding 0.03 for every dataset.
    """
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 3.0 * iqr  # Use 3× IQR for conservative estimate
    upper = q3 + 3.0 * iqr
    extreme_count = int(((series < lower) | (series > upper)).sum())
    rate = extreme_count / len(series)
    # Clamp to valid range for sklearn
    return max(0.01, min(0.45, rate)) if rate > 0 else 0.05


def detect_anomalies_ensemble(
    df: pd.DataFrame,
    numeric_cols: list,
    contamination: Optional[float] = None,
    random_state: int = 42,
    use_lof: bool = True,
) -> dict:
    """
    Detect anomalies using IsolationForest + LOF ensemble.

    Returns a rich result dict instead of just removing rows (like the
    old remove_outliers_isolationforest did). This is critical — you want
    to SHOW the user what was found before deciding to remove it.

    Args:
        df: Input dataframe
        numeric_cols: Columns to analyze
        contamination: Expected anomaly fraction (auto-estimated if None)
        random_state: For reproducibility
        use_lof: Whether to include LOF in the ensemble

    Returns:
        {
          "anomaly_mask": pd.Series (True = anomaly),
          "anomaly_scores": pd.Series (higher = more anomalous),
          "anomaly_count": int,
          "anomaly_indices": list,
          "per_column_outliers": dict,   ← which column contributed most
          "contamination_used": float,
          "method": str,
        }
    """
    if len(numeric_cols) == 0:
        return _empty_result("no_numeric_columns")

    # Fill NaN with median for fitting (we detect anomalies in real values)
    data = df[numeric_cols].copy()
    for col in numeric_cols:
        data[col] = data[col].fillna(data[col].median())

    # Convert bool columns
    for col in numeric_cols:
        if data[col].dtype == bool:
            data[col] = data[col].astype(int)

    arr = data.values.astype(float)

    # Scale for LOF (IsolationForest is scale-invariant, LOF is not)
    scaler = StandardScaler()
    arr_scaled = scaler.fit_transform(arr)

    # Auto-estimate contamination if not provided
    if contamination is None:
        per_col_rates = [
            _estimate_contamination(df[col].dropna())
            for col in numeric_cols
            if df[col].dropna().std() > 0
        ]
        contamination = float(np.median(per_col_rates)) if per_col_rates else 0.05

    try:
        # --- IsolationForest ---
        iso = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=100,
        )
        iso_preds = iso.fit_predict(arr)          # -1 = anomaly
        iso_scores = -iso.score_samples(arr)      # higher = more anomalous

        # --- LOF (optional) ---
        if use_lof and len(arr) >= 20:
            n_neighbors = min(20, len(arr) // 5)
            lof = LocalOutlierFactor(
                n_neighbors=n_neighbors,
                contamination=contamination,
            )
            lof_preds = lof.fit_predict(arr_scaled)   # -1 = anomaly
            lof_scores = -lof.negative_outlier_factor_  # higher = more anomalous
            # Normalize LOF scores to same range as Isolation Forest
            lof_scores = (lof_scores - lof_scores.min()) / (lof_scores.max() - lof_scores.min() + 1e-9)

            # Ensemble: flag if BOTH models agree it's an anomaly
            combined_mask = (iso_preds == -1) & (lof_preds == -1)
            combined_scores = (iso_scores / (iso_scores.max() + 1e-9) + lof_scores) / 2
            method = "IsolationForest + LOF ensemble"
        else:
            combined_mask = (iso_preds == -1)
            combined_scores = iso_scores / (iso_scores.max() + 1e-9)
            method = "IsolationForest"

        anomaly_indices = list(df.index[combined_mask])

        # Per-column contribution: which column pushed each row to be anomalous?
        per_column_outliers = _per_column_breakdown(df, numeric_cols, anomaly_indices)

        return {
            "anomaly_mask": pd.Series(combined_mask, index=df.index),
            "anomaly_scores": pd.Series(combined_scores, index=df.index),
            "anomaly_count": int(combined_mask.sum()),
            "anomaly_indices": anomaly_indices,
            "per_column_outliers": per_column_outliers,
            "contamination_used": contamination,
            "method": method,
        }

    except Exception as e:
        logger.error(f"Anomaly detection failed: {e}")
        return _empty_result(f"error: {e}")


def _per_column_breakdown(
    df: pd.DataFrame,
    numeric_cols: list,
    anomaly_indices: list,
) -> dict:
    """For each column, count how many anomalies had extreme values in it."""
    breakdown = {}
    if not anomaly_indices:
        return breakdown

    anomaly_rows = df.loc[anomaly_indices, numeric_cols]

    for col in numeric_cols:
        col_data = df[col].dropna()
        if len(col_data) == 0:
            continue
        q1, q3 = col_data.quantile(0.25), col_data.quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr

        extreme_in_col = anomaly_rows[col].dropna()
        extreme_count = int(((extreme_in_col < lower) | (extreme_in_col > upper)).sum())

        if extreme_count > 0:
            breakdown[col] = {
                "extreme_count": extreme_count,
                "lower_fence": round(float(lower), 4),
                "upper_fence": round(float(upper), 4),
                "example_values": [
                    round(float(v), 4) for v in
                    extreme_in_col[(extreme_in_col < lower) | (extreme_in_col > upper)].head(3).tolist()
                ],
            }

    return breakdown


def _empty_result(reason: str) -> dict:
    return {
        "anomaly_mask": pd.Series(dtype=bool),
        "anomaly_scores": pd.Series(dtype=float),
        "anomaly_count": 0,
        "anomaly_indices": [],
        "per_column_outliers": {},
        "contamination_used": 0.0,
        "method": reason,
    }


# ─────────────────────────────────────────────────────────────
# Apply (remove anomalies from dataframe)
# ─────────────────────────────────────────────────────────────

def remove_anomalies(df: pd.DataFrame, result: dict) -> tuple:
    """
    Remove flagged anomaly rows from dataframe.

    Args:
        df: Input dataframe
        result: Output from detect_anomalies_ensemble()

    Returns:
        (cleaned_df, removed_count)
    """
    indices_to_drop = result.get("anomaly_indices", [])
    df_clean = df.drop(index=indices_to_drop, errors="ignore").reset_index(drop=True)
    return df_clean, len(indices_to_drop)


# ─────────────────────────────────────────────────────────────
# Streamlit UI helpers
# ─────────────────────────────────────────────────────────────

def render_anomaly_results(
    df: pd.DataFrame,
    result: dict,
    show_llm_explanation: bool = True,
):
    """
    Render a full anomaly detection results panel in Streamlit.

    Shows: method used, count, score distribution, per-column breakdown,
    flagged rows preview, and optionally an LLM explanation.
    """
    if result["anomaly_count"] == 0:
        st.success("✅ No anomalies detected in the dataset.")
        return

    count = result["anomaly_count"]
    total = len(df)
    pct = round(count / total * 100, 2)

    col1, col2, col3 = st.columns(3)
    col1.metric("🚨 Anomalies Found", f"{count:,}")
    col2.metric("📊 Percentage", f"{pct}%")
    col3.metric("🔬 Method", result["method"].split("+")[0].strip())

    st.caption(f"Detection method: **{result['method']}** | Estimated contamination: `{result['contamination_used']:.3f}`")

    # Per-column breakdown
    if result["per_column_outliers"]:
        st.markdown("#### 📌 Columns Driving Anomalies")
        breakdown_data = []
        for col, info in result["per_column_outliers"].items():
            breakdown_data.append({
                "Column": col,
                "Extreme Values": info["extreme_count"],
                "Lower Fence": info["lower_fence"],
                "Upper Fence": info["upper_fence"],
                "Example Anomalous Values": str(info["example_values"]),
            })
        st.dataframe(pd.DataFrame(breakdown_data), use_container_width=True)

    # Preview of flagged rows
    st.markdown("#### 👁️ Preview of Flagged Rows")
    flagged_preview = df.loc[result["anomaly_indices"][:20]].copy()
    flagged_preview["anomaly_score"] = result["anomaly_scores"].loc[result["anomaly_indices"][:20]].round(4).values
    st.dataframe(flagged_preview.sort_values("anomaly_score", ascending=False), use_container_width=True)

    # LLM explanation (if enabled)
    if show_llm_explanation and result["per_column_outliers"]:
        worst_col = max(
            result["per_column_outliers"],
            key=lambda c: result["per_column_outliers"][c]["extreme_count"]
        )
        try:
            from ai.llm_advisor import render_anomaly_explanation
            render_anomaly_explanation(df, worst_col, result["anomaly_indices"])
        except ImportError:
            pass