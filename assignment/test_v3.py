import requests
import json
import time

API_KEY = "aac9f7305175cd44dce478668484111a8dcfa2a4fb59f656cecfd81048104516"
base_url = "https://api.openaq.org/v3"
headers = {"X-API-Key": API_KEY}

def probe():
    print("Searching for candidate locations (ID asc)...")
    r = requests.get(f"{base_url}/locations", params={"limit": 50, "order_by": "id", "sort_order": "asc", "has_sensors": "true"}, headers=headers)
    locations = r.json().get("results", [])
    
    working_stations = []
    for loc in locations:
        loc_id = loc['id']
        sensors = [s for s in loc.get("sensors", []) if s.get("parameter", {}).get("name") == "pm25"]
        if not sensors: continue
        
        sensor_id = sensors[0]['id']
        print(f"Checking Station {loc_id}, Sensor {sensor_id} (PM2.5)...")
        
        # Try a specific 2025 range
        url = f"{base_url}/sensors/{sensor_id}/hours"
        params = {
            "datetime_from": "2025-06-01T00:00:00Z",
            "datetime_to": "2025-06-07T23:59:59Z",
            "limit": 1
        }
        try:
            res = requests.get(url, params=params, headers=headers, timeout=10)
            found = res.json().get("meta", {}).get("found", "0")
            print(f"  Found: {found}")
            if str(found) != "0":
                working_stations.append(loc_id)
        except:
            print("  Timeout")
            
        if len(working_stations) >= 5:
            break
        time.sleep(1) # Rate limit safety

    print(f"\nWorking stations found: {working_stations}")

if __name__ == "__main__":
    probe()
