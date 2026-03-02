import requests
import json

base_url = "https://api.openaq.org/v2"
try:
    print(f"Probing {base_url}/measurements...")
    r = requests.get(f"{base_url}/measurements", params={"limit": 1})
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print("V2 Measurements SUCCESS!")
        print(json.dumps(r.json(), indent=2))
    else:
        print(f"V2 Measurements FAILED: {r.text}")
except Exception as e:
    print(f"Error: {e}")

try:
    print(f"\nProbing {base_url}/locations...")
    r = requests.get(f"{base_url}/locations", params={"limit": 1})
    print(f"Status: {r.status_code}")
except Exception as e:
    print(f"Error: {e}")
