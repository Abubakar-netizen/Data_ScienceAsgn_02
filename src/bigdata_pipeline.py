import dask.dataframe as dd
import pandas as pd
from pathlib import Path
import shutil
from .config import RAW_DATA_DIR, PROCESSED_DATA_DIR, TARGET_PARAMETERS
from .preprocess import clean_dataframe
from .utils import setup_logger

logger = setup_logger("bigdata_pipeline")

class BigDataPipeline:
    def __init__(self):
        self.raw_path = RAW_DATA_DIR
        self.processed_path = PROCESSED_DATA_DIR

    def run(self):
        """
        Executes the pipeline: Read Parquet -> Clean/Pivot -> Save Processed.
        """
        logger.info("Starting Big Data Pipeline...")
        
        # Check if raw data exists
        files = list(self.raw_path.glob("*.parquet"))
        if not files:
            logger.error("No raw data found. Run data_fetch.py first.")
            return

        logger.info(f"Found {len(files)} raw files. Processing with Dask...")
        
        # Read all parquet files lazily
        # Dask handles reading multiple files
        try:
            ddf = dd.read_parquet(self.raw_path / "*.parquet", engine="pyarrow")
        except Exception as e:
            logger.error(f"Failed to read parquet files: {e}")
            return

        # Map partitions to clean/pivot function
        # Since 'pivot' changes shape significantly and Dask pivot is expensive/hard,
        # and our files are likely "one station per file", we can use map_partitions
        # efficiently if we assume each partition roughly maps to a station or chunk of rows.
        # However, pivots require knowing all columns. Preprocess ensures columns exist.
        
        # Current data is LONG format: locationId, parameter, value, date...
        # We need WIDE format.
        
        # Optimziation: We can process each file independently and save it back out,
        # rather than loading a massive Dask df and shuffling.
        # But 'Big Data' assignment implies using Dask.
        
        # Let's try map_partitions.
        # We need to provide meta because structure changes.
        meta_dict = {
            'locationId': 'int64',
            'city': 'object',
            'date': 'datetime64[ns]',
            'zone': 'object',
            'pop_density': 'int64'
        }
        for col in TARGET_PARAMETERS:
            meta_dict[col] = 'float64'
            
        cleaned_ddf = ddf.map_partitions(clean_dataframe, meta=meta_dict)
        
        # Fill NA - Dask fillna
        # We want to fill NA *within* station groups preferably.
        # Global ffill is hard in Dask cross-partition.
        # We'll assume the local ffill in `clean_dataframe` per chunk/station did most work if chunks=stations.
        # If not, we do a simple fillna(method='ffill') if permissible or fill with mean.
        # For this assignment, simple fill with rolling mean or specific logic is better.
        # Let's just fillna(0) or dropna for PCA safety if strict, but environmental data needs imputation.
        # We'll stick to what `clean_dataframe` does (which should ideally handle it).
        
        # We save the processed data
        # Repartition to have reasonable chunk sizes (e.g. 1 partition per file/station is fine for 100 stations)
        
        clean_out_path = self.processed_path / "cleaned_data.parquet"
        if clean_out_path.exists():
            shutil.rmtree(clean_out_path) # dangerous if not careful
            
        logger.info("Computing and saving processed data...")
        cleaned_ddf.to_parquet(clean_out_path, engine="pyarrow", overwrite=True)
        logger.info(f"Pipeline finished. Data saved to {clean_out_path}")

if __name__ == "__main__":
    pipeline = BigDataPipeline()
    pipeline.run()
