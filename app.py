"""
AI Data Cleaning & Analysis Application
Main entry point for the Streamlit application. 

Author: Mohamed Alaa
Version: 2.0
"""
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from config. settings import PAGE_CONFIG
from ui.components import render_header, init_session_state, render_sidebar
from ui.tabes import (
    render_home_tab,
    render_error_detection_tab,
    render_clean_data_tab,
    render_column_matching_tab,
    render_analysis_tab,
    render_about_tab,
    render_text_cleaning_tab
)


def main():
    """Main application entry point."""
    # Page configuration
    st.set_page_config(**PAGE_CONFIG)
    
    # Initialize session state
    init_session_state()
    
    # Render header
    render_header()
    
    # Render sidebar and get settings
    settings = render_sidebar()
    
    # Main layout with tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🏠 Home",
        "🚨 Error Detection",
        "🧹 Clean Data",
        "✍️ Text Cleaner",
        "💯 Column Matching",
        "📊 Analysis",
        "📝 About",
    ])
    
    with tab1:
        render_home_tab(settings['uploaded_file'])
    
    with tab2:
        render_error_detection_tab(
            settings['uploaded_file'],
            settings['delimiter'],
            settings['use_ai_suggestions'],
            settings. get('excel_sheet', '')
        )
    
    with tab3:
        render_clean_data_tab(settings)
    
    with tab4:
        render_text_cleaning_tab()
    
    with tab5:
        render_column_matching_tab()
    
    with tab6:
        render_analysis_tab()
    
    with tab7:
        render_about_tab()
    
    # Footer
    st.markdown("---")
    st.caption("AI Data Cleaning & Analysis Tool v2.0 | Privacy-First | Local Processing | Supports CSV & Excel")


if __name__ == "__main__":
    main()