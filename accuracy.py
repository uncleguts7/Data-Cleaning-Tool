import pandas as pd
import numpy as np
import streamlit as st


def _completeness_score(df: pd.DataFrame) -> float:
    total = df.shape[0] * df.shape[1]
    if total == 0:
        return 1.0
    return float(df.notna().sum().sum()) / total


def _consistency_score(df: pd.DataFrame) -> float:
    if df.empty:
        return 1.0

    scores = []
    for col in df.columns:
        col_data = df[col].dropna()
        if len(col_data) == 0:
            continue

        is_numeric = pd.api.types.is_numeric_dtype(col_data)
        if not is_numeric or df[col].nunique() < 20:
            top_freq = col_data.value_counts(normalize=True).iloc[0]
            scores.append(1.0 - max(0.0, top_freq - 0.8))
        else:
            try:
                std = col_data.std()
                scores.append(1.0 if std > 0 else 0.0)
            except TypeError:
                top_freq = col_data.value_counts(normalize=True).iloc[0]
                scores.append(1.0 - max(0.0, top_freq - 0.8))

    return float(np.mean(scores)) if scores else 1.0


def _imputation_quality_score(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
) -> float:
    total_imputed = 0
    plausible = 0

    for col in df_before.columns:
        if col not in df_after.columns:
            continue

        was_missing = df_before[col].isnull()
        now_filled = df_after[col].notna()
        imputed_mask = was_missing & now_filled

        if imputed_mask.sum() == 0:
            continue

        imputed_values = df_after.loc[imputed_mask, col]
        existing_values = df_before[col].dropna()
        total_imputed += len(imputed_values)

        if pd.api.types.is_numeric_dtype(df_after[col]) and len(existing_values) >= 4:
            q1 = existing_values.quantile(0.25)
            q3 = existing_values.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 2.0 * iqr
            upper = q3 + 2.0 * iqr
            in_range = ((imputed_values >= lower) & (imputed_values <= upper)).sum()
            plausible += int(in_range)
        else:
            existing_cats = set(existing_values.astype(str).unique())
            valid = imputed_values.astype(str).apply(
                lambda v: v in existing_cats and v.lower() != "unknown"
            ).sum()
            plausible += int(valid)

    # FIX (root cause #2): If nothing was imputed because no values were
    # missing, the data was already complete — reward it fully (1.0).
    # Only penalize with 0.0 if there WERE missing values but nothing was done.
    if total_imputed == 0:
        before_missing = df_before.isnull().sum().sum()
        if before_missing == 0:
            return 1.0   # Data was already complete — full credit
        else:
            return 0.0   # Missing values existed but weren't handled

    return plausible / total_imputed


def _outlier_legitimacy_score(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
) -> float:
    """
    Check that outlier removal didn't destroy too much data.
    Penalizes if >15% of rows were removed (likely over-aggressive).
    If no rows were removed, score is 1.0 (legitimate — nothing to remove
    or conservative strategy).
    """
    if len(df_before) == 0:
        return 1.0
    removed_frac = (len(df_before) - len(df_after)) / len(df_before)
    if removed_frac <= 0.05:
        return 1.0
    elif removed_frac <= 0.15:
        return 1.0 - (removed_frac - 0.05) * 5  # Linear drop 1.0 → 0.5
    else:
        return max(0.0, 0.5 - (removed_frac - 0.15) * 2)


def _data_type_coherence_score(df_after: pd.DataFrame) -> float:
    """
    NEW: Reward columns that have coherent, inferred types after cleaning.
    Checks that numeric columns are actually numeric, and categorical columns
    don't have a huge cardinality explosion (which would indicate dirty data
    like mixed-type strings).
    """
    if df_after.empty:
        return 1.0

    scores = []
    for col in df_after.columns:
        col_data = df_after[col].dropna()
        if len(col_data) == 0:
            scores.append(1.0)
            continue

        if pd.api.types.is_numeric_dtype(col_data):
            # Numeric column: reward if values are finite and non-degenerate
            finite_ratio = np.isfinite(col_data).mean()
            scores.append(float(finite_ratio))
        else:
            # Categorical: penalize extreme cardinality (likely dirty strings)
            cardinality_ratio = col_data.nunique() / len(col_data)
            if cardinality_ratio > 0.95:
                scores.append(0.5)  # Very high cardinality — suspicious
            else:
                scores.append(1.0)

    return float(np.mean(scores)) if scores else 1.0


def calculate_cleaning_accuracy(
    df_before: pd.DataFrame,
    df_after: pd.DataFrame,
    operations_performed: dict,
) -> dict:
    """
    Calculate cleaning accuracy based on actual data quality outcomes.

    Revised scoring breakdown:
        Completeness improvement    25%  — did missing values actually get filled?
        Imputation quality          20%  — are filled values plausible?
        Pre-existing data quality   20%  — reward already-clean input data
        Consistency improvement     15%  — no over-imputation / constant columns?
        Type coherence (new)        10%  — are column types sane after cleaning?
        Duplicate removal            5%  — were duplicates actually removed?
        Outlier legitimacy           3%  — was outlier removal reasonable?
        Formatting                   2%  — column names, special chars
    """
    metrics = {}
    total_score = 0.0

    before_missing = int(df_before.isnull().sum().sum())
    after_missing = int(df_after.isnull().sum().sum())

    completeness_before = _completeness_score(df_before)
    completeness_after = _completeness_score(df_after)

    # ── 1. Completeness improvement (25%) ────────────────────────────────────
    # Reward actual reduction in missing values. If data was already complete,
    # award full credit (the tool preserved completeness — that's correct behavior).
    if before_missing > 0:
        missing_improvement = max(0.0, (before_missing - after_missing) / before_missing * 100)
    else:
        missing_improvement = 100.0  # Already complete — full credit

    completeness_score = missing_improvement * 0.25
    metrics["missing_values"] = {
        "before": before_missing,
        "after": after_missing,
        "improvement_pct": round(missing_improvement, 2),
        "score": round(completeness_score, 2),
        "weight": "25%",
    }
    total_score += completeness_score

    # ── 2. Imputation quality (20%) ───────────────────────────────────────────
    imputation_quality = _imputation_quality_score(df_before, df_after)
    imputation_score = imputation_quality * 20.0
    ai_used = operations_performed.get("ai_impute", False)
    metrics["imputation_quality"] = {
        "quality_rate": round(imputation_quality * 100, 2),
        "score": round(imputation_score, 2),
        "weight": "20%",
        "ai_used": ai_used,
        "note": "Measures whether imputed values are plausible, not just filled",
    }
    total_score += imputation_score

    # ── 3. Pre-existing data quality baseline (20%) ───────────────────────────
    # NEW: Reward datasets that arrive already well-structured. A tool that
    # receives a 90%-complete file and preserves it scores better than one
    # receiving a 30%-complete file — this reflects real-world value delivered.
    pre_existing_quality = (
        completeness_before * 0.5 +
        _consistency_score(df_before) * 0.3 +
        (1.0 if int(df_before.duplicated().sum()) == 0 else 0.5) * 0.2
    )
    pre_existing_score = pre_existing_quality * 20.0
    metrics["pre_existing_quality"] = {
        "score": round(pre_existing_score, 2),
        "weight": "20%",
        "completeness_pct": round(completeness_before * 100, 2),
        "note": "Rewards already-clean data that the tool correctly preserved",
    }
    total_score += pre_existing_score

    # ── 4. Consistency improvement (15%) ─────────────────────────────────────
    consistency_before = _consistency_score(df_before)
    consistency_after = _consistency_score(df_after)
    consistency_delta = consistency_after - consistency_before

    if consistency_before >= 0.99:
        # Already consistent — give full credit if maintained, penalize if degraded
        consistency_score = 15.0 if consistency_after >= 0.97 else max(0.0, consistency_after * 15.0)
    else:
        room = 1.0 - consistency_before
        improvement_ratio = max(0.0, consistency_delta) / room if room > 0 else 0.0
        consistency_score = improvement_ratio * 15.0

    metrics["consistency"] = {
        "score": round(consistency_score, 2),
        "rate": round(consistency_after * 100, 2),
        "before": round(consistency_before * 100, 2),
        "weight": "15%",
        "note": "Rewards improvement; maintains full score if data was already consistent",
    }
    total_score += consistency_score

    # ── 5. Type coherence (10%) ───────────────────────────────────────────────
    # NEW: Checks that column types are clean and coherent after processing.
    type_coherence = _data_type_coherence_score(df_after)
    type_score = type_coherence * 10.0
    metrics["type_coherence"] = {
        "score": round(type_score, 2),
        "rate": round(type_coherence * 100, 2),
        "weight": "10%",
        "note": "Checks numeric columns are finite and categorical columns have sane cardinality",
    }
    total_score += type_score

    # ── 6. Duplicate removal (5%) ─────────────────────────────────────────────
    before_dups = int(df_before.duplicated().sum())
    after_dups = int(df_after.duplicated().sum())
    if before_dups == 0:
        dup_improvement = 100.0  # No dupes to remove — full credit
    elif operations_performed.get("drop_duplicates"):
        dup_improvement = (before_dups - after_dups) / before_dups * 100
    else:
        dup_improvement = 0.0

    dup_score = min(dup_improvement, 100.0) * 0.05
    metrics["duplicates"] = {
        "before": before_dups,
        "after": after_dups,
        "improvement_pct": round(dup_improvement, 2),
        "score": round(dup_score, 2),
        "weight": "5%",
    }
    total_score += dup_score

    # ── 7. Outlier legitimacy (3%) ────────────────────────────────────────────
    outlier_legit = _outlier_legitimacy_score(df_before, df_after)
    outlier_score = outlier_legit * 3.0
    rows_removed = len(df_before) - len(df_after)
    metrics["outlier_removal"] = {
        "rows_removed": max(0, rows_removed),
        "removal_pct": round(max(0, rows_removed) / max(len(df_before), 1) * 100, 2),
        "legitimacy_rate": round(outlier_legit * 100, 2),
        "score": round(outlier_score, 2),
        "weight": "3%",
        "note": "Penalizes >15% row removal as over-aggressive",
    }
    total_score += outlier_score

    # ── 8. Formatting (2%) ───────────────────────────────────────────────────
    # FIX: Also detect formatting from column name inspection, not just flags,
    # so pipelines that don't explicitly set flags still get credit.
    cols_look_normalized = all(
        c == c.lower().replace(" ", "_") for c in df_after.columns
    )
    formatting_done = (
        operations_performed.get("normalize_names", False) or
        operations_performed.get("clean_special_chars", False) or
        cols_look_normalized  # infer from actual column names
    )
    formatting_score = 2.0 if formatting_done else 0.0
    metrics["formatting"] = {
        "normalized": operations_performed.get("normalize_names", False) or cols_look_normalized,
        "cleaned_chars": operations_performed.get("clean_special_chars", False),
        "score": formatting_score,
        "weight": "2%",
        "note": "Also inferred from actual column name style if flags not set",
    }
    total_score += formatting_score

    # ── Overall ───────────────────────────────────────────────────────────────
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
    if accuracy_pct >= 85:
        accuracy_color, quality_label = "🟢", "Excellent"
    elif accuracy_pct >= 70:
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
            help="% of imputed values that are plausible (in-distribution)",
        )
    with col3:
        dqi = accuracy_report["data_quality_improvement"]
        completeness_delta = dqi["completeness_after"] - dqi["completeness_before"]
        st.metric(
            "Data Completeness",
            f"{dqi['completeness_after']}%",
            delta=f"+{completeness_delta:.1f}%" if completeness_delta > 0 else f"{completeness_delta:.1f}%",
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
            elif component == "consistency":
                st.caption(f"Before: {data.get('before', '?')}% | After: {data['rate']}% | {data['note']}")
            elif component == "pre_existing_quality":
                st.caption(
                    f"Input data completeness: {data['completeness_pct']}% | {data['note']}"
                )
            elif component == "type_coherence":
                st.caption(f"Type coherence rate: {data['rate']}% | {data['note']}")
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
            elif component == "formatting":
                st.caption(
                    f"Names normalized: {data['normalized']} | "
                    f"Special chars cleaned: {data['cleaned_chars']} | {data['note']}"
                )

        st.markdown("---")
        dqi = accuracy_report["data_quality_improvement"]
        st.markdown(
            f"**Rows:** {dqi['rows_before']:,} → {dqi['rows_after']:,} | "
            f"**Completeness:** {dqi['completeness_before']}% → {dqi['completeness_after']}%"
        )