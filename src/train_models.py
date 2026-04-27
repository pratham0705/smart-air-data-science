import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import joblib

# Load data
df = pd.read_csv("/Users/pratham07/Desktop/data analysis projects/smart air/data/air_quality.csv")

# Filter Delhi
df = df[df['City'] == 'Delhi']

# Handle missing values
df = df.dropna(subset=['AQI'])
df = df.ffill()

# Create target
df['AQI_next'] = df['AQI'].shift(-1)
df = df.dropna()

# Features
features = ['PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 'CO', 'SO2', 'O3']

X = df[features]
y = df['AQI_next']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -------------------------------
# RANDOM FOREST
# -------------------------------
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

rf_pred = rf_model.predict(X_test)

# -------------------------------
# XGBOOST
# -------------------------------
xgb_model = XGBRegressor(n_estimators=100, learning_rate=0.1)
xgb_model.fit(X_train, y_train)

xgb_pred = xgb_model.predict(X_test)

# -------------------------------
# EVALUATION FUNCTION
# -------------------------------
def evaluate(y_true, y_pred, model_name):
    print(f"\n🔹 {model_name} Performance:")
    print("MAE:", mean_absolute_error(y_true, y_pred))
    print("RMSE:", np.sqrt(mean_squared_error(y_true, y_pred)))
    print("R2 Score:", r2_score(y_true, y_pred))

# Evaluate models
evaluate(y_test, rf_pred, "Random Forest")
evaluate(y_test, xgb_pred, "XGBoost")

# Save models
joblib.dump(rf_model, "models/random_forest.pkl")
joblib.dump(xgb_model, "models/xgboost.pkl")

print("\n✅ Models saved successfully!")