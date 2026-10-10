import pandas as pd
import numpy as np
import streamlit as st
import logging
from sklearn.impute import KNNImputer, SimpleImputer

from utils.data_utils import should_be_integer
from utils.validation import validate_city_country, get_valid_cities_for_country
from config.settings import CONTEXT_PRIORITY_KEYWORDS, MONETARY_KEYWORDS

logger = logging.getLogger(__name__)


def should_be_monetary(col_name: str, data_sample: pd.Series) -> bool:

    col_lower = col_name.lower().replace("_", " ").replace("-", " ")

    # Explicit exclusions — these are NOT monetary despite decimal patterns
    exclude_keywords = [
        "lat", "lon", "lng", "latitude", "longitude",
        "rating", "score", "rate", "pct", "percent",
        "ratio", "fraction", "probability", "weight",
    ]
    if any(kw in col_lower for kw in exclude_keywords):
        return False

    for keyword in MONETARY_KEYWORDS:
        if keyword in col_lower:
            return True

    non_null = data_sample.dropna()
    if len(non_null) >= 10:
        try:
            decimal_places = non_null.apply(
                lambda x: len(str(float(x)).split(".")[-1]) if "." in str(float(x)) else 0
            )
            avg_decimals = decimal_places.mean()
            max_val = non_null.max()
            
            if 0 < avg_decimals <= 2 and max_val > 10:
                return True
        except (ValueError, TypeError):
            pass

    return False


def impute_numeric_knn(
    df: pd.DataFrame,
    numeric_cols: list,
    n_neighbors: int = 3,
    manual_integer_cols: str = None,
) -> pd.DataFrame:
    """Impute numeric columns with KNN, respecting integer and monetary constraints."""
    if not numeric_cols:
        return df

    imputer = KNNImputer(n_neighbors=n_neighbors)

    df[numeric_cols] = df[numeric_cols].apply(
        lambda col: col.astype(int) if col.dtype == bool else col
    )

    arr = imputer.fit_transform(df[numeric_cols])

    manual_int_set = set()
    if manual_integer_cols:
        manual_int_set = {col.strip() for col in manual_integer_cols.split(",") if col.strip()}

    integer_cols_found = []
    monetary_cols_found = []

    for idx, col in enumerate(numeric_cols):
        df[col] = arr[:, idx]

        is_manual_int = col in manual_int_set or any(m in col.lower() for m in manual_int_set)
        is_auto_int = should_be_integer(col, df[col])

        if is_manual_int or is_auto_int:
            df[col] = np.round(df[col]).astype(int)
            integer_cols_found.append(col)
        elif should_be_monetary(col, df[col]):
            df[col] = np.round(df[col], 2)
            monetary_cols_found.append(col)

    if integer_cols_found:
        st.info(f"✓ Rounded to integers: {', '.join(integer_cols_found)}")
    if monetary_cols_found:
        st.info(f"✓ Rounded to 2 decimal places (monetary): {', '.join(monetary_cols_found)}")

    return df


def impute_categorical_mode(df: pd.DataFrame, cat_cols: list) -> pd.DataFrame:
    """Impute categorical columns using mode (most frequent value)."""
    imp = SimpleImputer(strategy="most_frequent")
    df[cat_cols] = imp.fit_transform(df[cat_cols])
    return df


def _llm_impute_value(
    column: str,
    context: dict,
    existing_values: list,
    sample_size: int = 10,
) -> str | None:
    """
    Ask the LLM to pick the most likely value for a missing cell.

    Args:
        column: Column name being imputed
        context: Other column values for this row {col: val}
        existing_values: Sample of existing non-null values in the column
        sample_size: How many existing values to show the LLM

    Returns:
        Imputed value string, or None if LLM unavailable
    """
    try:
        from ai.llm_advisor import _call_llm
        import json

        sample = existing_values[:sample_size]
        prompt = f"""You are a data imputation expert. A value is missing in a dataset.

Column being imputed: "{column}"
Existing values in this column (sample): {sample}
Other values in this row (context): {json.dumps(context, default=str)}

Task: Choose the single most likely value for the missing cell.
- Pick from the existing values if one fits the context
- If none fit, you may suggest a new but plausible value
- Return ONLY the value itself — no explanation, no quotes, no JSON

Value:"""

        result = _call_llm(prompt, max_tokens=32).strip().strip('"').strip("'")
        return result if result else None

    except Exception as e:
        logger.warning(f"LLM imputation unavailable: {e}")
        return None


def ai_impute_categorical(
    df: pd.DataFrame,
    column: str,
    context_columns: list = None,
) -> pd.DataFrame:
    """
    Impute categorical values using LLM with context awareness.

    Upgrade over original:
    - Actually calls the LLM for each missing value decision
    - LLM sees the row context + existing values → picks the most plausible value
    - Falls back to context-match → mode → "Unknown" if LLM unavailable
    - Geo validation still applied on top of LLM suggestions
    """
    try:
        if column not in df.columns:
            st.error(f"Column '{column}' not found in dataframe")
            return df

        missing_indices = df[df[column].isnull()].index

        if len(missing_indices) == 0:
            st.info(f"No missing values in column '{column}'")
            return df

        # ── Detect geographical imputation ────────────────────────────────────
        is_city_imputation = False
        country_column = None
        col_lower = column.lower()

        if "city" in col_lower or "مدينة" in col_lower:
            for col in df.columns:
                if any(k in col.lower() for k in ["country", "دولة", "بلد"]):
                    is_city_imputation = True
                    country_column = col
                    break

        # ── Auto-detect context columns ───────────────────────────────────────
        if context_columns is None:
            context_cols = [
                col for col in df.columns
                if col != column and
                any(kw in col.lower() for kw in CONTEXT_PRIORITY_KEYWORDS)
            ]
            for col in df.columns:
                if col != column and col not in context_cols and len(context_cols) < 3:
                    context_cols.append(col)
        else:
            context_cols = context_columns

        if is_city_imputation and country_column:
            st.info("🌍 Geographical imputation detected — using LLM + geo validation")
            context_cols = [country_column] + [c for c in context_cols if c != country_column]
        else:
            st.info(f"🤖 LLM-powered imputation for '{column}' using context: {', '.join(context_cols)}")

        # Existing values for LLM context
        existing_values = df[column].dropna().tolist()

        imputed_values = []
        imputation_details = []
        methods_used = {"llm": 0, "geo_validated": 0, "context_match": 0, "mode": 0, "fallback": 0}

        # Cap at 100 rows to avoid excessive LLM calls
        indices_to_process = missing_indices[:100]
        progress = st.progress(0, text="Imputing missing values...")

        for i, idx in enumerate(indices_to_process):
            progress.progress((i + 1) / len(indices_to_process), text=f"Imputing row {i+1}/{len(indices_to_process)}...")

            # Build context for this row
            context = {
                ctx_col: df.loc[idx, ctx_col]
                for ctx_col in context_cols
                if ctx_col in df.columns and pd.notna(df.loc[idx, ctx_col])
            }

            imputed_value = None
            method = "fallback"

            # ── Geo path ──────────────────────────────────────────────────────
            if is_city_imputation and country_column and country_column in context:
                country = context[country_column]
                valid_cities = get_valid_cities_for_country(df, column, country, country_column)

                if valid_cities and valid_cities[0] != "Unknown":
                    if len(valid_cities) == 1:
                        imputed_value = valid_cities[0]
                        method = "geo_validated"
                    else:
                        # Multiple valid cities — ask LLM to pick
                        llm_pick = _llm_impute_value(column, context, valid_cities)
                        imputed_value = llm_pick if llm_pick in valid_cities else valid_cities[0]
                        method = "llm" if llm_pick else "geo_validated"

            # ── LLM path (general) ────────────────────────────────────────────
            if imputed_value is None and context:
                llm_pick = _llm_impute_value(column, context, existing_values)
                if llm_pick:
                    imputed_value = llm_pick
                    method = "llm"

            # ── Context-match fallback ────────────────────────────────────────
            if imputed_value is None and context:
                mask = pd.Series([True] * len(df), index=df.index)
                for ctx_col, ctx_val in context.items():
                    if ctx_col in df.columns:
                        mask &= (df[ctx_col] == ctx_val)

                similar_rows = df[mask & df[column].notna()]
                if len(similar_rows) > 0:
                    imputed_value = similar_rows[column].value_counts().index[0]
                    method = "context_match"

            # ── Mode fallback ─────────────────────────────────────────────────
            if imputed_value is None:
                mode_vals = df[column].mode()
                imputed_value = mode_vals[0] if len(mode_vals) > 0 else "Unknown"
                method = "mode"

            methods_used[method] = methods_used.get(method, 0) + 1
            imputed_values.append((idx, imputed_value))
            imputation_details.append({
                "index": idx,
                "context": str(context),
                "imputed": imputed_value,
                "method": method,
            })

        progress.empty()

        # Apply imputed values
        df_copy = df.copy()
        for idx, value in imputed_values:
            df_copy.loc[idx, column] = value

        # Summary
        st.success(f"✓ Imputed {len(imputed_values)} values in '{column}'")
        method_summary = " | ".join(f"{m}: {c}" for m, c in methods_used.items() if c > 0)
        st.caption(f"Methods used — {method_summary}")

        with st.expander("🔍 Imputation Details (first 15 rows)"):
            st.dataframe(pd.DataFrame(imputation_details[:15]), use_container_width=True)

        return df_copy

    except Exception as e:
        st.error(f"AI Imputation failed for column '{column}': {e}")
        logger.error(f"AI Imputation error: {e}", exc_info=True)
        return df


def heuristic_impute(column: str, context: dict, existing_values: list) -> str:
    """Heuristic fallback — returns most common existing value."""
    if existing_values:
        return existing_values[0]
    return "Unknown"