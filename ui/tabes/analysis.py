"""Analysis tab UI - Enhanced version with interactive visualizations."""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from utils.data_utils import infer_column_types


def render_analysis_tab():
    """Render the enhanced analysis tab content."""
    st.subheader("📊 Data Analysis & Exploration")
    
    if st.session_state["current_df"] is None:
        st.info("No data available for analysis yet. Please upload and process a dataset first.")
        return
    
    df = st.session_state["current_df"]
    
    # Get column types
    col_types = infer_column_types(df)
    numeric_cols = [c for c, t in col_types.items() if t == "numeric"]
    categorical_cols = [c for c, t in col_types. items() if t == "categorical"]
    
    # Overview metrics
    st.markdown("### 📈 Dataset Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Rows", f"{len(df):,}")
    with col2:
        st.metric("Total Columns", f"{len(df.columns)}")
    with col3:
        st.metric("Numeric Columns", len(numeric_cols))
    with col4:
        st. metric("Categorical Columns", len(categorical_cols))
    
    # Missing data overview
    missing_total = df.isnull().sum(). sum()
    total_cells = df.shape[0] * df.shape[1]
    completeness = ((total_cells - missing_total) / total_cells) * 100
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Data Completeness", f"{completeness:.1f}%")
    with col2:
        st.metric("Missing Values", f"{missing_total:,}")
    
    st.markdown("---")
    
    # Create tabs for different analysis sections
    analysis_tab1, analysis_tab2, analysis_tab3, analysis_tab4 = st.tabs([
        "📋 Statistics",
        "🔥 Correlation Matrix", 
        "📊 Distribution Plots",
        "🔍 Column Explorer"
    ])
    
    # Tab 1: Descriptive Statistics
    with analysis_tab1:
        render_statistics_section(df, numeric_cols, categorical_cols)
    
    # Tab 2: Correlation Analysis
    with analysis_tab2:
        render_correlation_section(df, numeric_cols)
    
    # Tab 3: Distribution Plots
    with analysis_tab3:
        render_distribution_section(df, numeric_cols, categorical_cols)
    
    # Tab 4: Column Explorer
    with analysis_tab4:
        render_column_explorer(df, col_types)


def render_statistics_section(df: pd.DataFrame, numeric_cols: list, categorical_cols: list):
    """Render the descriptive statistics section."""
    st.markdown("#### 📋 Descriptive Statistics")
    
    stat_type = st.radio(
        "Select statistics type:",
        ["Numeric Columns", "Categorical Columns", "All Columns"],
        horizontal=True
    )
    
    if stat_type == "Numeric Columns":
        if numeric_cols:
            stats_df = df[numeric_cols].describe(). T
            stats_df['missing'] = df[numeric_cols].isnull().sum()
            stats_df['missing_%'] = (stats_df['missing'] / len(df) * 100).round(2)
            st.dataframe(stats_df, use_container_width=True)
        else:
            st.info("No numeric columns found in the dataset.")
    
    elif stat_type == "Categorical Columns":
        if categorical_cols:
            cat_stats = []
            for col in categorical_cols:
                cat_stats. append({
                    'Column': col,
                    'Unique Values': df[col].nunique(),
                    'Most Common': df[col].mode()[0] if len(df[col]. mode()) > 0 else 'N/A',
                    'Most Common Count': df[col]. value_counts().iloc[0] if len(df[col]. value_counts()) > 0 else 0,
                    'Missing': df[col].isnull().sum(),
                    'Missing %': round(df[col].isnull().sum() / len(df) * 100, 2)
                })
            st.dataframe(pd.DataFrame(cat_stats), use_container_width=True)
        else:
            st.info("No categorical columns found in the dataset.")
    
    else:
        st.dataframe(df.describe(include="all"). T, use_container_width=True)


def render_correlation_section(df: pd.DataFrame, numeric_cols: list):
    """Render the correlation analysis section with both static and interactive heatmaps."""
    st.markdown("#### 🔥 Correlation Analysis")
    
    if len(numeric_cols) < 2:
        st.warning("Need at least 2 numeric columns to compute correlations.")
        return
    
    # Column selection for correlation
    st.markdown("##### Select Columns for Correlation")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_cols = st.multiselect(
            "Choose columns to include:",
            numeric_cols,
            default=numeric_cols[:min(10, len(numeric_cols))],
            help="Select numeric columns to include in the correlation matrix"
        )
    with col2:
        corr_method = st.selectbox(
            "Correlation method:",
            ["pearson", "spearman", "kendall"],
            help="Pearson: linear correlation, Spearman: rank correlation, Kendall: ordinal correlation"
        )
    
    if len(selected_cols) < 2:
        st.warning("Please select at least 2 columns.")
        return
    
    # Calculate correlation matrix
    corr_matrix = df[selected_cols]. corr(method=corr_method)
    
    # Display options
    st.markdown("##### Visualization Options")
    col1, col2, col3 = st.columns(3)
    with col1:
        show_interactive = st.checkbox("Interactive Heatmap", value=True)
    with col2:
        show_static = st. checkbox("Static Heatmap", value=False)
    with col3:
        show_table = st.checkbox("Correlation Table", value=False)
    
    # Interactive Heatmap using Plotly
    if show_interactive:
        st.markdown("##### 🎯 Interactive Correlation Heatmap")
        st.caption("Hover over cells to see exact values.  Click and drag to zoom.  Double-click to reset.")
        
        if PLOTLY_AVAILABLE:
            render_interactive_heatmap(corr_matrix, selected_cols)
        else:
            st.warning("Plotly is not installed. Install it with `pip install plotly` for interactive heatmaps.")
            show_static = True
    
    # Static Heatmap using Seaborn
    if show_static:
        st.markdown("##### 📊 Static Correlation Heatmap")
        render_static_heatmap(corr_matrix, selected_cols)
    
    # Correlation Table
    if show_table:
        st.markdown("##### 📋 Correlation Matrix Table")
        styled_corr = corr_matrix. style.background_gradient(cmap='RdYlBu_r', vmin=-1, vmax=1)
        st.dataframe(styled_corr, use_container_width=True)
    
    # Top correlations
    st. markdown("##### 🔝 Strongest Correlations")
    render_top_correlations(corr_matrix)


def render_interactive_heatmap(corr_matrix: pd.DataFrame, columns: list):
    """Render an interactive correlation heatmap using Plotly."""
    
    # Create custom hover text
    hover_text = []
    for i, row in enumerate(columns):
        hover_row = []
        for j, col in enumerate(columns):
            corr_value = corr_matrix.iloc[i, j]
            hover_row.append(
                f"<b>{row}</b> vs <b>{col}</b><br>"
                f"Correlation: {corr_value:.3f}"
            )
        hover_text. append(hover_row)
    
    # Create the heatmap with updated colorbar syntax
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=columns,
        y=columns,
        hoverongaps=False,
        hoverinfo='text',
        text=hover_text,
        colorscale='RdBu_r',
        zmid=0,
        zmin=-1,
        zmax=1,
        colorbar=dict(
            title=dict(
                text="Correlation",
                side="right"
            ),
            tickvals=[-1, -0.5, 0, 0.5, 1],
            ticktext=["-1. 0", "-0. 5", "0. 0", "0. 5", "1. 0"]
        )
    )
    )
    
    # Add correlation values as annotations
    annotations = []
    for i, row in enumerate(columns):
        for j, col in enumerate(columns):
            val = corr_matrix.iloc[i, j]
            # Choose text color based on background
            text_color = 'white' if abs(val) > 0.5 else 'black'
            annotations.append(
                dict(
                    x=col,
                    y=row,
                    text=f"{val:.2f}",
                    font=dict(color=text_color, size=10),
                    showarrow=False
                )
            )
    
    # Calculate appropriate height based on number of columns
    n_cols = len(columns)
    height = max(400, min(600, n_cols * 45))
    
    fig.update_layout(
        title=dict(
            text="Interactive Correlation Heatmap",
            x=0.5,
            font=dict(size=14)
        ),
        annotations=annotations,
        xaxis=dict(
            title="",
            tickangle=45,
            side="bottom"
        ),
        yaxis=dict(
            title="",
            autorange="reversed"
        ),
        height=height,
        margin=dict(l=80, r=40, t=60, b=80)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add zoom controls info
    with st.expander("ℹ️ How to use the interactive heatmap"):
        st.markdown("""
        - **Hover**: See exact correlation values
        - **Click + Drag**: Zoom into a specific area
        - **Double-click**: Reset zoom
        - **Scroll**: Zoom in/out
        - **Download**: Use the camera icon to save as PNG
        """)


def render_static_heatmap(corr_matrix: pd.DataFrame, columns: list):
    n_cols = len(columns)

    # 🔹 Compact fixed size (thumbnail style)
    fig, ax = plt.subplots(figsize=(4.5, 3.8))

    # 🧠 Disable annotations لو الأعمدة كتير
    show_annot = n_cols <= 6

    sns.heatmap(
        corr_matrix,
        annot=show_annot,
        fmt=".2f",
        cmap="RdBu_r",
        center=0,
        vmin=-1,
        vmax=1,
        square=True,
        linewidths=0.4,
        cbar_kws={"shrink": 0.6},
        annot_kws={"size": 8},
        ax=ax
    )

    ax.set_title("Correlation Heatmap", fontsize=10, pad=6)

    # 🔹 Smaller ticks
    ax.tick_params(axis='x', labelsize=7)
    ax.tick_params(axis='y', labelsize=7)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)

    plt.tight_layout()

    # 🔥 المهم جدًا: امنع التمدد
    st.pyplot(fig, use_container_width=False)

    plt.close()



def render_top_correlations(corr_matrix: pd.DataFrame, top_n: int = 10):
    """Display the top positive and negative correlations."""
    
    # Get upper triangle of correlation matrix (excluding diagonal)
    upper_tri = corr_matrix.where(
        np.triu(np.ones(corr_matrix. shape), k=1).astype(bool)
    )
    
    # Stack and sort
    correlations = upper_tri.stack().reset_index()
    correlations.columns = ['Variable 1', 'Variable 2', 'Correlation']
    correlations['Abs Correlation'] = correlations['Correlation']. abs()
    correlations = correlations. sort_values('Abs Correlation', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔺 Top Positive Correlations**")
        positive = correlations[correlations['Correlation'] > 0]. head(top_n)
        if len(positive) > 0:
            for _, row in positive.iterrows():
                corr_val = row['Correlation']
                color = get_correlation_color(corr_val)
                st.markdown(
                    f"<span style='color:{color}'>●</span> "
                    f"**{row['Variable 1']}** ↔ **{row['Variable 2']}**: {corr_val:.3f}",
                    unsafe_allow_html=True
                )
        else:
            st. info("No positive correlations found.")
    
    with col2:
        st. markdown("**🔻 Top Negative Correlations**")
        negative = correlations[correlations['Correlation'] < 0].head(top_n)
        if len(negative) > 0:
            for _, row in negative.iterrows():
                corr_val = row['Correlation']
                color = get_correlation_color(corr_val)
                st. markdown(
                    f"<span style='color:{color}'>●</span> "
                    f"**{row['Variable 1']}** ↔ **{row['Variable 2']}**: {corr_val:.3f}",
                    unsafe_allow_html=True
                )
        else:
            st.info("No negative correlations found.")


def get_correlation_color(corr: float) -> str:
    """Get color based on correlation value."""
    if corr >= 0.7:
        return "#1a9850"  # Strong positive - dark green
    elif corr >= 0.4:
        return "#91cf60"  # Moderate positive - light green
    elif corr >= 0:
        return "#d9ef8b"  # Weak positive - yellow-green
    elif corr >= -0.4:
        return "#fee08b"  # Weak negative - yellow
    elif corr >= -0.7:
        return "#fc8d59"  # Moderate negative - orange
    else:
        return "#d73027"  # Strong negative - red


def render_distribution_section(df: pd. DataFrame, numeric_cols: list, categorical_cols: list):
    """Render distribution plots for columns."""
    st.markdown("#### 📊 Distribution Analysis")
    
    plot_type = st.radio(
        "Select plot type:",
        ["Numeric Distributions", "Categorical Distributions", "Box Plots"],
        horizontal=True
    )
    
    if plot_type == "Numeric Distributions":
        if not numeric_cols:
            st.info("No numeric columns available.")
            return
        
        selected_col = st.selectbox("Select column:", numeric_cols)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Histogram
            fig, ax = plt.subplots(figsize=(5, 3.5))
            df[selected_col]. hist(bins=30, ax=ax, color='#3498db', edgecolor='white', alpha=0.7)
            ax. set_title(f'Distribution of {selected_col}', fontsize=10, fontweight='bold')
            ax.set_xlabel(selected_col, fontsize=8)
            ax.set_ylabel('Frequency', fontsize=8)
            ax.tick_params(labelsize=7)
            plt. tight_layout()
            st.pyplot(fig)
            plt.clf()
            plt.close()
        
        with col2:
            # Box plot
            fig, ax = plt. subplots(figsize=(5, 3.5))
            df[selected_col]. plot. box(ax=ax, color=dict(boxes='#3498db', whiskers='#7f8c8d', 
                                                         medians='#e74c3c', caps='#7f8c8d'))
            ax.set_title(f'Box Plot of {selected_col}', fontsize=10, fontweight='bold')
            ax.tick_params(labelsize=7)
            plt.tight_layout()
            st. pyplot(fig)
            plt.clf()
            plt.close()
        
        # Summary statistics for selected column
        st. markdown(f"**Summary Statistics for {selected_col}:**")
        stats = df[selected_col].describe()
        stats_cols = st.columns(4)
        stats_cols[0]. metric("Mean", f"{stats['mean']:.2f}")
        stats_cols[1].metric("Std Dev", f"{stats['std']:.2f}")
        stats_cols[2].metric("Min", f"{stats['min']:.2f}")
        stats_cols[3].metric("Max", f"{stats['max']:.2f}")
    
    elif plot_type == "Categorical Distributions":
        if not categorical_cols:
            st. info("No categorical columns available.")
            return
        
        selected_col = st. selectbox("Select column:", categorical_cols)
        
        # Value counts
        value_counts = df[selected_col].value_counts(). head(15)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart
            fig, ax = plt.subplots(figsize=(5, 3.5))
            value_counts.plot(kind='bar', ax=ax, color='#9b59b6', edgecolor='white', alpha=0.8)
            ax. set_title(f'Distribution of {selected_col}', fontsize=10, fontweight='bold')
            ax.set_xlabel(selected_col, fontsize=8)
            ax.set_ylabel('Count', fontsize=8)
            plt.xticks(rotation=45, ha='right', fontsize=7)
            ax.tick_params(labelsize=7)
            plt.tight_layout()
            st.pyplot(fig)
            plt. clf()
            plt.close()
        
        with col2:
            # Pie chart
            fig, ax = plt. subplots(figsize=(5, 3.5))
            top_values = value_counts. head(8). copy()
            if len(value_counts) > 8:
                other_sum = value_counts. iloc[8:].sum()
                top_values = pd.concat([top_values, pd.Series({'Other': other_sum})])
            top_values.plot(kind='pie', ax=ax, autopct='%1.1f%%', startangle=90,
                           colors=plt.cm. Pastel1. colors, textprops={'fontsize': 7})
            ax. set_title(f'Proportion of {selected_col}', fontsize=10, fontweight='bold')
            ax.set_ylabel('')
            plt.tight_layout()
            st.pyplot(fig)
            plt. clf()
            plt.close()
    
    else:  # Box Plots
        if not numeric_cols:
            st.info("No numeric columns available.")
            return
        
        selected_cols = st.multiselect(
            "Select columns for comparison:",
            numeric_cols,
            default=numeric_cols[:min(5, len(numeric_cols))]
        )
        
        if selected_cols:
            fig, ax = plt. subplots(figsize=(8, 4))
            df[selected_cols]. boxplot(ax=ax, patch_artist=True,
                                      boxprops=dict(facecolor='#3498db', alpha=0.6),
                                      medianprops=dict(color='#e74c3c', linewidth=2))
            ax.set_title('Box Plot Comparison', fontsize=11, fontweight='bold')
            plt. xticks(rotation=45, ha='right', fontsize=8)
            ax.tick_params(labelsize=7)
            plt. tight_layout()
            st.pyplot(fig)
            plt.clf()
            plt.close()


def render_column_explorer(df: pd.DataFrame, col_types: dict):
    """Render the column explorer section."""
    st. markdown("#### 🔍 Column Explorer")
    
    selected_col = st. selectbox(
        "Select a column to explore:",
        df.columns. tolist()
    )
    
    if selected_col:
        col_data = df[selected_col]
        col_type = col_types.get(selected_col, "unknown")
        
        # Column info header
        st.markdown(f"**Column: `{selected_col}`** (Type: {col_type})")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Values", len(col_data))
        with col2:
            st.metric("Non-Null Values", col_data.notna().sum())
        with col3:
            st.metric("Missing Values", col_data.isnull(). sum())
        with col4:
            st.metric("Unique Values", col_data.nunique())
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Sample Values (First 10):**")
            st.dataframe(
                col_data. head(10).to_frame(),
                use_container_width=True,
                height=300
            )
        
        with col2:
            if col_type == "numeric":
                st. markdown("**Statistics:**")
                stats = col_data. describe()
                st.dataframe(stats.to_frame(), use_container_width=True)
            else:
                st.markdown("**Value Counts (Top 10):**")
                value_counts = col_data.value_counts().head(10). to_frame()
                value_counts.columns = ['Count']
                st.dataframe(value_counts, use_container_width=True)