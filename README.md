# 🌫️ Smart Air: AQI Prediction & Advisory System

> A predictive analytics system for forecasting next-day Air Quality Index (AQI) and generating data-driven environmental insights.

**🔴 Live Dashboard → [smart-air-data-science.streamlit.app]([https://smart-air-data-science.streamlit.app](https://smart-air-data-science-h6jswphov3rvmwydyyt78g.streamlit.app))**

---

## Overview

Air quality in Delhi and other Indian cities fluctuates dramatically based on season, traffic, and weather patterns. This project builds an end-to-end ML pipeline that ingests historical AQI data, trains predictive models, and surfaces forecasts through an interactive Streamlit dashboard — giving users actionable air quality advisories before conditions worsen.

---

## Key Results

| Metric | Value |
|---|---|
| Forecast accuracy | ~89% |
| Best model | Random Forest |
| Deep learning model | LSTM |
| Evaluation metrics | RMSE, MAE |

---

## Features

- **Data Pipeline** — Automated collection, preprocessing, and normalization of historical AQI data (handling missing values, feature selection)
- **ML Forecasting** — Random Forest model for next-day AQI prediction (~89% accuracy)
- **Deep Learning** — LSTM model trained on time-series AQI sequences for comparison
- **Model Comparison** — Side-by-side RMSE and MAE evaluation to select the best-performing model
- **Live Dashboard** — Interactive Streamlit app with real-time AQI trends, predictions, and pollution hotspot maps
- **Advisory Generation** — Automated health advisories based on predicted AQI bands (Good / Moderate / Unhealthy / Hazardous)

---

## Tech Stack

| Layer | Tools |
|---|---|
| Language | Python 3.x |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn (Random Forest) |
| Deep Learning | TensorFlow / Keras (LSTM) |
| Visualization | Matplotlib, Seaborn, Plotly |
| Dashboard | Streamlit |
| Evaluation | RMSE, MAE |

---

## Project Structure

```
smart-air/
├── data/
│   ├── raw/                  # Raw historical AQI datasets
│   └── processed/            # Cleaned and normalized data
├── notebooks/
│   ├── 01_eda.ipynb          # Exploratory data analysis
│   ├── 02_preprocessing.ipynb
│   ├── 03_random_forest.ipynb
│   └── 04_lstm_model.ipynb
├── models/
│   ├── rf_model.pkl          # Saved Random Forest model
│   └── lstm_model.h5         # Saved LSTM model
├── app.py                    # Streamlit dashboard
├── requirements.txt
└── README.md
```

---

## How to Run Locally

```bash
# Clone the repo
git clone https://github.com/pratham0705/<repo-name>.git
cd <repo-name>

# Install dependencies
pip install -r requirements.txt

# Launch the dashboard
streamlit run app.py
```

---

## How It Works

1. **Data Collection** — Historical AQI data (PM2.5, PM10, NO2, SO2, CO, O3) is loaded and cleaned
2. **Preprocessing** — Missing values imputed, features normalized, lag features engineered for time-series context
3. **Model Training** — Random Forest and LSTM models trained and evaluated on an 80/20 split
4. **Prediction** — Best model generates next-day AQI forecast per location
5. **Advisory** — AQI band classification maps forecast to a health advisory category
6. **Dashboard** — All outputs visualized in Streamlit with interactive filters and maps

---

## Future Improvements

- [ ] Real-time API integration (OpenAQ / CPCB) for live data feeds
- [ ] Multi-day forecast window (3-day, 7-day)
- [ ] City-level comparison across major Indian metros
- [ ] Push notification alerts when AQI crosses thresholds

---

## Author

**Pratham Narula** — [LinkedIn](https://www.linkedin.com/in/pratham-narula-885203240) | [GitHub](https://github.com/pratham0705) | pratham0705narula@gmail.com
