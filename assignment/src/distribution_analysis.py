import pandas as pd
import numpy as np
from typing import Dict, Tuple
from .config import TARGET_PARAMETERS

class DistributionAnalyzer:
    def __init__(self, threshold: float = 200.0):
        self.hazard_threshold = threshold

    def calculate_hazard_probability(self, df: pd.DataFrame, col: str = "pm25") -> float:
        """
        Task 3: Calculate the probability of 'Extreme Hazard' events (PM2.5 > 200 µg/m³).
        """
        if col not in df.columns or df.empty:
            return 0.0
        
        hazard_count = len(df[df[col] > self.hazard_threshold])
        total_count = len(df)
        return (hazard_count / total_count) if total_count > 0 else 0.0

    def get_percentile(self, df: pd.DataFrame, percentile: float = 99, col: str = "pm25") -> float:
        """
        Returns the specified percentile for a pollutant.
        """
        if col not in df.columns or df.empty:
            return 0.0
        return np.percentile(df[col].dropna(), percentile)

    def get_peak_data(self, df: pd.DataFrame, col: str = "pm25") -> pd.DataFrame:
        """
        Prepares data for a histogram/density plot optimized for reveal peaks.
        Using a standard linear scale.
        """
        return df[[col]].dropna()

    def get_tail_data(self, df: pd.DataFrame, col: str = "pm25") -> pd.DataFrame:
        """
        Prepares data for a plot optimized for revealing the long tail.
        This could be a log-transformed distribution or a CCDF (Complementary Cumulative Distribution Function).
        """
        data = df[col].dropna()
        # Sort for CCDF
        sorted_data = np.sort(data)
        ccdf = 1. - np.arange(len(sorted_data)) / len(sorted_data)
        return pd.DataFrame({
            "value": sorted_data,
            "ccdf": ccdf
        })

    def get_technical_justification(self) -> str:
        return (
            "The tail-revealing plot (Log-scale or CCDF) offers a more 'honest' depiction of rare, hazardous events "
            "because it prevents extreme values from being visually crushed into a single narrow bin at the end of a "
            "linear histogram. Linear scales prioritize the mode (the most common values), effectively hiding the "
            "variance and magnitude of outliers. A CCDF specifically shows exactly how much of the data exceeds a "
            "certain threshold, ensuring the 'long tail' is numerically and visually explicit."
        )
