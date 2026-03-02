import requests
import pandas as pd
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import random
from .config import (
    OPENAQ_API_URL, 
    RAW_DATA_DIR, 
    TARGET_YEAR, 
    REQUIRED_SENSORS, 
    TARGET_PARAMETERS,
    API_KEY
)
from .utils import setup_logger

logger = setup_logger("data_fetch")

class OpenAQFetcher:
    def __init__(self):
        self.headers = {"X-API-Key": API_KEY} if API_KEY else {}
        self.base_url = OPENAQ_API_URL

    def get_stations(self, limit: int = 100) -> List[Dict]:
        """
        Fetch a list of stations using OpenAQ v3.
        """
        logger.info(f"Searching for v3 stations with PM2.5...")
        
        params = {
            "limit": 1000,
            "order_by": "id",
            "sort_order": "asc",
            "has_sensors": "true"
        }
        
        try:
            url = f"{self.base_url}/locations"
            logger.info(f"Requesting {url} with params {params}")
            response = requests.get(url, params=params, headers=self.headers, timeout=15)
            response.raise_for_status()
            locations = response.json().get("results", [])
            logger.info(f"API returned {len(locations)} locations.")
            
            valid_stations = []
            for loc in locations:
                # v3 uses 'sensors' list in location instead of 'parameters'
                sensor_map = {s["id"]: s["parameter"]["name"] for s in loc.get("sensors", []) if s.get("parameter", {}).get("name") in TARGET_PARAMETERS}
                
                # Check for 2025 activity in v3
                f_obj = loc.get("datetimeFirst")
                l_obj = loc.get("datetimeLast")
                first_utc = f_obj.get("utc") if isinstance(f_obj, dict) else f_obj
                last_utc = l_obj.get("utc") if isinstance(l_obj, dict) else l_obj
                
                # REPRODUCIBILITY: Target stations that actually have data spanning 2025
                if sensor_map and first_utc and last_utc and first_utc < "2025-01-01" and last_utc >= "2025-06-01":
                    valid_stations.append({
                        "id": loc["id"],
                        "city": loc.get("name", "Unknown"),
                        "sensor_map": sensor_map
                    })
                else:
                    if len(valid_stations) < 3:
                        logger.debug(f"Rejected {loc['id']} (Reason: first={first_utc}, last={last_utc}, sensors={bool(sensor_map)})")
                
                if len(valid_stations) >= limit:
                    break
            
            logger.info(f"Found {len(valid_stations)} valid stations.")
            return valid_stations

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching stations: {e}")
            return []

    def fetch_measurements(self, location_id: int, start_date: str, end_date: str, sensor_map: Dict[int, str], city: str) -> pd.DataFrame:
        """
        Fetch aggregated hourly data for all sensors of a location using OpenAQ v3.
        """
        all_measurements = []
        
        for sensor_id, param_name in sensor_map.items():
            url = f"{self.base_url}/sensors/{sensor_id}/hours"
            page = 1
            limit = 1000
            
            params = {
                "datetime_from": start_date,
                "datetime_to": end_date,
                "limit": limit
            }
            
            try:
                while True:
                    params["page"] = page
                    time.sleep(0.5)
                    
                    resp = requests.get(url, params=params, headers=self.headers, timeout=15)
                    logger.debug(f"Fetch {location_id} sensor {sensor_id} page {page} status: {resp.status_code}")
                    
                    if resp.status_code == 429:
                        logger.warning("Rate limit. Waiting 10s...")
                        time.sleep(10)
                        continue
                    
                    if resp.status_code != 200:
                        logger.warning(f"Fetch {location_id} sensor {sensor_id} failed with status {resp.status_code}: {resp.text[:200]}")
                        break
                    
                    meta = resp.json().get("meta", {})
                    found_str = str(meta.get("found", "0"))
                    results = resp.json().get("results", [])
                    
                    if not results:
                        break
                        
                    # Harmonize v3 hourly data to v2-like flat format
                    for r in results:
                        flat_r = {
                            "locationId": location_id,
                            "city": city,
                            "parameter": param_name,
                            "value": r.get("value"),
                            "date": r.get("period", {}).get("datetimeFrom", {}).get("utc"), 
                            "unit": "" # v3 hourly results might not have units in result
                        }
                        all_measurements.append(flat_r)
                    
                    # Handle strings like ">1000" in found
                    if ">" in found_str:
                        has_more = True
                    else:
                        try:
                            has_more = int(found_str) > page * limit
                        except ValueError: # Catch ValueError for non-integer found_str
                            has_more = False
                    
                    if not has_more or page >= 5: 
                        break
                    page += 1

            except Exception as e:
                logger.error(f"Error fetching measurements for {location_id} sensor {sensor_id}: {e}")

        return pd.DataFrame(all_measurements)

    def run_pipeline(self):
        stations = self.get_stations(limit=100)
        
        # Real 2025 dates - adding Z for ISO format if needed by OpenAQ v3
        start_date = "2025-01-01T00:00:00Z"
        end_date = "2025-12-31T23:59:59Z"

        if not stations:
            logger.error("No stations found. Check your Internet/API Key.")
            return

        for i, station in enumerate(stations):
            loc_id = station["id"]
            sensor_map = station["sensor_map"]
            city = station.get("city", "Unknown")
            
            logger.info(f"[{i+1}/100] Fetching 2025 data for {city} (ID: {loc_id}, {len(sensor_map)} sensors)...")
            
            df = self.fetch_measurements(loc_id, start_date, end_date, sensor_map, city)
            
            if not df.empty:
                save_path = RAW_DATA_DIR / f"station_{loc_id}.parquet"
                df.to_parquet(save_path, index=False)
                logger.info(f"Saved {len(df)} records.")
            else:
                logger.warning(f"No 2025 data returned for station {loc_id}")

    def generate_mock_data(self):
        """
        Enhanced mock data for 2025 with zoning and population density.
        """
        logger.info("Generating HIGH VOLUME mock data for 2025 (Zoning Enabled)...")
        import numpy as np
        
        station_ids = range(101, 201)
        dates = pd.date_range(start="2025-01-01", end="2025-12-31", freq="h")
        
        for sid in station_ids:
            # Assign Zone and Population Density
            zone = "Industrial" if sid % 3 == 0 else "Residential"
            pop_density = np.random.randint(5000, 30000) if zone == "Industrial" else np.random.randint(1000, 8000)
            
            n_rows = len(dates)
            t = np.linspace(0, 4*np.pi, n_rows)
            daily = np.sin(np.linspace(0, 365*24*np.pi/12, n_rows))
            
            # Bias based on zone
            multi = 2.5 if zone == "Industrial" else 1.0
            pm25 = (np.random.lognormal(2, 0.5, n_rows) + 5 * (daily + 1)) * multi
            
            vals = {
                "pm25": pm25,
                "pm10": pm25 * 1.5 + np.random.normal(0, 5, n_rows),
                "no2": (np.random.lognormal(1.5, 0.4, n_rows) + 10 * (daily + 1)) * multi,
                "o3": np.maximum(0, 40 + 20 * np.sin(t) - 10 * daily + np.random.normal(0, 5, n_rows)),
                "temperature": 15 + 10 * np.sin(t) + 5 * daily + np.random.normal(0, 2, n_rows),
                "humidity": np.clip(60 - 10 * np.sin(t) + np.random.normal(0, 5, n_rows), 0, 100)
            }
            
            frames = []
            for sens in vals:
                temp_df = pd.DataFrame({
                    "locationId": sid,
                    "city": f"{zone}_City_{sid}",
                    "zone": zone,
                    "pop_density": pop_density,
                    "parameter": sens,
                    "value": vals[sens],
                    "date": dates,
                    "unit": "val"
                })
                frames.append(temp_df)
            
            pd.concat(frames).to_parquet(RAW_DATA_DIR / f"station_{sid}.parquet", index=False)

if __name__ == "__main__":
    fetcher = OpenAQFetcher()
    # Direct call to run_pipeline for real data as requested
    fetcher.run_pipeline()
