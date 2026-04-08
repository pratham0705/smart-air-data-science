import streamlit as st
import pandas as pd
import numpy as np

# ML Model
from sklearn.ensemble import RandomForestRegressor

# LSTM (Deep Learning)
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# Scaling
from sklearn.preprocessing import MinMaxScaler

# Load dataset
df = pd.read_csv("air_quality.csv")

# Filter Delhi
df = df[df['City'] == 'Delhi']

# Handle missing values
df = df.dropna(subset=['AQI'])
df.fillna(method='ffill', inplace=True)

# Create target
df['AQI_next'] = df['AQI'].shift(-1)
df.dropna(inplace=True)

features = ['PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 'CO', 'SO2', 'O3']

# Random Forest
X = df[features]
y = df['AQI_next']

# LTSM 

# Scaling
scaler = MinMaxScaler()
data = df[['AQI']].values
data_scaled = scaler.fit_transform(data)

# Create sequences
X_lstm, y_lstm = [], []

for i in range(10, len(data_scaled)):
    X_lstm.append(data_scaled[i-10:i])
    y_lstm.append(data_scaled[i])

X_lstm = np.array(X_lstm)
y_lstm = np.array(y_lstm)

# random forest
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X, y)

# LTSM
lstm_model = Sequential()

lstm_model.add(LSTM(50, return_sequences=False, input_shape=(10,1)))
lstm_model.add(Dense(1))

lstm_model.compile(optimizer='adam', loss='mean_squared_error')

lstm_model.fit(X_lstm, y_lstm, epochs=3, batch_size=32, verbose=0)

# aqi category
def get_aqi_category(aqi):
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

# live data from open ap
import requests

def get_live_aqi():
    url = "https://api.openaq.org/v3/latest?city=Delhi"

    headers = {
        "accept": "application/json"
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    return data

# process live data

def process_live_data():
    data = get_live_aqi()
    
    results = data.get("results", [])
    
    pollution_dict = {}
    
    if results:
        measurements = results[0].get("measurements", [])
        
        for m in measurements:
            pollution_dict[m['parameter']] = m['value']
    
    return pollution_dict

# title
st.title("🌍 Air Quality Prediction System")

# show current data
latest_data = df[features].iloc[-1:]

st.subheader("📊 Current Pollution Data")
st.write(latest_data)

# random forest prediction
rf_prediction = rf_model.predict(latest_data)

# LTSM prediction
last_10_days = data_scaled[-10:]
last_10_days = last_10_days.reshape(1, 10, 1)

lstm_pred = lstm_model.predict(last_10_days)
lstm_pred = scaler.inverse_transform(lstm_pred)

#results
st.subheader("🔮 Predicted AQI for Tomorrow")

live_pollution = process_live_data()

st.subheader("🌍 Current Pollution Data (Live)")
st.write(live_pollution)

rf_val = rf_prediction[0]
lstm_val = lstm_pred[0][0]

st.write(f"🌲 Random Forest: {rf_val:.2f}")
st.write(f"   Category: {get_aqi_category(rf_val)}")

st.write(f"🤖 LSTM: {lstm_val:.2f}")
st.write(f"   Category: {get_aqi_category(lstm_val)}")