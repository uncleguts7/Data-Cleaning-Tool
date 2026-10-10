# AI Data Cleaning & Analysis Tool

A local, privacy-first Streamlit application for automated data cleaning and quick exploratory analysis.
Suitable as an academic project / demo.

## Features
- Upload CSV / Excel files
- Numeric imputation with KNN
- Categorical imputation (mode)
- Exact + fuzzy duplicate removal
- Outlier detection with IsolationForest
- Correlation heatmap and distribution diagnostics
- Download cleaned CSV and cleaning report

## Requirements
Python 3.9+, see `requirements.txt`


## Install & Run (local)
1. Create & activate virtual environment:

Steps:
    =>  For linux: 
         source venv/bin/activate
        
        For Windows (PowerShell):
         venv\Scripts\Activate.ps1
         
    =>  pip install -r requirements.txt
    
    
    =>  streamlit run app.py
