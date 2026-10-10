import streamlit as st
import pandas as pd
from utils.data_utils import infer_column_types
from utils.helpers import get_timestamp, download_link_df
from services.cleaning import (
    drop_exact_duplicates, 
    clean_special_characters, 
    remove_outliers_isolationforest,
    convert_placeholders_to_nan,
    detect_placeholder_values,
    PLACEHOLDER_VALUES
)
from services.imputation import impute_numeric_knn, impute_categorical_mode, ai_impute_categorical
from services.accuracy import calculate_cleaning_accuracy, display_accuracy_report
from ui.components import save_to_history


def render_clean_data_tab(settings:  dict):
    """Render the clean data tab content. 
    
    Args:
        settings:  Dictionary of settings from sidebar
    """
    st.subheader("🧹 Clean Data with Preview")
    
    if st.session_state["current_df"] is None: 
        st.warning("Please upload and analyze data first.")
        return
    
    df_current = st.session_state["current_df"]. copy()
    
    st.markdown("### Current State")
    st.write(f"Rows: {df_current.shape[0]} | Columns: {df_current.shape[1]}")
    
    # Detect and show placeholder values
    placeholder_detection = detect_placeholder_values(df_current)
    if placeholder_detection["total_found"] > 0:
        with st.expander(f"⚠️ Found {placeholder_detection['total_found']} placeholder values (UNKNOWN, ERROR, etc. )", expanded=True):
            st.markdown("**Placeholder values detected that should be treated as missing:**")
            
            # Show by column
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**By Column:**")
                for col, col_data in placeholder_detection["by_column"].items():
                    # Handle different data structures safely
                    if isinstance(col_data, dict):
                        if "count" in col_data:
                            total_in_col = col_data["count"]
                        else: 
                            # Sum all values if it's a dict of value -> count
                            total_in_col = sum(
                                v if isinstance(v, int) else v.get("count", 0) if isinstance(v, dict) else 0
                                for v in col_data.values()
                            )
                    elif isinstance(col_data, int):
                        total_in_col = col_data
                    else:
                        total_in_col = 0
                    st.write(f"• `{col}`: {total_in_col} values")
            
            with col2:
                st. markdown("**By Value Type:**")
                for value, count in placeholder_detection. get("by_value", {}).items():
                    if isinstance(count, int):
                        st.write(f"• `{value}`: {count} occurrences")
                    elif isinstance(count, dict):
                        st.write(f"• `{value}`: {count.get('count', 0)} occurrences")
            
            st.info("💡 Enable 'Convert placeholder values to missing' below to fix these.")
    
    preview_mode = st.checkbox("🔍 Preview Mode (don't apply changes)", value=True)
    
    st.markdown("### Select Cleaning Operations")
    
    operations = {}
    operations["normalize_names"] = st.checkbox("Normalize column names", value=True)
    
    # New placeholder handling option
    operations["convert_placeholders"] = st.checkbox(
        "🔄 Convert placeholder values to missing (UNKNOWN, ERROR, N/A, etc.)",
        value=True if placeholder_detection["total_found"] > 0 else False,
        help="Treats values like 'UNKNOWN', 'ERROR', 'N/A', 'NULL', '-' as missing values so they can be imputed"
    )
    
    # Show custom placeholder option
    if operations["convert_placeholders"]:
        with st.expander("⚙️ Customize placeholder values"):
            st.markdown("**Default placeholders detected:**")
            st.caption(", ".join([f"`{v}`" for v in PLACEHOLDER_VALUES[: 15]]) + ", ...")
            
            custom_placeholders = st.text_input(
                "Add custom placeholder values (comma-separated):",
                placeholder="e.g., BLANK, TBD, PENDING",
                help="Add your own values to treat as missing"
            )
    else:
        custom_placeholders = ""
    
    operations["clean_special_chars"] = st.checkbox(
        "🧹 Clean special characters (@#$ from names, preserve in emails)", 
        value=True
    )
    operations["drop_duplicates"] = st. checkbox("Drop exact duplicates", value=settings['drop_exact_dup'])
    operations["impute_numeric"] = st.checkbox("Impute numeric (KNN)", value=True)
    operations["impute_categorical"] = st.checkbox("Impute categorical", value=settings['do_cat_impute'])
    
    ai_impute_col = None
    ai_context_cols = None
    if settings['use_ai_imputation']:
        operations["ai_impute"] = st.checkbox("🧠 AI Categorical Imputation", value=False)
        if operations["ai_impute"]: 
            cat_cols = [c for c in df_current.columns if df_current[c]. dtype == object]
            if cat_cols: 
                st.markdown("**Configure AI Imputation:**")
                ai_impute_col = st.selectbox("Column to impute", cat_cols)
                
                other_cols = [c for c in df_current.columns if c != ai_impute_col]
                ai_context_cols = st.multiselect(
                    "Context columns (for matching logic)",
                    other_cols,
                    help="Select columns that provide context.  Leave empty for auto-detection."
                )
                
                st.info("💡 Example: If imputing 'City', select 'Country' as context")
            else:
                st.warning("No categorical columns available for AI imputation")
                operations["ai_impute"] = False
    
    operations["remove_outliers"] = st.checkbox("Remove outliers", value=True)
    
    if st.button("▶️ Run Cleaning Pipeline"):
        with st.spinner("Processing... "):
            df_before = df_current. copy()
            df_preview = df_current. copy()
            for col in df_preview.columns:
                if "date" in col.lower() or "time" in col.lower():
                    df_preview[col] = pd.to_datetime(df_preview[col], errors="coerce")
            steps = []
            operations_performed = {}
            
            original_ai_col = ai_impute_col if operations. get("ai_impute") else None
            original_context_cols = ai_context_cols if operations.get("ai_impute") and ai_context_cols else None
            
            # Normalize names
            if operations["normalize_names"]:
                old_cols = df_preview.columns.tolist()
                df_preview. columns = [str(c).strip().lower().replace(" ", "_") for c in df_preview. columns]
                new_cols = df_preview.columns. tolist()
                col_mapping = dict(zip(old_cols, new_cols))
                
                if original_ai_col and original_ai_col in old_cols:
                    ai_impute_col_normalized = col_mapping[original_ai_col]
                else:
                    ai_impute_col_normalized = None
                
                if original_context_cols: 
                    ai_context_cols_normalized = [col_mapping. get(c, c) for c in original_context_cols if c in col_mapping]
                else:
                    ai_context_cols_normalized = None
                
                steps.append("✓ Normalized column names")
                operations_performed['normalize_names'] = True
            else:
                ai_impute_col_normalized = original_ai_col
                ai_context_cols_normalized = original_context_cols
            
            # Convert placeholders to NaN
            if operations["convert_placeholders"]:
                # Add custom placeholders if provided
                all_placeholders = list(PLACEHOLDER_VALUES)
                if custom_placeholders: 
                    custom_list = [v.strip() for v in custom_placeholders.split(',') if v.strip()]
                    all_placeholders.extend(custom_list)
                
                df_preview, conversion_report = convert_placeholders_to_nan(df_preview, all_placeholders)
                
                if conversion_report["total_converted"] > 0:
                    steps. append(f"✓ Converted {conversion_report['total_converted']} placeholder values to missing")
                    operations_performed['convert_placeholders'] = True
                    
                    # Show details
                    with st.expander("📋 Placeholder Conversion Details"):
                        st.markdown("**Converted by column:**")
                        for col, count in conversion_report["by_column"].items():
                            st.write(f"• `{col}`: {count} values converted")
                        
                        st.markdown("**Converted by value type:**")
                        for value, count in conversion_report["by_value"].items():
                            st.write(f"• `{value}`: {count} occurrences → NaN")
            
            # Clean special characters
            if operations["clean_special_chars"]:
                text_cols = [
                    c for c in df_preview.columns
                    if df_preview[c].dtype == object
                    and "date" not in c.lower()
                    and "time" not in c.lower()
                ]
                cleaned_count = 0
                for col in text_cols:
                    before_clean = df_preview[col].copy()
                    df_preview = clean_special_characters(df_preview, col)
                    if not df_preview[col].equals(before_clean):
                        cleaned_count += 1
                if cleaned_count > 0:
                    steps.append(f"✓ Cleaned special characters from {cleaned_count} columns")
                operations_performed['clean_special_chars'] = True
            
            # Drop duplicates
            if operations["drop_duplicates"]:
                before = len(df_preview)
                df_preview, removed = drop_exact_duplicates(df_preview)
                steps.append(f"✓ Removed {removed} duplicate rows")
                operations_performed['drop_duplicates'] = True
            
            # Impute numeric
            if operations["impute_numeric"]: 
                col_types = infer_column_types(df_preview)
                numeric_cols = [c for c, t in col_types.items() if t == "numeric"]
                if numeric_cols: 
                    df_preview = impute_numeric_knn(
                        df_preview,
                        numeric_cols,
                        settings['knn_neighbors'],
                        settings['manual_integer_cols']
                    )
                    steps. append(f"✓ Imputed {len(numeric_cols)} numeric columns")
                    operations_performed['impute_numeric'] = True
            
            # Impute categorical
            if operations["impute_categorical"]:
                col_types = infer_column_types(df_preview)
                cat_cols = [c for c, t in col_types.items() if t == "categorical"]
                if cat_cols: 
                    df_preview = impute_categorical_mode(df_preview, cat_cols)
                    steps.append(f"✓ Imputed {len(cat_cols)} categorical columns")
                    operations_performed['impute_categorical'] = True
            
            # AI Imputation
            if operations. get("ai_impute") and settings['use_ai_imputation'] and ai_impute_col_normalized: 
                if ai_impute_col_normalized in df_preview.columns:
                    df_preview = ai_impute_categorical(
                        df_preview,
                        ai_impute_col_normalized,
                        context_columns=ai_context_cols_normalized if ai_context_cols_normalized else None
                    )
                    steps.append(f"✓ AI imputed column:  {ai_impute_col_normalized}")
                    operations_performed['ai_impute'] = True
                else:
                    st.warning(f"Column '{ai_impute_col_normalized}' not found after normalization")
            
            # Remove outliers
            outliers_removed = 0
            if operations["remove_outliers"]: 
                col_types = infer_column_types(df_preview)
                numeric_cols = [c for c, t in col_types.items() if t == "numeric"]
                df_preview, outliers_removed = remove_outliers_isolationforest(
                    df_preview, 
                    numeric_cols, 
                    settings['contamination']
                )
                steps.append(f"✓ Removed {outliers_removed} outliers")
                operations_performed['outliers_removed'] = outliers_removed
            
            # Show results
            st.markdown("### 📋 Cleaning Summary")
            for step in steps: 
                st.write(step)
            
            st.write(f"**Before:** {len(df_current)} rows | **After:** {len(df_preview)} rows")
            
            # Calculate and display accuracy
            accuracy_report = calculate_cleaning_accuracy(df_before, df_preview, operations_performed)
            display_accuracy_report(accuracy_report)
            
            # Preview
            st.markdown("### 👁️ Preview of Cleaned Data")
            st.dataframe(df_preview. head(100))
            
            # Apply or discard
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if not preview_mode:
                    if st.button("✅ Apply Changes"):
                        save_to_history(df_preview, "Full cleaning pipeline")
                        st.success("Changes applied!")
                        st.rerun()
            
            with col2:
                cleaned_bytes = download_link_df(df_preview)
                st.download_button(
                    "💾 Download Preview",
                    data=cleaned_bytes,
                    file_name=f"preview_{get_timestamp()}.csv",
                    mime="text/csv"
                )
            
            with col3:
                if st.button("❌ Discard"):
                    st. info("Changes discarded")