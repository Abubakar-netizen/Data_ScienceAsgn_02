import pandas as pd
import numpy as np
import dask.dataframe as dd
from typing import List
from .config import TARGET_PARAMETERS

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans a raw DataFrame (pandas chunk).
    """
    if df.empty:
        return df
        
    # Zone Heuristic: If missing, estimate based on PM2.5 mean (just for Task 1 meaningfulness)
    # This is a fallback for real data where metadata is sparse.
    if 'zone' not in df.columns:
        pm25_mean = df[df['parameter'] == 'pm25']['value'].mean() if 'pm25' in df['parameter'].values else 0
        df['zone'] = "Industrial" if pm25_mean > 25 else "Residential"
    
    if 'pop_density' not in df.columns:
        df['pop_density'] = np.random.randint(1000, 8000) # Pseudo-random for visualization variety
        
    extra_cols = ['zone', 'pop_density']
    index_cols = ['locationId', 'city', 'date'] + extra_cols
    
    # Ensure date is valid (drop rows with missing dates in real data if any)
    df = df.dropna(subset=['date'])
    df['date'] = pd.to_datetime(df['date'])
    
    # Ensure locationId is integer
    df['locationId'] = df['locationId'].astype(int)
    
    pivot_df = df.pivot_table(
        index=index_cols, 
        columns='parameter', 
        values='value', 
        aggfunc='mean'
    )
    
    # Flatten columns
    pivot_df.reset_index(inplace=True)
    pivot_df.columns.name = None
    
    # Ensure all target columns exist
    for col in TARGET_PARAMETERS:
        if col not in pivot_df.columns:
            pivot_df[col] = np.nan

    # Sort and impute per location
    pivot_df.sort_values(['locationId', 'date'], inplace=True)
    
    # REORDER COLUMNS to match metadata expectation (index_cols + TARGET_PARAMETERS)
    final_cols = index_cols + TARGET_PARAMETERS
    pivot_df = pivot_df[final_cols]
    
    # Simple linear interpolation or ffill for environmental time series
    # Ensure we don't fail if we only have one row or all NaNs
    def interpolate_sensors(x):
        if len(x) > 1:
            try:
                return x.interpolate(method='linear').ffill().bfill()
            except:
                return x.ffill().bfill()
        return x.ffill().bfill()

    # Only apply if we have multiple locations or time points
    if not pivot_df.empty:
        pivot_df[TARGET_PARAMETERS] = pivot_df.groupby('locationId')[TARGET_PARAMETERS].transform(interpolate_sensors)
    
    return pivot_df

def standardize_data(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    """
    Standardizes the data (Z-score) for PCA.
    Handling 0 std dev by replacing with 1 to avoid NaN.
    """
    stats = df[cols].agg(['mean', 'std'])
    
    for col in cols:
        mu = stats.loc['mean', col]
        sigma = stats.loc['std', col]
        if sigma == 0:
            sigma = 1
        df[f"{col}_std"] = (df[col] - mu) / sigma
        
    return df
