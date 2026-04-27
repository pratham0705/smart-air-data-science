import os
import requests
import pandas as pd

API_KEY = "68d7a3546adf333b233af33873b8aa59f58096ad5198ce6f06ddba4f058bb40d"
BASE_URL = "https://api.openaq.org/v3"

HEADERS = {"X-API-Key": API_KEY}

# Delhi bounding box: min_lon, min_lat, max_lon, max_lat
DELHI_BBOX = "76.84,28.40,77.35,28.88"


def get_delhi_locations():
    url = f"{BASE_URL}/locations"
    params = {
        "iso": "IN",
        "bbox": DELHI_BBOX,
        "limit": 100
    }

    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code != 200:
        return pd.DataFrame()

    rows = []
    for item in response.json().get("results", []):
        coordinates = item.get("coordinates") or {}

        rows.append({
            "location_id": item.get("id"),
            "station": item.get("name"),
            "latitude": coordinates.get("latitude"),
            "longitude": coordinates.get("longitude"),
            "timezone": item.get("timezone")
        })

    return pd.DataFrame(rows)


def get_sensors_for_location(location_id):
    url = f"{BASE_URL}/locations/{location_id}/sensors"

    response = requests.get(url, headers=HEADERS, params={"limit": 100})

    if response.status_code != 200:
        return []

    records = []

    print(f"\nLocation ID: {location_id}")
    for sensor in response.json().get("results", []):
        print(sensor.get("parameter"))

    for sensor in response.json().get("results", []):
        parameter = sensor.get("parameter") or {}
        latest = sensor.get("latest") or {}
        datetime_obj = latest.get("datetime") or {}

        if latest.get("value") is None:
            continue

        records.append({
            "location_id": location_id,
            "sensor_id": sensor.get("id"),
            "parameter": parameter.get("name"),
            "display_name": parameter.get("displayName"),
            "unit": parameter.get("units"),
            "value": latest.get("value"),
            "datetime": datetime_obj.get("local"),
        })

    return records


def fetch_delhi_live_data():
    locations_df = get_delhi_locations()

    if locations_df.empty:
        print("No Delhi locations found.")
        return pd.DataFrame()

    print("Delhi locations found:", len(locations_df))

    all_records = []

    for _, row in locations_df.iterrows():
        sensor_records = get_sensors_for_location(row["location_id"])

        for record in sensor_records:
            record["station"] = row["station"]
            record["latitude"] = row["latitude"]
            record["longitude"] = row["longitude"]
            all_records.append(record)

    return pd.DataFrame(all_records)


if __name__ == "__main__":
    df = fetch_delhi_live_data()

    if not df.empty:
        os.makedirs("data/live", exist_ok=True)
        df.to_csv("data/live/delhi_live_aqi.csv", index=False)

        print("\nLive data saved successfully.")
    else:
        print("No live data saved.")