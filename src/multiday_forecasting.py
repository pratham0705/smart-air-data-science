import os
import joblib
import pandas as pd
from xgboost import XGBRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

df = pd.read_csv("data/air_quality.csv")

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date", "AQI"])
df = df[df["City"] == "Delhi"].copy()
df = df.sort_values("Date").reset_index(drop=True)

features = ["PM2.5", "PM10", "NO", "NO2", "NOx", "CO", "SO2", "O3"]

df = df.ffill()
df = df.dropna(subset=features + ["AQI"])

models = {}
results = []

for day in range(1, 5):
    target_col = f"AQI_Day_{day}"
    df[target_col] = df["AQI"].shift(-day)

    temp_df = df.dropna(subset=[target_col]).copy()

    X = temp_df[features]
    y = temp_df[target_col]

    split_index = int(len(X) * 0.8)

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    model = XGBRegressor(
        n_estimators=250,
        learning_rate=0.05,
        max_depth=4,
        random_state=42
    )

    model.fit(X_train, y_train)

    pred = model.predict(X_test)

    r2 = r2_score(y_test, pred)
    mae = mean_absolute_error(y_test, pred)
    rmse = mean_squared_error(y_test, pred) ** 0.5

    models[f"day_{day}"] = model

    results.append({
        "Forecast Horizon": f"Day {day}",
        "R2": round(r2, 4),
        "MAE": round(mae, 2),
        "RMSE": round(rmse, 2)
    })

os.makedirs("models", exist_ok=True)

joblib.dump(models, "models/multiday_aqi_models.pkl")
joblib.dump(df[features].median(), "models/feature_medians.pkl")

results_df = pd.DataFrame(results)
results_df.to_csv("data/processed/multiday_model_results.csv", index=False)

print(results_df)
print("\n4-day forecast models saved successfully.")