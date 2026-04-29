# 🌍 Smart Air – AI-Based AQI Prediction & Advisory System

## 📌 Overview
Smart Air is an AI-powered system that predicts Air Quality Index (AQI) and provides future forecasts, hotspot detection, and health advisories.

It uses Machine Learning (XGBoost, Random Forest) and Deep Learning (LSTM) to deliver accurate and actionable insights.

---

## 🚀 Features
- Real-time AQI calculation  
- 4-day AQI forecasting  
- Hotspot detection (high pollution areas)  
- Health, travel & precaution advisories  
- Feature importance (pollution cause analysis)  
- Interactive dashboard (maps, charts, graphs)  

---

## 🛠️ Tech Stack
- Python  
- Pandas, NumPy  
- Scikit-learn, XGBoost  
- TensorFlow / Keras (LSTM)  
- Streamlit (Dashboard)  
- Plotly & Folium (Visualization)  

---

## ▶️ How to Run

### Step 1: Go to project folder
cd "/Users/pratham07/Desktop/data analysis projects/smart air"

### Step 2: Run pipeline
cd "/Users/pratham07/Desktop/data analysis projects/smart air"

python3 src/data_fetch.py
python3 src/aqi_calculator.py
python3 src/live_prediction.py
python3 src/clustering_hotspots.py

### Step 3: Run dashboard
streamlit run dashboard/app.py

---

## 🔁 First-Time Setup (Full Run)

cd "/Users/pratham07/Desktop/data analysis projects/smart air"

python3 src/data_fetch.py
python3 src/aqi_calculator.py
python3 src/forecasting.py
python3 src/lstm_forecasting.py
python3 src/multiday_forecasting.py
python3 src/live_prediction.py

streamlit run dashboard/app.py

---

## 📊 Output
- Dashboard showing:
  - Current AQI & Predicted AQI  
  - 4-day Forecast  
  - Hotspot Map  
  - Advisory System  

---

## 🎯 Project Goal
To transform air quality monitoring into prediction + analysis + decision support system.

---

## ⭐ Acknowledgement
Based on CPCB AQI standards and public datasets.

---

⭐ If you like this project, feel free to star the repo!