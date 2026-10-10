"""Column matching tab UI."""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from services.matching import find_matching_columns


def render_column_matching_tab():
    """Render the column matching tab content."""
    st.subheader("💯 Column Matching & Relationships")
    
    if st.session_state["current_df"] is None:
        st.warning("Please upload data first.")
        return
    
    df = st.session_state["current_df"]
    
    st.markdown("### Find Matching Values Between Columns")
    
    col1_select = st.selectbox("Select Column 1", df.columns, key="match_col1")
    col2_select = st.selectbox("Select Column 2", df.columns, key="match_col2")
    match_threshold = st.slider("Matching Threshold (%)", 50, 100, 80)
    
    if st.button("🔍 Find Matches"):
        if col1_select != col2_select:
            with st.spinner("Finding matches..."):
                matches = find_matching_columns(df, col1_select, col2_select, match_threshold)
                
                if matches:
                    st.success(f"Found {len(matches)} matches!")
                    
                    match_df = pd. DataFrame(matches)
                    st.dataframe(match_df)
                    
                    st.markdown("### Match Score Distribution")
                    fig, ax = plt. subplots(figsize=(8, 4))
                    ax.hist([m["score"] for m in matches], bins=20, color='#4CAF50', alpha=0.7)
                    ax. set_xlabel("Match Score")
                    ax.set_ylabel("Frequency")
                    ax. set_title("Distribution of Match Scores")
                    st.pyplot(fig)
                    plt.clf()
                else:
                    st. info("No matches found above threshold.")
        else:
            st.warning("Please select different columns.")