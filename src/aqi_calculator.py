import os
import pandas as pd

from advisory import generate_advisory
from hotspot_detection import detect_hotspot, hotspot_priority


BREAKPOINTS = {
    "pm25": [
        (0, 30, 0, 50),
        (31, 60, 51, 100),
        (61, 90, 101, 200),
        (91, 120, 201, 300),
        (121, 250, 301, 400),
        (251, 500, 401, 500),
    ],
    "pm10": [
        (0, 50, 0, 50),
        (51, 100, 51, 100),
        (101, 250, 101, 200),
        (251, 350, 201, 300),
        (351, 430, 301, 400),
        (431, 600, 401, 500),
    ],
    "no2": [
        (0, 40, 0, 50),
        (41, 80, 51, 100),
        (81, 180, 101, 200),
        (181, 280, 201, 300),
        (281, 400, 301, 400),
        (401, 1000, 401, 500),
    ],
    "so2": [
        (0, 40, 0, 50),
        (41, 80, 51, 100),
        (81, 380, 101, 200),
        (381, 800, 201, 300),
        (801, 1600, 301, 400),
        (1601, 2000, 401, 500),
    ],
    "co": [
        (0, 1, 0, 50),
        (1.1, 2, 51, 100),
        (2.1, 10, 101, 200),
        (10.1, 17, 201, 300),
        (17.1, 34, 301, 400),
        (34.1, 50, 401, 500),
    ],
    "o3": [
        (0, 50, 0, 50),
        (51, 100, 51, 100),
        (101, 168, 101, 200),
        (169, 208, 201, 300),
        (209, 748, 301, 400),
        (749, 1000, 401, 500),
    ],
}


def calculate_sub_index(value, breakpoints):
    if pd.isna(value):
        return None

    for bp_low, bp_high, aqi_low, aqi_high in breakpoints:
        if bp_low <= value <= bp_high:
            return round(
                ((aqi_high - aqi_low) / (bp_high - bp_low))
                * (value - bp_low)
                + aqi_low,
                2,
            )

    return None


def get_aqi_category(aqi):
    if pd.isna(aqi):
        return "Unknown"
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Satisfactory"
    elif aqi <= 200:
        return "Moderate"
    elif aqi <= 300:
        return "Poor"
    elif aqi <= 400:
        return "Very Poor"
    else:
        return "Severe"


def filter_latest_data(df, hours=48):
    df = df.copy()

    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    df = df.dropna(subset=["datetime"])

    cutoff_time = pd.Timestamp.now(tz="Asia/Kolkata") - pd.Timedelta(hours=hours)

    df = df[df["datetime"] >= cutoff_time]

    df = df.sort_values("datetime", ascending=False)

    # Keep latest record per station + pollutant
    df = df.drop_duplicates(subset=["station", "parameter"], keep="first")

    return df


def get_data_status(dt):
    now = pd.Timestamp.now(tz="Asia/Kolkata")
    age_hours = (now - dt).total_seconds() / 3600

    if age_hours <= 12:
        return "Fresh"
    elif age_hours <= 48:
        return "Delayed"
    else:
        return "Old"

def calculate_confidence(row):
    score = 0

    pollutant_count = row.get("available_pollutants_count", 0)

    # Pollutant coverage score
    if pollutant_count >= 5:
        score += 50
    elif pollutant_count >= 3:
        score += 35
    elif pollutant_count >= 1:
        score += 20

    # Data freshness score
    if row["data_status"] == "Fresh":
        score += 30
    elif row["data_status"] == "Delayed":
        score += 15

    # AQI validity score
    if pd.notna(row["AQI"]):
        score += 20

    if score >= 80:
        level = "High"
    elif score >= 55:
        level = "Medium"
    else:
        level = "Low"

    return score, level

def get_grap_stage(aqi):
    if pd.isna(aqi):
        return "Unknown", "Insufficient AQI data"

    if aqi <= 200:
        return "No GRAP Stage", "AQI below GRAP trigger level"
    elif aqi <= 300:
        return "Stage I - Poor", "AQI Poor: basic pollution control measures advised"
    elif aqi <= 400:
        return "Stage II - Very Poor", "AQI Very Poor: stronger restrictions and public advisory required"
    elif aqi <= 450:
        return "Stage III - Severe", "AQI Severe: avoid outdoor activity and reduce traffic exposure"
    else:
        return "Stage IV - Severe+", "AQI Severe+: emergency-level restrictions and avoid outdoor exposure"

def calculate_station_aqi(df):
    df = df.copy()

    # Keep only latest valid data
    df = filter_latest_data(df, hours=48)

    # Keep only AQI pollutants
    df = df[df["parameter"].isin(BREAKPOINTS.keys())].copy()

    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    df["sub_index"] = df.apply(
        lambda row: calculate_sub_index(
            row["value"],
            BREAKPOINTS[row["parameter"]],
        ),
        axis=1,
    )

    df = df.dropna(subset=["sub_index"])
    pollutant_counts = (
    df.groupby("station")["parameter"]
    .nunique()
    .reset_index()
    .rename(columns={"parameter": "available_pollutants_count"})
)

    # Pick worst pollutant per station
    station_aqi = (
        df.sort_values("sub_index", ascending=False)
        .groupby("station", as_index=False)
        .first()
    )

    station_aqi = station_aqi.merge(
    pollutant_counts,
    on="station",
    how="left"
)

    station_aqi = station_aqi.rename(
        columns={
            "parameter": "dominant_pollutant",
            "value": "dominant_value",
            "sub_index": "AQI",
        }
    )

    station_aqi["AQI_Category"] = station_aqi["AQI"].apply(get_aqi_category)

    station_aqi[["GRAP_Stage", "GRAP_Advisory"]] = station_aqi["AQI"].apply(
    lambda x: pd.Series(get_grap_stage(x))
)

    station_aqi["data_status"] = station_aqi["datetime"].apply(get_data_status)

    # Advisory
    station_aqi["advisory"] = station_aqi.apply(
        lambda row: generate_advisory(
            row["AQI"],
            row["AQI_Category"],
            row["dominant_pollutant"],
        ),
        axis=1,
    )

    station_aqi["outdoor_decision"] = station_aqi["advisory"].apply(
        lambda x: x["outdoor_decision"]
    )
    station_aqi["health_advisory"] = station_aqi["advisory"].apply(
        lambda x: x["health_advisory"]
    )
    station_aqi["precautions"] = station_aqi["advisory"].apply(
        lambda x: x["precautions"]
    )
    station_aqi["travel_advisory"] = station_aqi["advisory"].apply(
        lambda x: x["travel_advisory"]
    )

    # Hotspot detection
    station_aqi["hotspot_status"] = station_aqi.apply(
        lambda row: detect_hotspot(row["AQI"], row["AQI_Category"]),
        axis=1,
    )

    station_aqi["hotspot_priority"] = station_aqi["AQI"].apply(hotspot_priority)

    station_aqi[["confidence_score", "confidence_level"]] = station_aqi.apply(
    lambda row: pd.Series(calculate_confidence(row)),
    axis=1
)

    final_cols = [
        "station",
        "latitude",
        "longitude",
        "dominant_pollutant",
        "dominant_value",
        "AQI",
        "AQI_Category",
        "datetime",
        "data_status",
        "hotspot_status",
        "hotspot_priority",
        "outdoor_decision",
        "health_advisory",
        "precautions",
        "travel_advisory",
        "available_pollutants_count",
        "confidence_score",
        "confidence_level",
        "GRAP_Stage",
        "GRAP_Advisory",
    ]

    return station_aqi[final_cols]


if __name__ == "__main__":
    input_path = "data/live/delhi_live_aqi.csv"
    output_path = "data/processed/station_live_aqi.csv"

    df = pd.read_csv(input_path)

    station_aqi = calculate_station_aqi(df)

    os.makedirs("data/processed", exist_ok=True)
    station_aqi.to_csv(output_path, index=False)

    print(f"\nSaved to {output_path}")