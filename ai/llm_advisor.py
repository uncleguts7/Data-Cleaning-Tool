"""
LLM Advisor Module — Uses Groq API (free) instead of Anthropic.
"""

import os
import json
import pandas as pd
import numpy as np
import streamlit as st
import logging
from groq import Groq  # type: ignore

logger = logging.getLogger(__name__)
GROQ_MODEL = "llama-3.1-8b-instant"
_client = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found. Add it to your .env file.")
        _client = Groq(api_key=api_key)
    return _client


def _call_llm(prompt: str, max_tokens: int = 1000) -> str:
    client = _get_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


def _safe_sample(series: pd.Series, n: int = 8) -> list:
    non_null = series.dropna()
    if len(non_null) == 0:
        return []
    samples = non_null.sample(min(n, len(non_null)), random_state=42).tolist()
    return [x.item() if hasattr(x, "item") else x for x in samples]


def _build_column_profile(df: pd.DataFrame, column: str) -> dict:
    col = df[column]
    profile = {
        "name": column,
        "dtype": str(col.dtype),
        "total_rows": len(col),
        "missing_count": int(col.isnull().sum()),
        "missing_pct": round(col.isnull().mean() * 100, 2),
        "unique_count": int(col.nunique()),
        "sample_values": _safe_sample(col),
    }
    if pd.api.types.is_numeric_dtype(col):
        desc = col.describe()
        profile.update({
            "mean": round(float(desc["mean"]), 4) if not pd.isna(desc["mean"]) else None,
            "std": round(float(desc["std"]), 4) if not pd.isna(desc["std"]) else None,
            "min": float(desc["min"]) if not pd.isna(desc["min"]) else None,
            "max": float(desc["max"]) if not pd.isna(desc["max"]) else None,
            "iqr_outlier_count": int(
                ((col < (desc["25%"] - 1.5 * (desc["75%"] - desc["25%"]))) |
                 (col > (desc["75%"] + 1.5 * (desc["75%"] - desc["25%"])))).sum()
            ) if not pd.isna(desc["25%"]) else 0,
        })
    else:
        vc = col.value_counts()
        profile.update({
            "top_values": vc.head(5).to_dict(),
            "has_mixed_case": bool(
                col.dropna().astype(str).str.lower().nunique() <
                col.dropna().astype(str).nunique()
            ),
        })
    return profile


def suggest_cleaning_strategy(df: pd.DataFrame, column: str) -> dict:
    profile = _build_column_profile(df, column)
    prompt = f"""You are a data quality expert. Analyze this column profile and recommend the best cleaning strategy.

Column Profile:
{json.dumps(profile, indent=2)}

Respond ONLY with valid JSON matching this exact schema (no markdown fences, no extra text):
{{
  "strategy": "<one of: knn_impute | mode_impute | median_impute | mean_impute | forward_fill | drop_column | flag_only | semantic_impute>",
  "confidence": "<high | medium | low>",
  "reasoning": "<2-3 sentence plain English explanation>",
  "warnings": ["<concern 1>", "<concern 2>"],
  "params": {{}}
}}"""
    try:
        raw = _call_llm(prompt, max_tokens=512)
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)  # ← was "return json.loads(raw)"

        # Save learned pattern if AI is confident
        if result.get("confidence") == "high":
            from config.learned_patterns import save_pattern
            strategy = result.get("strategy", "")
            if strategy in ("knn_impute", "median_impute", "mean_impute"):
                save_pattern("integer_cols", column)
            elif strategy == "mode_impute":
                save_pattern("monetary_cols", column)
            elif strategy in ("flag_only", "drop_column"):
                save_pattern("id_cols", column)

        return result  # ← now returns here instead
    except Exception as e:
        logger.error(f"LLM strategy suggestion failed: {e}")
        return {
            "strategy": "mode_impute",
            "confidence": "low",
            "reasoning": "LLM unavailable — defaulting to mode imputation.",
            "warnings": [str(e)],
            "params": {}
        }
    
    except Exception as e:
        logger.error(f"LLM strategy suggestion failed: {e}")
        return {
            "strategy": "mode_impute",
            "confidence": "low",
            "reasoning": "LLM unavailable — defaulting to mode imputation.",
            "warnings": [str(e)],
            "params": {}
        }


def explain_anomalies(df: pd.DataFrame, column: str, anomaly_indices: list) -> str:
    if not anomaly_indices:
        return "No anomalies detected."
    col = df[column]
    normal_sample = _safe_sample(col.drop(index=anomaly_indices, errors="ignore"), n=5)
    anomaly_sample = _safe_sample(col.iloc[anomaly_indices] if anomaly_indices else col, n=5)
    prompt = f"""You are a data quality analyst. Explain these anomalies concisely.

Column: "{column}"
Normal value examples: {normal_sample}
Anomalous value examples: {anomaly_sample}
Total anomalies: {len(anomaly_indices)} out of {len(col)} rows ({round(len(anomaly_indices)/len(col)*100,1)}%)

Write 2-3 sentences: what pattern breaks, likely cause, and whether to remove or investigate.
Be specific about the values. No preamble."""
    try:
        return _call_llm(prompt, max_tokens=256)
    except Exception as e:
        logger.error(f"LLM anomaly explanation failed: {e}")
        return f"Anomaly explanation unavailable: {e}"


def generate_quality_report(df: pd.DataFrame, issues: dict) -> str:
    summary = {
        "rows": len(df),
        "columns": len(df.columns),
        "missing_columns": list(issues.get("missing_values", {}).keys()),
        "total_missing": sum(v["count"] for v in issues.get("missing_values", {}).values()),
        "duplicate_rows": issues.get("duplicates", {}).get("exact", 0),
        "outlier_columns": list(issues.get("outliers", {}).keys()),
        "format_issue_columns": list(issues.get("format_issues", {}).keys()),
        "column_names": df.columns.tolist()[:20],
    }
    prompt = f"""You are a senior data scientist writing a data quality report.

Dataset summary:
{json.dumps(summary, indent=2)}

Write a concise Markdown report with these exact sections:
## Overall Assessment
## Key Issues Found
## Recommended Cleaning Priority
## Risk Flags

Use actual column names and numbers. Max 300 words. No preamble."""
    try:
        return _call_llm(prompt, max_tokens=600)
    except Exception as e:
        logger.error(f"LLM quality report failed: {e}")
        return f"**Report generation failed:** {e}"


def smart_rename_suggestion(df: pd.DataFrame, column: str) -> dict:
    sample = _safe_sample(df[column], n=10)
    prompt = f"""Suggest a clean snake_case column name.
Current name: "{column}"
Data type: {str(df[column].dtype)}
Sample values: {sample}
Respond ONLY with JSON (no markdown): {{"suggested_name": "<name>", "reasoning": "<one sentence>"}}"""
    try:
        raw = _call_llm(prompt, max_tokens=128)
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        return {"suggested_name": column, "reasoning": f"LLM unavailable: {e}"}


# ── Streamlit UI helpers ──────────────────────────────────────

def render_strategy_card(df: pd.DataFrame, column: str):
    with st.spinner(f"🤖 Analyzing '{column}' with AI..."):
        result = suggest_cleaning_strategy(df, column)
    confidence_colors = {"high": "🟢", "medium": "🟡", "low": "🔴"}
    emoji = confidence_colors.get(result.get("confidence", "low"), "⚪")
    st.markdown(f"""
    <div style="border:1px solid #333; border-radius:8px; padding:16px; margin:8px 0; background:#1a1a2e;">
        <h4 style="margin:0 0 8px 0;">🧠 AI Recommendation: <code>{result.get('strategy','?')}</code> {emoji}</h4>
        <p style="margin:4px 0; color:#ccc;">{result.get('reasoning','')}</p>
    </div>
    """, unsafe_allow_html=True)
    if result.get("warnings"):
        for w in result["warnings"]:
            st.warning(f"⚠️ {w}")
    if result.get("params"):
        st.caption(f"Suggested parameters: `{result['params']}`")
    return result


def render_anomaly_explanation(df: pd.DataFrame, column: str, anomaly_indices: list):
    if not anomaly_indices:
        return
    with st.spinner("🤖 Generating anomaly explanation..."):
        explanation = explain_anomalies(df, column, anomaly_indices)
    st.info(f"🔍 **AI Anomaly Analysis:** {explanation}")


def render_quality_report(df: pd.DataFrame, issues: dict):
    with st.expander("🤖 AI Data Quality Report", expanded=True):
        with st.spinner("Generating report with AI..."):
            report = generate_quality_report(df, issues)
        st.markdown(report)