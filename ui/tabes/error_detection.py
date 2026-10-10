"""
Error Detection Tab — Upgraded UI that surfaces all AI features visibly.

Key additions vs original:
1. "🤖 AI Quality Report" button → generates LLM report
2. AI anomaly detection results rendered with scores and explanations
3. Strategy recommendation shown per-column in missing value section
4. Method badge shows whether SBERT or fuzzy is active
"""

import streamlit as st
import pandas as pd

# ── AI imports ────────────────────────────────────────────────────────────────
try:
    from ai.llm_advisor import render_quality_report, render_strategy_card
    from ai.anomaly_detector import render_anomaly_results
    _AI_AVAILABLE = True
except ImportError:
    _AI_AVAILABLE = False
# ─────────────────────────────────────────────────────────────────────────────

from services.error_detection import detect_errors_and_issues
from utils.data_utils import infer_column_types


def render_error_detection_tab(
    uploaded_file,
    delimiter: str,
    use_ai_suggestions: bool,
    excel_sheet: str = "",
):
    """Render the error detection tab with AI-powered analysis."""
    st.subheader("🚨 Error Detection & Data Quality")

    if uploaded_file is None:
        st.info("Please upload a file to begin error detection.")
        return

    # ── Load data from session state (already loaded by home tab) ────────────
    df = st.session_state.get("current_df")
    if df is None:
        st.info("Please upload and load a file from the 🏠 Home tab first.")
        return

    # ── AI Quality Report button ───────────────────────────────────────────────
    if _AI_AVAILABLE and use_ai_suggestions:
        col_report, col_badge = st.columns([3, 1])
        with col_badge:
            st.markdown(
                "<span style='background:#1a1a2e;border:1px solid #7c3aed;"
                "padding:4px 10px;border-radius:12px;font-size:12px;'>🤖 AI Active</span>",
                unsafe_allow_html=True,
            )
        with col_report:
            if st.button("🤖 Generate AI Quality Report", type="primary"):
                issues_for_report = detect_errors_and_issues(df, use_ai=True)
                render_quality_report(df, issues_for_report)

    st.markdown("---")

    # ── Run detection ─────────────────────────────────────────────────────────
    with st.spinner("Analyzing data quality..."):
        issues = detect_errors_and_issues(df, use_ai=use_ai_suggestions and _AI_AVAILABLE)

    # ── Summary metrics ───────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Missing Value Columns", len(issues["missing_values"]))
    col2.metric(
        "Anomalies Detected",
        issues["outliers"].get("__ai_total__", sum(
            v for k, v in issues["outliers"].items()
            if not k.startswith("__")
        ))
    )
    col3.metric("Duplicate Rows", issues["duplicates"].get("exact", 0))
    col4.metric("Format Issues", len(issues["format_issues"]))

    if issues["outliers"].get("__ai_method__"):
        st.caption(f"Detection engine: **{issues['outliers']['__ai_method__']}**")

    st.markdown("---")

    # ── Tabs for each issue type ──────────────────────────────────────────────
    tab_missing, tab_anomalies, tab_duplicates, tab_format = st.tabs([
        "❓ Missing Values",
        "🚨 Anomalies / Outliers",
        "👥 Duplicates",
        "📝 Format Issues",
    ])

    # ── Missing Values ────────────────────────────────────────────────────────
    with tab_missing:
        st.markdown("#### ❓ Missing Values by Column")
        if not issues["missing_values"]:
            st.success("✅ No missing values detected.")
        else:
            mv_data = [
                {
                    "Column": col,
                    "Missing Count": info["count"],
                    "Missing %": f"{info['percentage']}%",
                }
                for col, info in issues["missing_values"].items()
            ]
            st.dataframe(pd.DataFrame(mv_data), use_container_width=True)

            # AI strategy recommendation per column
            if _AI_AVAILABLE and use_ai_suggestions:
                st.markdown("#### 🧠 AI-Recommended Cleaning Strategy")
                col_select = st.selectbox(
                    "Select a column to get AI advice:",
                    list(issues["missing_values"].keys()),
                )
                if col_select:
                    render_strategy_card(df, col_select)

    # ── Anomalies ─────────────────────────────────────────────────────────────
    with tab_anomalies:
        st.markdown("#### 🚨 Anomaly / Outlier Detection")
        ai_result = issues.get("ai_anomaly_result")

        if ai_result:
            render_anomaly_results(df, ai_result, show_llm_explanation=use_ai_suggestions)
        else:
            # Fallback: show IQR-based results as before
            outliers = {k: v for k, v in issues["outliers"].items() if not k.startswith("__")}
            if not outliers:
                st.success("✅ No outliers detected.")
            else:
                st.dataframe(
                    pd.DataFrame(
                        [{"Column": c, "Outlier Count": n} for c, n in outliers.items()]
                    ),
                    use_container_width=True,
                )

    # ── Duplicates ────────────────────────────────────────────────────────────
    with tab_duplicates:
        st.markdown("#### 👥 Duplicate Rows")
        exact = issues["duplicates"].get("exact", 0)
        if exact == 0:
            st.success("✅ No exact duplicate rows found.")
        else:
            st.warning(f"Found **{exact}** exact duplicate rows.")
            dup_preview = df[df.duplicated(keep=False)].head(20)
            st.dataframe(dup_preview, use_container_width=True)

    # ── Format Issues ─────────────────────────────────────────────────────────
    with tab_format:
        st.markdown("#### 📝 Format Issues")
        if not issues["format_issues"]:
            st.success("✅ No format issues detected.")
        else:
            fmt_data = []
            for col, info in issues["format_issues"].items():
                if "error" not in info:
                    fmt_data.append({
                        "Column": col,
                        "Leading Spaces": info.get("leading_spaces", 0),
                        "Trailing Spaces": info.get("trailing_spaces", 0),
                    })
            if fmt_data:
                st.dataframe(pd.DataFrame(fmt_data), use_container_width=True)