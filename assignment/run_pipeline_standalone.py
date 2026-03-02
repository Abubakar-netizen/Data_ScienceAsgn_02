from assignment.src.bigdata_pipeline import BigDataPipeline
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pipeline = BigDataPipeline()
    pipeline.run()
