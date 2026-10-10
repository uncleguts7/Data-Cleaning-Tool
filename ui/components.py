"""Reusable UI components for Streamlit."""

import streamlit as st
import pandas as pd
from config.settings import APP_TITLE, AUTHOR, APP_VERSION, DEFAULT_KNN_NEIGHBORS, DEFAULT_CONTAMINATION
from config.styles import CSS_STYLES


def render_header():
    """Render the application header."""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
    
    with st.container():
        st.markdown(f"""
        <div class="header">
            <div>
                <div class="title">{APP_TITLE}</div>
                <div class="subtitle">AI-powered pipeline with advanced imputation, error detection, and smart suggestions. </div>
            </div>
            <div style="text-align:right">
                <div class="byline">{AUTHOR}</div>
                <div class="subtitle">v{APP_VERSION} – Enhanced with AI Features</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")


def init_session_state():
    """Initialize Streamlit session state variables."""
    if "df_history" not in st.session_state:
        st.session_state["df_history"] = []
    if "current_df" not in st.session_state:
        st.session_state["current_df"] = None
    if "error_report" not in st.session_state:
        st.session_state["error_report"] = {}
    if "ai_suggestions" not in st.session_state:
        st.session_state["ai_suggestions"] = {}
    if "loaded_file_name" not in st.session_state:
        st.session_state["loaded_file_name"] = None


def _load_file(uploaded_file, delimiter: str, excel_sheet: str) -> pd.DataFrame:
    """Read uploaded file into a dataframe."""
    file_name = uploaded_file.name
    file_ext = file_name.split(".")[-1].lower()

    if file_ext in ["xlsx", "xls"]:
        if excel_sheet:
            return pd.read_excel(uploaded_file, sheet_name=excel_sheet)
        else:
            return pd.read_excel(uploaded_file)
    else:
        # CSV / TSV / TXT
        sep = delimiter if delimiter else ","
        return pd.read_csv(uploaded_file, sep=sep, encoding="utf-8", on_bad_lines="skip")


def save_to_history(df, operation_name: str):
    """Save current state to history for undo functionality."""
    from utils.helpers import get_timestamp

    if st.session_state["current_df"] is not None:
        st.session_state["df_history"].append({
            "df": st.session_state["current_df"].copy(),
            "operation": operation_name,
            "timestamp": get_timestamp()
        })
    st.session_state["current_df"] = df.copy()


def undo_last_operation() -> tuple:
    """Undo the last operation."""
    if len(st.session_state["df_history"]) > 0:
        last_state = st.session_state["df_history"].pop()
        st.session_state["current_df"] = last_state["df"].copy()
        return True, last_state["operation"]
    return False, None


def render_sidebar() -> dict:
    """Render the sidebar and return settings."""
    settings = {}

    with st.sidebar:
        st.header("📤 Upload & Settings")

        settings['uploaded_file'] = st.file_uploader(
            "Upload your data file",
            type=["csv", "tsv", "txt", "xlsx", "xls"],
            help="Supported formats: CSV, TSV, TXT, Excel (.xlsx, .xls)"
        )

        if settings['uploaded_file']:
            file_name = settings['uploaded_file'].name
            file_ext = file_name.split('.')[-1].lower()

            if file_ext in ['xlsx', 'xls']:
                st.info(f"📊 Excel file: {file_name}")
                settings['excel_sheet'] = st.text_input(
                    "Sheet name (optional)",
                    value="",
                    help="Leave empty to read the first sheet"
                )
            else:
                st.info(f"📄 Text file: {file_name}")
                settings['excel_sheet'] = ""
        else:
            settings['excel_sheet'] = ""

        settings['delimiter'] = st.selectbox(
            "Delimiter (for CSV/TSV)",
            [",", ";", "\t", "|"],
            index=0,
        )

        # ── AUTO-LOAD INTO SESSION STATE ──────────────────────────────────────
        # Load the file whenever a new file is uploaded or delimiter changes.
        # This makes session_state["current_df"] available to ALL tabs.
        if settings['uploaded_file'] is not None:
            file_id = f"{settings['uploaded_file'].name}_{settings['delimiter']}_{settings.get('excel_sheet','')}"
            if st.session_state.get("loaded_file_name") != file_id:
                try:
                    df = _load_file(
                        settings['uploaded_file'],
                        settings['delimiter'],
                        settings.get('excel_sheet', '')
                    )
                    st.session_state["current_df"] = df
                    st.session_state["loaded_file_name"] = file_id
                    st.session_state["df_history"] = []  # Reset history on new file
                    st.success(f"✅ Loaded {len(df):,} rows × {len(df.columns)} columns")
                except Exception as e:
                    st.error(f"Failed to load file: {e}")
        else:
            # File removed — reset state
            if st.session_state.get("loaded_file_name") is not None:
                st.session_state["current_df"] = None
                st.session_state["loaded_file_name"] = None
                st.session_state["df_history"] = []
        # ─────────────────────────────────────────────────────────────────────

        st.markdown("---")
        st.header("🤖 AI Features")
        settings['use_ai_suggestions'] = st.checkbox("AI Column Type Suggestions", value=True)
        settings['use_ai_imputation'] = st.checkbox("AI Categorical Imputation", value=False)

        st.markdown("---")
        st.header("🔧 Cleaning Options")
        settings['knn_neighbors'] = st.slider("KNN neighbors", 1, 10, DEFAULT_KNN_NEIGHBORS)
        settings['contamination'] = st.slider(
            "Outlier contamination", 0.0, 0.2,
            DEFAULT_CONTAMINATION, step=0.01
        )
        settings['do_cat_impute'] = st.checkbox("Impute categorical by mode", value=True)
        settings['drop_exact_dup'] = st.checkbox("Drop exact duplicates", value=True)

        st.markdown("---")
        st.header("🔢 Integer Columns")
        settings['manual_integer_cols'] = st.text_input(
            "Additional integer columns (comma-separated)",
            placeholder="e.g., age, count, year",
        )

        st.markdown("---")

        if st.button("↶ Undo Last Operation"):
            success, operation = undo_last_operation()
            if success:
                st.success(f"✅ Undone: {operation}")
                st.rerun()
            else:
                st.warning("No operations to undo")

        st.markdown("---")
        with st.expander("📁 Supported File Formats"):
            st.markdown("""
            **Text Files:**
            - `.csv` - Comma-separated values
            - `.tsv` - Tab-separated values
            - `.txt` - Text files (specify delimiter)

            **Excel Files:**
            - `.xlsx` - Excel 2007+ format
            - `.xls` - Excel 97-2003 format
            """)

    return settings