"""Data cleaning operations."""

import pandas as pd
import numpy as np
import re
import streamlit as st
from sklearn.ensemble import IsolationForest
from config.settings import PLACEHOLDER_VALUES


# Placeholder values to treat as missing

# PLACEHOLDER_VALUES = [
#     'UNKNOWN', 'Unknown', 'unknown',
#     'ERROR', 'Error', 'error',
#     'N/A', 'n/a', 'NA', 'na', 'N/a',
#     'NULL', 'Null', 'null',
#     'NONE', 'None', 'none',
#     'NAN', 'NaN', 'nan',
#     'MISSING', 'Missing', 'missing',
#     'NOT AVAILABLE', 'Not Available', 'not available',
#     'NOT FOUND', 'Not Found', 'not found',
#     'UNDEFINED', 'Undefined', 'undefined',
#     'INVALID', 'Invalid', 'invalid',
#     'EMPTY', 'Empty', 'empty',
#     '-', '--', '---',
#     '? ', '?? ', '??? ',
#     '. ', '..', '.. .',
#     '#N/A', '#VALUE!', '#REF!', '#DIV/0!', '#NAME?',
#     '', ' ',
# ]


def convert_boolean_to_int(df: pd.DataFrame) -> pd.DataFrame:
    bool_cols = df.select_dtypes(include=['bool']).columns
    if len(bool_cols) > 0:
        df[bool_cols] = df[bool_cols].astype(int)
    return df



def detect_placeholder_values(df:  pd.DataFrame) -> dict:
    """Detect placeholder values in the dataframe that should be treated as missing. 
    
    Args:
        df:  Input dataframe
        
    Returns:
        Dictionary with detection results
    """
    results = {
        "total_found": 0,
        "by_column": {},
        "by_value": {}
    }
    
    for col in df.columns:
        col_count = 0
        col_values = {}
        
        for idx, value in df[col]. items():
            if pd.isna(value):
                continue
            
            str_value = str(value).strip()
            
            if str_value in PLACEHOLDER_VALUES: 
                col_count += 1
                
                if str_value not in col_values:
                    col_values[str_value] = 0
                col_values[str_value] += 1
                
                # Track globally by value
                if str_value not in results["by_value"]: 
                    results["by_value"][str_value] = 0
                results["by_value"][str_value] += 1
        
        if col_count > 0:
            results["by_column"][col] = {
                "count":  col_count,
                "values": col_values
            }
            results["total_found"] += col_count
    
    return results


def convert_placeholders_to_nan(df:  pd.DataFrame, placeholder_values: list = None) -> tuple: 
    """Convert placeholder values to NaN so they can be imputed.
    
    Args:
        df: Input dataframe
        placeholder_values:  Optional custom list of placeholder values
        
    Returns: 
        Tuple of (cleaned dataframe, conversion report)
    """
    if placeholder_values is None:
        placeholder_values = PLACEHOLDER_VALUES
    
    df_copy = df. copy()
    conversion_report = {
        "total_converted": 0,
        "by_column": {},
        "by_value":  {}
    }
    
    for col in df_copy.columns:
        col_converted = 0
        
        for idx, value in df_copy[col].items():
            if pd.isna(value):
                continue
            
            str_value = str(value).strip()
            
            if str_value in placeholder_values: 
                df_copy. loc[idx, col] = np.nan
                col_converted += 1
                
                # Track by value type
                if str_value not in conversion_report["by_value"]:
                    conversion_report["by_value"][str_value] = 0
                conversion_report["by_value"][str_value] += 1
        
        if col_converted > 0:
            conversion_report["by_column"][col] = col_converted
            conversion_report["total_converted"] += col_converted
    
    return df_copy, conversion_report


def drop_exact_duplicates(df: pd. DataFrame) -> tuple:
    """Remove exact duplicate rows from the dataframe.
    
    Args: 
        df: Input dataframe
        
    Returns:
        Tuple of (cleaned dataframe, number of removed rows)
    """
    before = len(df)
    df2 = df.drop_duplicates().reset_index(drop=True)
    removed = before - len(df2)
    return df2, removed


def clean_special_characters(df:  pd.DataFrame, column: str) -> pd.DataFrame:

    if pd.api.types.is_datetime64_any_dtype(df[column]):
        return df
    def clean_value(val):
        if pd.isna(val):
            return val
        
        val_str = str(val).strip()
        
        # Check if it's an email
        if '@' in val_str and '.' in val_str. split('@')[-1]:
            return val_str
        
        # Check if it's a URL
        if 'http' in val_str or 'www.' in val_str: 
            return val_str
        
        # For names and other text, remove special characters
        # Keep letters, numbers, spaces, Arabic characters, and basic punctuation
        cleaned = re.sub(r'[^\w\s\u0600-\u06FF.-]', '', val_str)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned if cleaned else val_str
    
    df[column] = df[column].apply(clean_value)
    return df


def remove_outliers_isolationforest(
    df: pd. DataFrame,
    numeric_cols: list,
    contamination:  float = 0.03,
    random_state: int = 42
) -> tuple:
    df = convert_boolean_to_int(df)
    if len(numeric_cols) == 0:
        return df, 0
    
    try:
        iso = IsolationForest(contamination=contamination, random_state=random_state)
        arr = df[numeric_cols]. values. astype(float)
        
        # Handle NaN values
        if np.isnan(arr).any():
            med = np.nanmedian(arr, axis=0)
            inds = np.where(np.isnan(arr))
            arr[inds] = np.take(med, inds[1])
        
        preds = iso.fit_predict(arr)
        mask = (preds == 1)  # Keep inliers
        outliers = int((preds == -1).sum())
        df_clean = df[mask].reset_index(drop=True)
        return df_clean, outliers
    except Exception as e:
        st.warning(f"Outlier detection failed: {e}")
        return df, 0