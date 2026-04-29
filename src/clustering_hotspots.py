import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


def apply_kmeans_hotspots(df, n_clusters=3):
    df = df.copy()

    features = [
        "AQI",
        "predicted_AQI_tomorrow",
        "latitude",
        "longitude"
    ]

    for col in features:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=features)

    X = df[features]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df["cluster"] = kmeans.fit_predict(X_scaled)

    cluster_summary = (
        df.groupby("cluster")["AQI"]
        .mean()
        .sort_values()
        .reset_index()
    )

    cluster_labels = {}

    if len(cluster_summary) == 3:
        cluster_labels[cluster_summary.iloc[0]["cluster"]] = "Low Pollution Cluster"
        cluster_labels[cluster_summary.iloc[1]["cluster"]] = "Moderate Pollution Cluster"
        cluster_labels[cluster_summary.iloc[2]["cluster"]] = "Hotspot Cluster"

    df["cluster_hotspot_status"] = df["cluster"].map(cluster_labels)

    df["cluster_priority"] = df["cluster_hotspot_status"].map({
        "Low Pollution Cluster": "Low",
        "Moderate Pollution Cluster": "Medium",
        "Hotspot Cluster": "High"
    })

    return df


if __name__ == "__main__":
    input_path = "data/processed/station_predictions.csv"
    output_path = "data/processed/station_predictions.csv"

    df = pd.read_csv(input_path)

    df = apply_kmeans_hotspots(df)

    df.to_csv(output_path, index=False)

    print(df[[
        "station",
        "AQI",
        "predicted_AQI_tomorrow",
        "cluster",
        "cluster_hotspot_status",
        "cluster_priority"
    ]].head(20))

    print("\nK-Means hotspot clustering completed.")