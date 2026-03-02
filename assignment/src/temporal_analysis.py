import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List
from .config import PROCESSED_DATA_DIR, LOGS_DIR
from .utils import setup_logger

logger = setup_logger("temporal_analysis")

class TemporalAnalyzer:
    def __init__(self):
        self.data_path = PROCESSED_DATA_DIR / "cleaned_data.parquet"

    def load_data(self) -> pd.DataFrame:
        try:
            return pd.read_parquet(self.data_path)
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return pd.DataFrame()

    def detect_violations(self, df: pd.DataFrame, threshold: float = 35.0, col: str = "pm25") -> pd.DataFrame:
        """
        Detects rows where pollutant exceeds threshold.
        Default PM2.5 > 35 µg/m³ (WHO/EPA standard-ish).
        """
        if col not in df.columns:
            return pd.DataFrame()
        
        violations = df[df[col] > threshold].copy()
        violations['violation_magnitude'] = violations[col] - threshold
        return violations

    def get_heatmap_matrix(self, df: pd.DataFrame, station_col='locationId', metric='pm25') -> pd.DataFrame:
        """
        Prepares matrix for heatmap: Index=Station, Columns=Date(Day/Hour), Values=Metric.
        This is for the "High-Density Temporal Analysis".
        We might aggregate to Daily avg for a full year view to reduce columns (365 columns).
        Or Hourly if zoomed in.
        For "Entire Year", Daily is best for 100 stations x 365 days = 36,500 cells (very readable).
        """
        # Aggregate to daily
        daily = df.groupby([station_col, pd.Grouper(key='date', freq='D')])[metric].mean().reset_index()
        
        matrix = daily.pivot(index=station_col, columns='date', values=metric)
        return matrix

    def analyze_periodicity(self, df: pd.DataFrame, station_id: int = None) -> Dict:
        """
        Analyzes daily/monthly patterns.
        """
        if station_id:
            df = df[df['locationId'] == station_id]
            
        # Daily Pattern (0-23 hour)
        daily_pattern = df.groupby(df['date'].dt.hour)[['pm25', 'no2']].mean()
        
        # Monthly Pattern (1-12 month)
        monthly_pattern = df.groupby(df['date'].dt.month)[['pm25', 'no2']].mean()
        
        return {
            "daily": daily_pattern,
            "monthly": monthly_pattern
        }

if __name__ == "__main__":
    analyzer = TemporalAnalyzer()
    df = analyzer.load_data()
    violations = analyzer.detect_violations(df)
    print(f"Violations found: {len(violations)}")
