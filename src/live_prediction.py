import pandas as pd
import joblib

station_df = pd.read_csv("data/processed/station_live_aqi.csv")
live_raw = pd.read_csv("data/live/delhi_live_aqi.csv")

models = joblib.load("models/multiday_aqi_models.pkl")
feature_medians = joblib.load("models/feature_medians.pkl")

features = ["PM2.5", "PM10", "NO", "NO2", "NOx", "CO", "SO2", "O3"]

parameter_map = {
    "pm25": "PM2.5",
    "pm10": "PM10",
    "no": "NO",
    "no2": "NO2",
    "nox": "NOx",
    "co": "CO",
    "so2": "SO2",
    "o3": "O3",
}

live_raw["mapped_parameter"] = live_raw["parameter"].map(parameter_map)
live_raw = live_raw.dropna(subset=["mapped_parameter"])

pivot = live_raw.pivot_table(
    index="station",
    columns="mapped_parameter",
    values="value",
    aggfunc="mean"
).reset_index()

df = station_df.merge(pivot, on="station", how="left")

for col in features:
    if col not in df.columns:
        df[col] = feature_medians[col]
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df[col] = df[col].fillna(feature_medians[col])

X = df[features]

for day in range(1, 5):
    df[f"predicted_AQI_day_{day}"] = models[f"day_{day}"].predict(X).round(2)

df["predicted_AQI_tomorrow"] = df["predicted_AQI_day_1"]
df["AQI_change"] = (df["predicted_AQI_tomorrow"] - df["AQI"]).round(2)

df["forecast_trend"] = df["AQI_change"].apply(
    lambda x: "Increasing" if x > 10 else ("Decreasing" if x < -10 else "Stable")
)

df.to_csv("data/processed/station_predictions.csv", index=False)

print(df[[
    "station", "AQI",
    "predicted_AQI_day_1",
    "predicted_AQI_day_2",
    "predicted_AQI_day_3",
    "predicted_AQI_day_4",
    "forecast_trend"
]].head(10))

print("\n4-day live predictions saved.")