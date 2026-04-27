import os
import pandas as pd
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "air_quality.csv")

features = ['PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 'CO', 'SO2', 'O3']

def get_dynamic_live_data(location="Delhi"):
    df = pd.read_csv(DATA_PATH)

    df = df[df["City"] == location]
    df = df.dropna(subset=["AQI"])
    df = df.ffill()

    # Use last 100 rows (recent behavior)
    recent_df = df.tail(100)

    # pick random realistic row
    live_row = recent_df.sample(1)

    live_values = live_row[features].iloc[0].to_dict()

    # Add small variation (simulate real-time change)
    for key in live_values:
        variation = random.uniform(-3, 3)
        live_values[key] = round(live_values[key] + variation, 2)

    return {
        "status": "success",
        "source": "Dynamic Realistic Simulation",
        "location": location,
        "data": live_values
    }


if __name__ == "__main__":
    print(get_dynamic_live_data("Delhi"))