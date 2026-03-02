import requests
import json

base_url = "https://api.openaq.org/v3"
# Try locations
try:
    r = requests.get(f"{base_url}/locations", params={"limit": 1})
    print("LOCATIONS VERSION:")
    print(json.dumps(r.json(), indent=2))
except Exception as e:
    print(f"Error locations: {e}")

try:
    # Try measurements with a known recent ID or just any
    r = requests.get(f"{base_url}/measurements", params={"limit": 1})
    print("\nMEASUREMENTS VERSION:")
    print(json.dumps(r.json(), indent=2))
except Exception as e:
    print(f"Error measurements: {e}")
