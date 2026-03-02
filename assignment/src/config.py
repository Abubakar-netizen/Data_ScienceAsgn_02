import os
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# OpenAQ API Settings
#bcz old  version is retired thats why we use api key with url
OPENAQ_API_URL = "https://api.openaq.org/v3"
API_KEY = "aac9f7305175cd44dce478668484111a8dcfa2a4fb59f656cecfd81048104516"

# Data Context
TARGET_YEAR = 2025
TARGET_PARAMETERS = ["pm25", "pm10", "no2", "o3", "temperature", "humidity"]
REQUIRED_SENSORS = ["pm25", "pm10", "no2", "o3", "temperature", "humidity"]

# Streamlit Settings
DASHBOARD_TITLE = "Urban Environmental Intelligence"
DASHBOARD_LAYOUT = "wide"
