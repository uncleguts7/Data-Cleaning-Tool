"""Home tab UI."""

import streamlit as st


def render_home_tab(uploaded_file):
    """Render the home tab content. 
    
    Args:
        uploaded_file: Uploaded file object or None
    """
    st.subheader("Overview")
    st.write("""
    Enhanced AI-powered data cleaning tool with:
    - **🤖 AI Type Suggestions**: Intelligent column type detection
    - **🎯 AI Imputation**: Smart categorical value filling
    - **🚨 Error Detection**: Comprehensive data quality checks
    - **💯 Column Matching**: Find relationships between columns
    - **↶ Undo/Preview**: Review changes before applying
    """)
    
    if uploaded_file:
        file_name = uploaded_file.name
        file_ext = file_name.split('.')[-1]. lower()
        
        if file_ext in ['xlsx', 'xls']:
            st.success(f"✅ Excel file uploaded: {file_name}")
        else:
            st. success(f"✅ File uploaded: {file_name}")
        
        # File info
        file_size = uploaded_file.size / 1024  # KB
        if file_size > 1024:
            file_size_mb = file_size / 1024
            st.info(f"📁 File size: {file_size_mb:.2f} MB")
        else:
            st.info(f"📁 File size: {file_size:.2f} KB")
    else:
        # Show upload instructions
        st.markdown("---")
        st.markdown("### 📤 Get Started")
        st.markdown("""
        Upload your data file using the sidebar to begin cleaning and analysis.
        
        **Supported formats:**
        
        | Format | Extension | Description |
        |--------|-----------|-------------|
        | CSV | `.csv` | Comma-separated values |
        | TSV | `.tsv` | Tab-separated values |
        | Text | `.txt` | Plain text with delimiter |
        | Excel | `.xlsx` | Excel 2007+ workbook |
        | Excel | `.xls` | Excel 97-2003 workbook |
        
        **Tips for best results:**
        - Ensure your file has headers in the first row
        - For Excel files with multiple sheets, specify the sheet name in the sidebar
        - Large files (>100MB) may take longer to process
        """)