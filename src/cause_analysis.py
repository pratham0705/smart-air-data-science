import os
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(BASE_DIR, "models", "random_forest.pkl")
DATA_PATH = os.path.join(BASE_DIR, "data", "air_quality.csv")

features = ['PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 'CO', 'SO2', 'O3']

def analyze_causes():
    model = joblib.load(MODEL_PATH)

    importance = model.feature_importances_

    result = pd.DataFrame({
        "Pollutant": features,
        "Importance": importance
    }).sort_values(by="Importance", ascending=False)

    print("\nTop Pollutants Affecting AQI:")
    print(result)

    output_path = os.path.join(BASE_DIR, "data", "feature_importance.csv")
    result.to_csv(output_path, index=False)

    print("\n✅ Cause analysis completed!")
    print(f"Saved file: {output_path}")

if __name__ == "__main__":
    analyze_causes()