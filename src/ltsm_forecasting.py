import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import joblib

df = pd.read_csv("data/air_quality.csv")

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date", "AQI"])
df = df[df["City"] == "Delhi"].copy()
df = df.sort_values("Date").reset_index(drop=True)

features = ["PM2.5", "PM10", "NO", "NO2", "NOx", "CO", "SO2", "O3", "AQI"]

df = df[features].ffill().dropna()

scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(df)

sequence_length = 10

X = []
y = []

for i in range(sequence_length, len(scaled_data)):
    X.append(scaled_data[i-sequence_length:i, :])
    y.append(scaled_data[i, features.index("AQI")])

X = np.array(X)
y = np.array(y)

split_index = int(len(X) * 0.8)

X_train, X_test = X[:split_index], X[split_index:]
y_train, y_test = y[:split_index], y[split_index:]

model = Sequential()
model.add(LSTM(64, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
model.add(Dropout(0.2))
model.add(LSTM(32))
model.add(Dropout(0.2))
model.add(Dense(1))

model.compile(optimizer="adam", loss="mse")

history = model.fit(
    X_train,
    y_train,
    epochs=30,
    batch_size=16,
    validation_data=(X_test, y_test),
    verbose=1
)

pred_scaled = model.predict(X_test)

# inverse transform only AQI
dummy_pred = np.zeros((len(pred_scaled), len(features)))
dummy_actual = np.zeros((len(y_test), len(features)))

dummy_pred[:, features.index("AQI")] = pred_scaled.flatten()
dummy_actual[:, features.index("AQI")] = y_test

pred = scaler.inverse_transform(dummy_pred)[:, features.index("AQI")]
actual = scaler.inverse_transform(dummy_actual)[:, features.index("AQI")]

r2 = r2_score(actual, pred)
mae = mean_absolute_error(actual, pred)
rmse = mean_squared_error(actual, pred) ** 0.5

print("\nLSTM Results")
print("R²:", r2)
print("MAE:", mae)
print("RMSE:", rmse)

os.makedirs("models", exist_ok=True)

model.save("models/lstm_aqi_model.keras")
joblib.dump(scaler, "models/lstm_scaler.pkl")

print("\nLSTM model saved successfully.")