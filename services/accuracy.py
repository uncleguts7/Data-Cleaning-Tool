"""
Cleaning accuracy calculation — outcome-based scoring.

Scoring breakdown (v3 — fixed consistency deadlock):
    Completeness improvement    25%  — did missing values get filled?
    Imputation quality          25%  — are filled values plausible?
    Format & type quality       20%  — did cleaning improve value quality?
    Duplicate removal           15%  — were duplicates actually removed?
    Outlier legitimacy          10%  — was outlier removal reasonable?
    Operations breadth           5%  — did the pipeline address detected issues?

Why v3 vs v2:
    v2 had a permanent bug: the "consistency" component always scored 0/20
    because consistency_before was always ~1.0 in normal datasets (room ≈ 0).
    This made the maximum achievable score ~75, regardless of cleaning quality.

    v3 replaces that dead component with "Format & Type Quality" — a composite
    that measures real, observable improvements from the cleaning pipeline:
    column name standardization, placeholder removal, type homogeneity,
    and value distribution changes. These all change measurably during cleaning.
"""

import pandas as pd
import numpy as np
import streamlit as st


# ─────────────────────────────────────────────────────────────────────────────
# Internal metric functions
# ─────────────────────────────────────────────────────────────────────────────

def _completeness_score(df: pd.DataFrame) -> float:
    """Fraction of non-null cells [0.0, 1.0]."""
    total = df.shape[0] * df.shape[1]
    if total == 0:
        return 1.0
    return float(df.notna().sum().sum()) / total


def _imputation_quality_score(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
) -> float:
    """
    Measure how well missing values were filled — not just that they were filled.

    Works correctly even when df_after has fewer rows than df_before
    (e.g. after drop_duplicates + reset_index). Uses column-level null count
    comparison rather than row-level index alignment, which breaks after reindex.

    For numeric columns: sampled filled values must fall within 2× IQR fence.
    For categorical columns: filled values must be existing categories
    (not invented placeholders like Unknown).

    Returns fraction of imputed values that are plausible [0.0, 1.0].
    Returns 0.0 if nothing was imputed (no contribution, no free points).
    """
    total_imputed = 0
    plausible = 0

    # Build a case-insensitive column mapping from before → after
    after_cols_lower = {c.lower(): c for c in df_after.columns}

    for col in df_before.columns:
        # Match columns even if names were normalized (e.g. Age → age)
        after_col = col if col in df_after.columns else after_cols_lower.get(col.lower())
        if after_col is None:
            continue

        before_null_count = int(df_before[col].isnull().sum())
        after_null_count  = int(df_after[after_col].isnull().sum())
        newly_filled = before_null_count - after_null_count

        if newly_filled <= 0:
            continue

        existing_values = df_before[col].dropna()
        after_nonnull   = df_after[after_col].dropna()
        total_imputed  += newly_filled

        if pd.api.types.is_numeric_dtype(df_after[after_col]) and len(existing_values) >= 4:
            q1 = existing_values.quantile(0.25)
            q3 = existing_values.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 2.0 * iqr
            upper = q3 + 2.0 * iqr
            sample = after_nonnull.sample(min(newly_filled, len(after_nonnull)), random_state=42)
            in_range = int(((sample >= lower) & (sample <= upper)).sum())
            plausible += in_range
        else:
            existing_cats = set(existing_values.astype(str).unique())
            sample = after_nonnull.sample(min(newly_filled, len(after_nonnull)), random_state=42)
            valid = int(sample.astype(str).apply(
                lambda v: v in existing_cats and v.lower() not in ("unknown", "nan", "none", "")
            ).sum())
            plausible += valid

    if total_imputed == 0:
        return 0.0

    return plausible / total_imputed


def _format_and_type_quality(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
    operations_performed: dict,
) -> float:
    """
    Measure actual data quality improvements from the cleaning pipeline.

    This replaces the broken "consistency delta" component (which always
    scored 0 because normal datasets are already internally consistent).

    Measures four real, observable improvements:
    1. Column name standardization (snake_case, no spaces/caps)
    2. Placeholder removal (were 'UNKNOWN'/'N/A' values cleaned out?)
    3. Special character removal from text columns
    4. Type homogeneity (categorical columns with fewer mixed-type values)

    Returns a composite score [0.0, 1.0].
    """
    sub_scores = []

    # ── Sub-score 1: Column name quality ─────────────────────────────────────
    if operations_performed.get("normalize_names"):
        after_cols = df_after.columns.tolist()
        # Count columns that are now clean (lowercase, no spaces, no special chars)
        clean_count = sum(
            1 for c in after_cols
            if c == c.lower() and " " not in c and c.replace("_", "").isalnum()
        )
        col_score = clean_count / max(len(after_cols), 1)
        sub_scores.append(col_score)
    else:
        # Check how clean names already are
        before_cols = df_before.columns.tolist()
        clean_count = sum(1 for c in before_cols if " " not in str(c))
        sub_scores.append(clean_count / max(len(before_cols), 1) * 0.5)  # Half credit

    # ── Sub-score 2: Placeholder elimination ──────────────────────────────────
    PLACEHOLDERS = {"unknown", "n/a", "na", "null", "none", "nan", "missing",
                    "error", "undefined", "invalid", "-", "--", "---", ""}
    before_placeholder_count = 0
    after_placeholder_count = 0
    for col in df_before.select_dtypes(include=["object","string"]).columns:
        before_placeholder_count += df_before[col].astype(str).str.strip().str.lower().isin(PLACEHOLDERS).sum()
    for col in df_after.select_dtypes(include=["object","string"]).columns:
        if col in df_after.columns:
            after_placeholder_count += df_after[col].astype(str).str.strip().str.lower().isin(PLACEHOLDERS).sum()

    if before_placeholder_count > 0:
        placeholder_reduction = (before_placeholder_count - after_placeholder_count) / before_placeholder_count
        sub_scores.append(max(0.0, placeholder_reduction))
    else:
        # No placeholders to remove — partial credit for clean state
        sub_scores.append(0.6)

    # ── Sub-score 3: Special character cleanliness ────────────────────────────
    if operations_performed.get("clean_special_chars"):
        import re
        def special_char_ratio(df):
            ratios = []
            for col in df.select_dtypes(include=["object","string"]).columns:
                vals = df[col].dropna().astype(str)
                if len(vals) == 0:
                    continue
                dirty = vals.apply(lambda v: bool(re.search(r'[^\w\s\u0600-\u06FF@./:-]', v))).sum()
                ratios.append(dirty / len(vals))
            return float(np.mean(ratios)) if ratios else 0.0

        before_ratio = special_char_ratio(df_before)
        after_ratio = special_char_ratio(df_after)
        if before_ratio > 0:
            reduction = (before_ratio - after_ratio) / before_ratio
            sub_scores.append(max(0.0, reduction))
        else:
            sub_scores.append(0.7)  # Already clean
    else:
        sub_scores.append(0.5)  # Not attempted

    # ── Sub-score 4: Categorical value homogeneity ────────────────────────────
    # Measures whether categorical columns have fewer unique values after cleaning
    # (consolidation of variants like 'eng' / 'Eng' / 'Engineering')
    cat_cols_before = df_before.select_dtypes(include=["object","string"]).columns
    homogeneity_scores = []
    for col in cat_cols_before:
        if col not in df_after.columns:
            continue
        before_unique = df_before[col].dropna().nunique()
        after_unique = df_after[col].dropna().nunique()
        if before_unique == 0:
            continue
        if after_unique <= before_unique:
            # Improvement or same — score based on how much consolidation happened
            ratio = after_unique / before_unique
            homogeneity_scores.append(1.0 - (ratio - 0.5) if ratio < 1.0 else 0.7)
        else:
            # More unique values after cleaning — slight penalty (unlikely but possible)
            homogeneity_scores.append(0.4)

    if homogeneity_scores:
        sub_scores.append(float(np.mean(homogeneity_scores)))
    else:
        sub_scores.append(0.65)

    return float(np.mean(sub_scores)) if sub_scores else 0.5


def _outlier_legitimacy_score(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
) -> float:
    """
    Check that outlier removal didn't destroy too much data.
    Full score if ≤5% of rows removed. Penalty above that.
    """
    if len(df_before) == 0:
        return 1.0
    removed_frac = (len(df_before) - len(df_after)) / len(df_before)
    if removed_frac <= 0.0:
        return 1.0  # Nothing removed — no penalty, no bonus
    elif removed_frac <= 0.05:
        return 1.0  # Reasonable removal
    elif removed_frac <= 0.15:
        return 1.0 - (removed_frac - 0.05) * 5  # Linear drop: 1.0 → 0.5
    else:
        return max(0.0, 0.5 - (removed_frac - 0.15) * 2)


def _operations_breadth_score(
    df_before: pd.DataFrame,
    operations_performed: dict,
) -> float:
    """
    Reward pipelines that address the issues actually present in the data.

    If the data had missing values → imputation should have been run.
    If the data had duplicates → drop_duplicates should have been run.
    Penalizes doing nothing when issues exist.
    """
    expected = 0
    done = 0

    # Was imputation needed?
    has_missing = df_before.isnull().any().any()
    if has_missing:
        expected += 1
        if operations_performed.get("impute_numeric") or operations_performed.get("impute_categorical") or operations_performed.get("ai_impute"):
            done += 1

    # Were duplicates present?
    has_dupes = df_before.duplicated().any()
    if has_dupes:
        expected += 1
        if operations_performed.get("drop_duplicates"):
            done += 1

    # Was formatting needed? (always expected for basic hygiene)
    expected += 1
    if operations_performed.get("normalize_names") or operations_performed.get("clean_special_chars"):
        done += 1

    # Was placeholder cleaning done if placeholders exist?
    PLACEHOLDERS = {"unknown", "n/a", "null", "none", "-", "error"}
    has_placeholders = False
    for col in df_before.select_dtypes(include=["object","string"]).columns:
        if df_before[col].astype(str).str.strip().str.lower().isin(PLACEHOLDERS).any():
            has_placeholders = True
            break
    if has_placeholders:
        expected += 1
        if operations_performed.get("convert_placeholders"):
            done += 1

    return done / max(expected, 1)


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def calculate_cleaning_accuracy(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
    operations_performed: dict,
) -> dict:
    """
    Calculate cleaning accuracy based on actual data quality outcomes.

    Weights (v3):
        Completeness improvement    25%
        Imputation quality          25%
        Format & type quality       20%
        Duplicate removal           15%
        Outlier legitimacy          10%
        Operations breadth           5%
    """
    metrics = {}
    total_score = 0.0

    before_missing = int(df_before.isnull().sum().sum())
    after_missing = int(df_after.isnull().sum().sum())
    completeness_before = _completeness_score(df_before)
    completeness_after = _completeness_score(df_after)

    # ── 1. Completeness improvement (25%) ────────────────────────────────────
    if before_missing > 0:
        missing_improvement = (before_missing - after_missing) / before_missing * 100
        missing_improvement = max(0.0, missing_improvement)
    else:
        missing_improvement = 0.0

    completeness_score = missing_improvement * 0.25
    metrics["missing_values"] = {
        "before": before_missing,
        "after": after_missing,
        "improvement_pct": round(missing_improvement, 2),
        "score": round(completeness_score, 2),
        "weight": "25%",
    }
    total_score += completeness_score

    # ── 2. Imputation quality (25%) ───────────────────────────────────────────
    imputation_quality = _imputation_quality_score(df_before, df_after)
    imputation_score = imputation_quality * 25.0
    ai_used = operations_performed.get("ai_impute", False)
    metrics["imputation_quality"] = {
        "quality_rate": round(imputation_quality * 100, 2),
        "score": round(imputation_score, 2),
        "weight": "25%",
        "ai_used": ai_used,
        "note": "% of imputed values that are plausible and in-distribution",
    }
    total_score += imputation_score

    # ── 3. Format & type quality (20%) ───────────────────────────────────────
    fmt_quality = _format_and_type_quality(df_before, df_after, operations_performed)
    fmt_score = fmt_quality * 20.0
    metrics["format_quality"] = {
        "score": round(fmt_score, 2),
        "rate": round(fmt_quality * 100, 2),
        "weight": "20%",
        "note": "Column names, placeholder removal, special chars, value homogeneity",
    }
    total_score += fmt_score

    # ── 4. Duplicate removal (15%) ────────────────────────────────────────────
    before_dups = int(df_before.duplicated().sum())
    after_dups = int(df_after.duplicated().sum())
    if before_dups > 0 and operations_performed.get("drop_duplicates"):
        dup_improvement = (before_dups - after_dups) / before_dups * 100
    elif before_dups == 0:
        dup_improvement = 100.0  # No dupes to remove — full credit
    else:
        dup_improvement = 0.0

    dup_score = min(dup_improvement, 100.0) * 0.15
    metrics["duplicates"] = {
        "before": before_dups,
        "after": after_dups,
        "improvement_pct": round(dup_improvement, 2),
        "score": round(dup_score, 2),
        "weight": "15%",
    }
    total_score += dup_score

    # ── 5. Outlier legitimacy (10%) ───────────────────────────────────────────
    outlier_legit = _outlier_legitimacy_score(df_before, df_after)
    outlier_score = outlier_legit * 10.0
    rows_removed = len(df_before) - len(df_after)
    metrics["outlier_removal"] = {
        "rows_removed": max(0, rows_removed),
        "removal_pct": round(max(0, rows_removed) / max(len(df_before), 1) * 100, 2),
        "legitimacy_rate": round(outlier_legit * 100, 2),
        "score": round(outlier_score, 2),
        "weight": "10%",
        "note": "Penalizes >15% row removal as over-aggressive",
    }
    total_score += outlier_score

    # ── 6. Operations breadth (5%) ────────────────────────────────────────────
    ops_score_raw = _operations_breadth_score(df_before, operations_performed)
    ops_score = ops_score_raw * 5.0
    metrics["operations_breadth"] = {
        "score": round(ops_score, 2),
        "rate": round(ops_score_raw * 100, 2),
        "weight": "5%",
        "note": "Did the pipeline address all detected issues in the data?",
    }
    total_score += ops_score

    overall_accuracy = min(total_score, 100.0)

    return {
        "overall_accuracy": round(overall_accuracy, 2),
        "total_score": round(total_score, 2),
        "max_score": 100,
        "metrics": metrics,
        "data_quality_improvement": {
            "rows_before": len(df_before),
            "rows_after": len(df_after),
            "columns": df_after.shape[1],
            "completeness_before": round(completeness_before * 100, 2),
            "completeness_after": round(completeness_after * 100, 2),
        },
    }


def display_accuracy_report(accuracy_report: dict, title: str = "🎯 Cleaning Accuracy Report"):
    """Display a formatted accuracy report in Streamlit."""
    st.markdown(f"### {title}")

    accuracy_pct = accuracy_report["overall_accuracy"]
    if accuracy_pct >= 88:
        accuracy_color, quality_label = "🟢", "Excellent"
    elif accuracy_pct >= 72:
        accuracy_color, quality_label = "🟡", "Good"
    elif accuracy_pct >= 50:
        accuracy_color, quality_label = "🟠", "Fair"
    else:
        accuracy_color, quality_label = "🔴", "Needs Improvement"

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(f"{accuracy_color} Overall Accuracy", f"{accuracy_pct}%", delta=quality_label)
    with col2:
        qi = accuracy_report["metrics"].get("imputation_quality", {})
        st.metric(
            "Imputation Quality",
            f"{qi.get('quality_rate', 0)}%",
            help="% of imputed values that are plausible and in-distribution",
        )
    with col3:
        dqi = accuracy_report["data_quality_improvement"]
        completeness_delta = dqi["completeness_after"] - dqi["completeness_before"]
        st.metric(
            "Data Completeness",
            f"{dqi['completeness_after']}%",
            delta=f"+{completeness_delta:.1f}%" if completeness_delta > 0 else (
                "No change" if completeness_delta == 0 else f"{completeness_delta:.1f}%"
            ),
        )
    with col4:
        rows_before = accuracy_report["data_quality_improvement"]["rows_before"]
        rows_after = accuracy_report["data_quality_improvement"]["rows_after"]
        rows_change = rows_after - rows_before
        st.metric(
            "Rows",
            f"{rows_after:,}",
            delta=f"{rows_change:,}" if rows_change != 0 else "No change",
        )

    with st.expander("📊 Detailed Accuracy Breakdown"):
        for component, data in accuracy_report["metrics"].items():
            name = component.replace("_", " ").title()
            score = data.get("score", 0)
            weight = data.get("weight", "")
            st.markdown(f"**{name}** ({weight}) → `{score:.1f}` pts")

            if component == "missing_values":
                st.caption(
                    f"Before: {data['before']:,} missing | After: {data['after']:,} missing | "
                    f"Improvement: {data['improvement_pct']}%"
                )
            elif component == "imputation_quality":
                st.caption(
                    f"Plausible imputed values: {data['quality_rate']}% | "
                    f"AI used: {data['ai_used']} | {data['note']}"
                )
            elif component == "format_quality":
                st.caption(f"Quality rate: {data['rate']}% | {data['note']}")
            elif component == "duplicates":
                st.caption(
                    f"Before: {data['before']:,} | After: {data['after']:,} | "
                    f"Improvement: {data['improvement_pct']}%"
                )
            elif component == "outlier_removal":
                st.caption(
                    f"Rows removed: {data['rows_removed']:,} ({data['removal_pct']}%) | "
                    f"Legitimacy: {data['legitimacy_rate']}% | {data['note']}"
                )
            elif component == "operations_breadth":
                st.caption(f"Pipeline coverage: {data['rate']}% | {data['note']}")

        st.markdown("---")
        dqi = accuracy_report["data_quality_improvement"]
        st.markdown(
            f"**Rows:** {dqi['rows_before']:,} → {dqi['rows_after']:,} | "
            f"**Completeness:** {dqi['completeness_before']}% → {dqi['completeness_after']}%"
        )