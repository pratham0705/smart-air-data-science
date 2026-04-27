import os
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor


# Load historical data
df = pd.read_csv("data/air_quality.csv")

# Drop rows where AQI is missing
df = df.dropna(subset=["AQI"])

# Fill pollutant missing values
df = df.ffill()

# Convert date
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# Sort
df = df.sort_values("Date")

# IMPORTANT: Use only Delhi data
df = df[df["City"] == "Delhi"].copy()
df = df.reset_index(drop=True)

# Create next-day target
df["AQI_Next"] = df["AQI"].shift(-1)

# Drop last null target
df = df.dropna(subset=["AQI_Next"])

# Features from your notebook
features = ["PM2.5", "PM10", "NO", "NO2", "NOx", "CO", "SO2", "O3"]

# Drop rows with missing feature values
df = df.dropna(subset=features)

X = df[features]
y = df["AQI_Next"]

# Time-series split: past train, future test
split_index = int(len(X) * 0.8)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]


# Random Forest
rf = RandomForestRegressor(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

rf_pred = rf.predict(X_test)
rf_r2 = r2_score(y_test, rf_pred)
rf_mae = mean_absolute_error(y_test, rf_pred)
rf_rmse = mean_squared_error(y_test, rf_pred) ** 0.5


# XGBoost
xgb = XGBRegressor(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=4,
    random_state=42
)

xgb.fit(X_train, y_train)

xgb_pred = xgb.predict(X_test)
xgb_r2 = r2_score(y_test, xgb_pred)
xgb_mae = mean_absolute_error(y_test, xgb_pred)
xgb_rmse = mean_squared_error(y_test, xgb_pred) ** 0.5


print("\nRandom Forest Results")
print("R²:", rf_r2)
print("MAE:", rf_mae)
print("RMSE:", rf_rmse)

print("\nXGBoost Results")
print("R²:", xgb_r2)
print("MAE:", xgb_mae)
print("RMSE:", xgb_rmse)


# Save best model
os.makedirs("models", exist_ok=True)

if rf_r2 >= xgb_r2:
    joblib.dump(rf, "models/aqi_model.pkl")
    print("\nBest Model: Random Forest")
    best_model = rf
else:
    joblib.dump(xgb, "models/aqi_model.pkl")
    print("\nBest Model: XGBoost")
    best_model = xgb

print("Model saved successfully.")


# Get feature importance
importance = best_model.feature_importances_

features = ["PM2.5", "PM10", "NO", "NO2", "NOx", "CO", "SO2", "O3"]

importance_df = pd.DataFrame({
    "Feature": features,
    "Importance": importance
}).sort_values(by="Importance", ascending=False)

# Save it
importance_df.to_csv("data/processed/feature_importance.csv", index=False)

print("\nFeature Importance:")
print(importance_df)