import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import joblib
from pathlib import Path
from typing import Tuple, Dict
import plotly.express as px
from .config import PROCESSED_DATA_DIR, TARGET_PARAMETERS, LOGS_DIR
from .utils import setup_logger

logger = setup_logger("pca_analysis")

class PCAAnalyzer:
    def __init__(self, n_components: int = 2):
        self.n_components = n_components
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=n_components)
        self.kmeans = KMeans(n_clusters=3, random_state=42) # Industrial, Residential, Mixed?
        self.data_path = PROCESSED_DATA_DIR / "cleaned_data.parquet"

    def load_data(self) -> pd.DataFrame:
        if not self.data_path.exists():
            # Fallback to recursively finding parquet files if directory is partitioned
            pass 
        # Read using pandas is fine for < 10M rows for analysis 
        # (100 stations * 8760 = 876k rows)
        try:
            return pd.read_parquet(self.data_path)
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return pd.DataFrame()

    def run_analysis(self, df: pd.DataFrame = None) -> Tuple[pd.DataFrame, pd.DataFrame, Dict]:
        """
        Runs Standardization -> PCA -> Clustering.
        Returns:
            - df_pca: DataFrame with PC1, PC2, Cluster, and original metadata
            - loadings: DataFrame of component loadings
            - report: Dictionary with explained variance, etc.
        """
        if df is None:
            df = self.load_data()
            
        if df.empty:
            logger.warning("Empty dataframe provided for PCA.")
            return df, pd.DataFrame(), {}
            
        # Filter for rows with no NaNs in target cols
        df_clean = df.dropna(subset=TARGET_PARAMETERS).copy()
        
        if df_clean.empty:
            logger.warning("No data remains after dropping NaNs for PCA.")
            return pd.DataFrame(), pd.DataFrame(), {}
        
        # Standardize
        X = df_clean[TARGET_PARAMETERS].values
        X_scaled = self.scaler.fit_transform(X)
        
        # PCA
        components = self.pca.fit_transform(X_scaled)
        
        # Loadings
        loadings = pd.DataFrame(
            self.pca.components_.T, 
            columns=[f'PC{i+1}' for i in range(self.n_components)],
            index=TARGET_PARAMETERS
        )
        
        # Clustering on Reduced Data (or original? Prompt implies clustering zones)
        # Using PC scores for clustering is standard for identifying patterns in the reduced space
        clusters = self.kmeans.fit_predict(components)
        
        # Add results to DF
        df_clean['PC1'] = components[:, 0]
        df_clean['PC2'] = components[:, 1]
        df_clean['Cluster'] = clusters
        
        # Labels for clusters (heuristic based on pollutant levels?)
        # We can map cluster centers to qualitative labels later in dashboard
        
        explained_variance = self.pca.explained_variance_ratio_
        report = {
            "explained_variance": explained_variance,
            "total_variance": sum(explained_variance)
        }
        
        logger.info(f"PCA Completed. Explained Variance: {explained_variance}")
        
        return df_clean, loadings, report

if __name__ == "__main__":
    analyzer = PCAAnalyzer()
    df, loadings, report = analyzer.run_analysis()
    # verify
    print(loadings)
