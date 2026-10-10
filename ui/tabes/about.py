"""About tab UI."""

import streamlit as st


def render_about_tab():
    """Render the about tab content."""
    st.subheader("About This Tool")
    st.markdown("""
    ### 🚀 Enhanced Features
    
    **Version 2.0** includes:
    
    1. **🤖 AI-Powered Type Suggestions**
       - Intelligent detection of column data types
       - Context-aware recommendations
       - Confidence scoring
    
    2.  **🎯 Advanced Categorical Imputation** ⭐ ENHANCED v2. 1
       - **Geographical validation**: Built-in database of 200+ cities across 10+ countries
       - **Smart city-country matching**: Turkey → Istanbul/Ankara (NOT Xinjiang!)
       - **Context-aware imputation**: Considers relationships between columns
       - **Multi-level validation**:
         * Level 1: Validated geographical match (Egypt → Cairo/Alexandria)
         * Level 2: Same country from dataset
         * Level 3: Fallback to most common
       - **Detailed reporting**: See validation status for each imputed value
       - **Supports**: Arabic and English city/country names
       
    3. **🧼 Smart Special Character Cleaning** 🆕 NEW
       - **Intelligent detection**: Removes @#$ from names
       - **Preserves context**: Keeps @ in emails, special chars in URLs 
       - **Examples**:
         * "@#Mohamed$" → "Mohamed" ✅ 
         * "mohamed@email. com" → "mohamed@email.com" 🔒 (unchanged)
         * "https://example.com" → "https://example.com" 🌐 (unchanged) 
       - **Safe cleaning**: Never breaks valid data formats
    
    4. **🚨 Comprehensive Error Detection**
       - Missing value analysis
       - Duplicate detection
       - Outlier identification
       - Format inconsistency checks
    
    5. **💯 Column Matching**
       - Find relationships between columns
       - Fuzzy matching with configurable threshold
       - Visual match distribution
    
    6. **↶ Undo/Preview System**
       - Preview all changes before applying
       - Undo last operations
       - Complete operation history
    
    7. **🔢 Smart Integer Detection** ⭐ NEW
       - Auto-detects columns that should be integers (age, count, etc.)
       - Automatically rounds imputed values for discrete data
       - Supports both Arabic and English column names
       - Manual override option available
       - Prevents unrealistic decimal values (e.g., age = 33.4 → 33)
    
    ### 🔢 Integer Column Examples
    
    The system automatically detects and handles these column types:
    - **Ages** (age, عمر, سن) → Always whole numbers
    - **Counts** (count, عدد, quantity) → Discrete values
    - **Years** (year, سنة, عام) → No decimals
    - **IDs** (id, رقم) → Integer identifiers
    - **Scores/Ranks** (score, نقاط, rank, ترتيب)
    - **People counts** (students, employees, طلاب, موظفين)
    
    ### 📌 Context-Aware Imputation Example
    
    **Scenario:** You have a dataset with Name, Country, and City columns.  Some cities are missing. 
    
    | Name | Country | City |
    |------|---------|------|
    | Mohamed | Egypt | ???  |
    | Ahmed | Egypt | Cairo |
    | Ali | Egypt | Alexandria |
    | John | USA | ??? |
    | Mike | USA | New York |
    
    **Smart Imputation Process:**
    1. For Mohamed (Egypt): System finds other Egyptian records
    2.  Sees Cairo and Alexandria are common in Egypt
    3.  Imputes with most common: "Cairo"
    4. For John (USA): Finds USA records, imputes "New York"
    
    **Result:** Mohamed gets an Egyptian city, John gets a US city!  ✅
    
    Without context: Mohamed might randomly get "New York" ❌
    
    ---
    
    **Author:** Mohamed Alaa  
    **Version:** 2.0 - Enhanced Edition
    
    All processing is performed locally.  AI features can be enhanced with Claude API integration.
    """)