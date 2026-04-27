import os
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FILE_PATH = os.path.join(BASE_DIR, "data", "feature_importance.csv")

def plot_feature_importance():
    df = pd.read_csv(FILE_PATH)

    plt.figure()
    plt.bar(df["Pollutant"], df["Importance"])
    plt.title("Feature Importance - Pollutants Affecting AQI")
    plt.xlabel("Pollutants")
    plt.ylabel("Importance")

    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.show()

if __name__ == "__main__":
    plot_feature_importance()