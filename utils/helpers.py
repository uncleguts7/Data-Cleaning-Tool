"""General helper functions."""

from datetime import datetime
from config.settings import EXPORT_DATETIME_FORMAT
import pandas as pd


def get_timestamp() -> str:
    """Get current timestamp in YYYYMMDD_HHMMSS format.
    
    Returns:
        Formatted timestamp string
    """
    return datetime. now().strftime("%Y%m%d_%H%M%S")


def get_formatted_timestamp() -> str:
    """Get current timestamp in readable format.
    
    Returns:
        Formatted timestamp string
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def download_link_df(df: pd.DataFrame, name: str = "cleaned.csv") -> bytes:
    df_export = df.copy()

    for col in df_export.columns:
        if pd.api.types.is_datetime64_any_dtype(df_export[col]):
            #df_export[col] = df_export[col].dt.strftime("%Y-%m-%d")
            df_export[col] = df_export[col].dt.strftime(EXPORT_DATETIME_FORMAT)

    csv = df_export.to_csv(index=False).encode('utf-8')
    return csv


def missing_summary(df: pd. DataFrame) -> pd. DataFrame:
    """Generate a summary of missing values in the dataframe.
    
    Args:
        df: Input dataframe
        
    Returns:
        Dataframe with missing value counts and percentages
    """
    miss = df.isnull().sum()
    pct = (miss / len(df) * 100).round(2)
    return pd.DataFrame({
        "missing": miss, 
        "percent": pct
    }). sort_values("missing", ascending=False)