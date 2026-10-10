"""Data utility functions for type inference and analysis."""

import pandas as pd
import numpy as np
import re
from config. settings import INTEGER_KEYWORDS


def infer_column_types(df: pd.DataFrame) -> dict:
    """Infer the data type of each column in the dataframe.
    
    Args:
        df: Input dataframe
        
    Returns:
        Dictionary mapping column names to inferred types
    """
    types = {}
    for col in df.columns:
        s = df[col]
        if pd.api.types. is_numeric_dtype(s):
            types[col] = "numeric"
            continue
        
        try:
            sample_size = min(10, max(1, s.dropna().shape[0]))
            pd.to_datetime(s.dropna(). sample(sample_size))
            types[col] = "datetime"
            continue
        except Exception:
            pass
        
        uniq_ratio = s.nunique() / max(1, len(s))
        if uniq_ratio > 0.8 and s.dtype == object:
            types[col] = "text"
        else:
            types[col] = "categorical"
    return types


def should_be_integer(col_name: str, data_sample: pd.Series) -> bool:
    col_lower = col_name.lower()

    for keyword in INTEGER_KEYWORDS:
        if keyword in col_lower:
            return True

    non_null = data_sample.dropna()

    # 🔥 FIX: Boolean guard
    if non_null.dtype == bool:
        return True

    if len(non_null) > 0:
        try:
            is_int = np.all(np.abs(non_null.astype(float) - np.round(non_null.astype(float))) < 0.01)
            return is_int
        except Exception:
            return False

    return False



def heuristic_type_suggestion(col_name: str, sample_data: list) -> dict:
    """Heuristic-based type suggestion for a column.
    
    Args:
        col_name: Name of the column
        sample_data: List of sample values from the column
        
    Returns:
        Dictionary with type, confidence, and reason
    """
    col_lower = col_name.lower()
    
    # Check for email
    email_pattern = re.compile(r'^[a-zA-Z0-9. _%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    if any(email_pattern. match(str(val)) for val in sample_data if pd.notna(val)):
        return {"type": "email", "confidence": 0.9, "reason": "Matches email pattern"}
    
    # Check for phone
    if 'phone' in col_lower or 'tel' in col_lower:
        return {"type": "phone", "confidence": 0.85, "reason": "Column name suggests phone number"}
    
    # Check for ID
    if 'id' in col_lower and all(isinstance(val, (int, str)) for val in sample_data):
        return {"type": "id", "confidence": 0.9, "reason": "Column name suggests identifier"}
    
    # Check for URL
    if any('http' in str(val) or 'www.' in str(val) for val in sample_data):
        return {"type": "url", "confidence": 0.85, "reason": "Contains URL patterns"}
    
    # Check for date
    if 'date' in col_lower or 'time' in col_lower:
        return {"type": "datetime", "confidence": 0.8, "reason": "Column name suggests date/time"}
    
    # Check if numeric
    if all(isinstance(val, (int, float)) for val in sample_data):
        return {"type": "numeric", "confidence": 0.95, "reason": "All values are numeric"}
    
    # Check uniqueness for categorical vs text
    unique_ratio = len(set(sample_data)) / len(sample_data) if sample_data else 0
    if unique_ratio < 0.5:
        return {"type": "categorical", "confidence": 0.8, "reason": "Low unique value ratio"}
    else:
        return {"type": "text", "confidence": 0.7, "reason": "High unique value ratio"}


def ai_suggest_column_types(df: pd.DataFrame, sample_size: int = 5) -> dict:
    """Use AI/heuristics to suggest appropriate column types.
    
    Args:
        df: Input dataframe
        sample_size: Number of sample values to analyze
        
    Returns:
        Dictionary mapping column names to type suggestions
    """
    suggestions = {}
    
    for col in df.columns:
        sample_data = df[col].dropna(). head(sample_size). tolist()
        if len(sample_data) == 0:
            continue
        
        try:
            suggested = heuristic_type_suggestion(col, sample_data)
            suggestions[col] = suggested
        except Exception as e:
            suggestions[col] = {"type": "unknown", "confidence": 0.0, "reason": str(e)}
    
    return suggestions