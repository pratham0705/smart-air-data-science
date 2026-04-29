import os
from datetime import datetime, timedelta
# import sys
# sys.path.append("src")
# from ai_advisory import generate_ai_advisory
import sys
sys.path.append("src")
from gemini_advisory import generate_gemini_advisory

import pandas as pd
import streamlit as st
import folium
import plotly.express as px
import plotly.graph_objects as go
from folium.plugins import HeatMap
from streamlit_folium import st_folium


st.set_page_config(
    page_title="Smart Air Delhi",
    page_icon="🌫️",
    layout="wide"
)

st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

DATA_PATH = "data/processed/station_predictions.csv"

if not os.path.exists(DATA_PATH):
    st.error("Run pipeline first: data_fetch.py → aqi_calculator.py → live_prediction.py")
    st.stop()

df = pd.read_csv(DATA_PATH)

df = df.dropna(subset=["latitude", "longitude", "AQI"])
df["AQI"] = pd.to_numeric(df["AQI"], errors="coerce")
df["predicted_AQI_tomorrow"] = pd.to_numeric(df["predicted_AQI_tomorrow"], errors="coerce")
df["AQI_change"] = pd.to_numeric(df["AQI_change"], errors="coerce")

today_date = datetime.now().strftime("%d %b %Y")
tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%d %b %Y")


def get_aqi_category(aqi):
    if pd.isna(aqi):
        return "Unknown"
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
    return "Severe"


def get_color(category):
    return {
        "Good": "green",
        "Satisfactory": "blue",
        "Moderate": "orange",
        "Poor": "red",
        "Very Poor": "purple",
        "Severe": "darkred",
    }.get(category, "gray")


def make_gauge(value, title):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=float(value),
        title={"text": title},
        gauge={
            "axis": {"range": [0, 500]},
            "bar": {"color": "black"},
            "steps": [
                {"range": [0, 50], "color": "#22C55E"},
                {"range": [51, 100], "color": "#38BDF8"},
                {"range": [101, 200], "color": "#FACC15"},
                {"range": [201, 300], "color": "#FB923C"},
                {"range": [301, 400], "color": "#A855F7"},
                {"range": [401, 500], "color": "#DC2626"},
            ],
        }
    ))
    fig.update_layout(height=260, margin=dict(l=20, r=20, t=50, b=20))
    return fig


def chart_layout(fig, height=450):
    fig.update_layout(
        height=height,
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=30, r=30, t=60, b=40),
        font=dict(size=13),
    )
    return fig


st.sidebar.title("🌫️ Smart Air Delhi")

stations = sorted(df["station"].dropna().unique())
selected_station = st.sidebar.selectbox("Select Station", stations)

category_filter = st.sidebar.multiselect(
    "AQI Category",
    sorted(df["AQI_Category"].dropna().unique()),
    default=sorted(df["AQI_Category"].dropna().unique())
)

status_filter = st.sidebar.multiselect(
    "Data Status",
    sorted(df["data_status"].dropna().unique()),
    default=sorted(df["data_status"].dropna().unique())
)

filtered_df = df[
    (df["AQI_Category"].isin(category_filter)) &
    (df["data_status"].isin(status_filter))
].copy()

station_row = df[df["station"] == selected_station].iloc[0]
future_category = get_aqi_category(station_row["predicted_AQI_tomorrow"])

st.title("🌫️ Smart Air Delhi")
st.caption(
    f"Computed Live AQI: {today_date} | Predicted AQI: {tomorrow_date} | "
    "AQI Forecasting • Hotspots • Advisory • Pollution Mapping"
)

overview_tab, map_tab, hotspot_tab, forecast_tab, graphs_tab, model_tab, data_tab = st.tabs(
    ["🏠 Overview", "🗺️ Maps", "🔥 Hotspots", "📈 Forecast", "📊 Graphs", "🤖 Models", "📋 Data"]
)


# ---------------- OVERVIEW TAB ----------------
with overview_tab:
    k1, k2, k3, k4, k5 = st.columns(5)

    k1.metric("Computed Avg AQI", round(filtered_df["AQI"].mean(), 2))
    k2.metric("Tomorrow Avg AQI", round(filtered_df["predicted_AQI_tomorrow"].mean(), 2))
    k3.metric("Active Stations", len(filtered_df))
    k4.metric("Hotspots", len(filtered_df[filtered_df["cluster_hotspot_status"] == "Hotspot Cluster"]))
    k5.metric("Fresh Stations", len(filtered_df[filtered_df["data_status"] == "Fresh"]))

    st.markdown("---")
    st.subheader(f"📍 Station Intelligence: {selected_station}")

    c1, c2, c3 = st.columns([1, 1, 1.5])

    with c1:
        st.plotly_chart(
            make_gauge(station_row["AQI"], f"Computed Live AQI"),
            use_container_width=True
        )

    with c2:
        st.plotly_chart(
            make_gauge(station_row["predicted_AQI_tomorrow"], f"Predicted AQI Tomorrow"),
            use_container_width=True
        )

    with c3:
        st.markdown("### Live + Forecast Summary")
        st.write(f"**Today:** {today_date}")
        st.write(f"**Tomorrow:** {tomorrow_date}")
        st.write(f"**Computed Live AQI:** {round(station_row['AQI'], 2)} ({station_row['AQI_Category']})")
        st.write(f"**Predicted AQI Tomorrow:** {round(station_row['predicted_AQI_tomorrow'], 2)} ({future_category})")
        st.write(f"**Trend:** {station_row['forecast_trend']} ({station_row['AQI_change']})")
        st.write(f"**Dominant Pollutant:** {str(station_row['dominant_pollutant']).upper()} = {station_row['dominant_value']}")
        st.write(f"**Data Status:** {station_row['data_status']}")
        st.write(f"**GRAP Stage:** {station_row['GRAP_Stage']}")
        st.write(f"**GRAP Advisory:** {station_row['GRAP_Advisory']}")
        st.write(f"**Cluster Hotspot Status:** {station_row['cluster_hotspot_status']}")
        st.write(f"**Cluster Priority:** {station_row['cluster_priority']}")

        if "confidence_level" in station_row.index:
            st.write(f"**Confidence:** {station_row['confidence_level']} ({station_row['confidence_score']}%)")

    st.subheader("🧠 Advisory & Precautions")
    a1, a2, a3, a4 = st.columns(4)

    a1.info(f"**Outdoor Decision**\n\n{station_row['outdoor_decision']}")
    a2.warning(f"**Health Advisory**\n\n{station_row['health_advisory']}")
    a3.error(f"**Precautions**\n\n{station_row['precautions']}")
    a4.success(f"**Travel Advisory**\n\n{station_row['travel_advisory']}")

    # st.subheader("🤖 AI-Generated Advisory")

    # if st.button("Generate AI Advisory"):
    #     try:
    #         ai_text = generate_ai_advisory(
    #             station=selected_station,
    #             aqi=round(station_row["AQI"], 2),
    #             category=station_row["AQI_Category"],
    #             pollutant=station_row["dominant_pollutant"],
    #             trend=station_row["forecast_trend"],
    #             grap_stage=station_row["GRAP_Stage"],
    #             hotspot=station_row["hotspot_status"]
    #         )

    #         st.success(ai_text)

    #     except Exception as e:
    #         st.error("AI advisory could not be generated. Check API key or quota.")
    #         st.write(e)
    st.subheader("🤖 AI Advisory")

    if st.button("Generate AI Advisory"):
        try:
            ai_text = generate_gemini_advisory(
                station=selected_station,
                aqi=round(station_row["AQI"], 2),
                category=station_row["AQI_Category"],
                pollutant=station_row["dominant_pollutant"],
                trend=station_row["forecast_trend"],
                grap_stage=station_row["GRAP_Stage"],
                hotspot=station_row["hotspot_status"]
            )
            st.success(ai_text)

        except Exception as e:
            st.error("Gemini advisory could not be generated. Check API key or quota.")
            st.write(e)

    st.subheader("🚨 GRAP Status")

    grap_stage = station_row["GRAP_Stage"]

    if "Stage IV" in grap_stage:
        st.error(f"{grap_stage}")
    elif "Stage III" in grap_stage:
        st.error(f"{grap_stage}")
    elif "Stage II" in grap_stage:
        st.warning(f"{grap_stage}")
    elif "Stage I" in grap_stage:
        st.info(f"{grap_stage}")
    else:
        st.success(f"{grap_stage}")


# ---------------- MAP TAB ----------------
with map_tab:
    st.subheader("🗺️ Delhi AQI Station Map")

    map_choice = st.radio(
        "Choose Map Type",
        ["Station Pin Map", "Pollution Heatmap", "Combined Map"],
        horizontal=True
    )

    m = folium.Map(location=[28.61, 77.23], zoom_start=10, tiles="CartoDB positron")

    if map_choice in ["Station Pin Map", "Combined Map"]:
        for _, row in filtered_df.iterrows():
            forecast_cat = get_aqi_category(row["predicted_AQI_tomorrow"])

            confidence_html = ""
            if "confidence_level" in row.index:
                confidence_html = f"<b>Confidence:</b> {row['confidence_level']} ({row['confidence_score']}%)<br>"

            popup_html = f"""
            <div style="font-family: Arial; width: 310px;">
                <h4>{row['station']}</h4>
                <b>Computed Live AQI ({today_date}):</b> {round(row['AQI'], 2)} ({row['AQI_Category']})<br>
                <b>Predicted AQI ({tomorrow_date}):</b> {round(row['predicted_AQI_tomorrow'], 2)} ({forecast_cat})<br>
                <b>Trend:</b> {row['forecast_trend']} ({row['AQI_change']})<br>
                <b>Cluster Status:</b> {row['cluster_hotspot_status']}<br>
                <b>Cluster Priority:</b> {row['cluster_priority']}<br>
                <b>Dominant Pollutant:</b> {str(row['dominant_pollutant']).upper()} = {row['dominant_value']}<br>
                <b>Data Status:</b> {row['data_status']}<br>
                {confidence_html}
                <hr>
                <b>Outdoor:</b> {row['outdoor_decision']}<br>
                <b>Travel:</b> {row['travel_advisory']}

            </div>
            """

            tooltip = (
                f"{row['station']} | AQI: {round(row['AQI'], 1)} | "
                f"Tomorrow: {round(row['predicted_AQI_tomorrow'], 1)}"
            )

            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                popup=folium.Popup(popup_html, max_width=350),
                tooltip=tooltip,
                icon=folium.Icon(
                    color=get_color(row["AQI_Category"]),
                    icon="map-marker",
                    prefix="fa"
                )
            ).add_to(m)

    if map_choice in ["Pollution Heatmap", "Combined Map"]:
        heat_data = filtered_df[["latitude", "longitude", "AQI"]].dropna().values.tolist()

        HeatMap(
            heat_data,
            min_opacity=0.55,
            radius=85,
            blur=65,
            max_zoom=10,
            name="AQI Heatmap"
        ).add_to(m)

    folium.LayerControl().add_to(m)
    st_folium(m, width=None, height=650)

    st.caption(
        "Note: Heatmap is an estimated spatial layer from available station points, not satellite imagery."
    )


# ---------------- HOTSPOT TAB ----------------
with hotspot_tab:
    st.subheader("🔥 AI-Detected Hotspot Clusters")

    hotspot_df = filtered_df[
        filtered_df["cluster_hotspot_status"] == "Hotspot Cluster"
    ].sort_values("AQI", ascending=False).copy()

    if hotspot_df.empty:
        st.success("No hotspot cluster detected currently.")
    else:
        show_cols = [
            "station",
            "AQI",
            "AQI_Category",
            "predicted_AQI_tomorrow",
            "AQI_change",
            "forecast_trend",
            "dominant_pollutant",
            "cluster_hotspot_status",
            "cluster_priority",
            "data_status"
        ]

        st.dataframe(
            hotspot_df[show_cols],
            use_container_width=True,
            hide_index=True
        )

        st.markdown("### Top AI-Detected Hotspot Regions")

        top_hot = hotspot_df.head(10)

        fig = px.bar(
            top_hot.sort_values("AQI"),
            x="AQI",
            y="station",
            orientation="h",
            text="AQI",
            color="AQI",
            color_continuous_scale="OrRd",
            title="Top 10 AI-Detected Hotspot Regions"
        )

        fig.update_traces(texttemplate="%{text:.0f}", textposition="outside")
        st.plotly_chart(chart_layout(fig, 500), use_container_width=True)


# ---------------- FORECAST TAB ----------------
with forecast_tab:
    st.subheader("📈 AQI Forecast Verification Style Graph")

    forecast_line = filtered_df.sort_values("AQI", ascending=False).head(25).copy()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=forecast_line["station"],
        y=forecast_line["AQI"],
        mode="lines+markers",
        name=f"Computed Live AQI ({today_date})",
        line=dict(width=3),
        marker=dict(size=8)
    ))

    fig.add_trace(go.Scatter(
        x=forecast_line["station"],
        y=forecast_line["predicted_AQI_tomorrow"],
        mode="lines+markers",
        name=f"Predicted AQI ({tomorrow_date})",
        line=dict(width=3),
        marker=dict(size=8)
    ))

    fig.update_layout(
        title="Forecast Verification: Computed Live AQI vs Predicted AQI",
        xaxis_title="Monitoring Stations",
        yaxis_title="AQI",
        height=650,
        xaxis_tickangle=-45,
        yaxis=dict(range=[0, max(500, forecast_line[["AQI", "predicted_AQI_tomorrow"]].max().max() + 50)]),
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader(f"📍 Selected Station Forecast: {selected_station}")

    forecast_dates = [
    today_date,
    (datetime.now() + timedelta(days=1)).strftime("%d %b %Y"),
    (datetime.now() + timedelta(days=2)).strftime("%d %b %Y"),
    (datetime.now() + timedelta(days=3)).strftime("%d %b %Y"),
    (datetime.now() + timedelta(days=4)).strftime("%d %b %Y"),
]

    selected_forecast = pd.DataFrame({
        "Date": forecast_dates,
        "AQI": [
            station_row["AQI"],
            station_row["predicted_AQI_day_1"],
            station_row["predicted_AQI_day_2"],
            station_row["predicted_AQI_day_3"],
            station_row["predicted_AQI_day_4"],
        ],
        "Type": [
            "Computed Live AQI",
            "Forecast",
            "Forecast",
            "Forecast",
            "Forecast",
        ]
    })

    fig2 = px.line(
        selected_forecast,
        x="Date",
        y="AQI",
        markers=True,
        title=f"4-Day AQI Forecast for {selected_station}"
    )

    fig2.update_traces(line=dict(width=4), marker=dict(size=12))
    fig2.update_yaxes(range=[0, max(500, selected_forecast["AQI"].max() + 50)])

    st.plotly_chart(fig2, use_container_width=True)

    fig2 = px.line(
        selected_forecast,
        x="Date",
        y="AQI",
        markers=True,
        title=f"Today vs Tomorrow AQI for {selected_station}"
    )
    fig2.update_traces(line=dict(width=4), marker=dict(size=12))
    st.plotly_chart(chart_layout(fig2, 450), use_container_width=True)


# ---------------- GRAPHS TAB ----------------
with graphs_tab:
    st.subheader("📊 AQI Analytics & Charts")

    c3, c4 = st.columns(2)

    with c3:
        top_df = filtered_df.sort_values("AQI", ascending=False).head(15)

        fig_bar = px.bar(
            top_df,
            x="station",
            y=["AQI", "predicted_AQI_tomorrow"],
            barmode="group",
            title="Top 15 Stations: Computed Live AQI vs Predicted AQI"
        )
        fig_bar.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(chart_layout(fig_bar, 500), use_container_width=True)

    with c4:
        pollutant_df = filtered_df["dominant_pollutant"].value_counts().reset_index()
        pollutant_df.columns = ["Pollutant", "Count"]

        fig_pie = px.pie(
            pollutant_df,
            names="Pollutant",
            values="Count",
            title="Dominant Pollutant Distribution",
            hole=0.45
        )
        st.plotly_chart(chart_layout(fig_pie, 500), use_container_width=True)

    c5, c6 = st.columns(2)

    with c5:
        cat_df = filtered_df["AQI_Category"].value_counts().reset_index()
        cat_df.columns = ["AQI Category", "Count"]

        fig_cat = px.bar(
            cat_df,
            x="AQI Category",
            y="Count",
            text="Count",
            title="Stations by AQI Category",
            color="AQI Category"
        )
        fig_cat.update_traces(textposition="outside")
        st.plotly_chart(chart_layout(fig_cat, 450), use_container_width=True)

    with c6:
        trend_df = filtered_df["forecast_trend"].value_counts().reset_index()
        trend_df.columns = ["Forecast Trend", "Count"]

        fig_trend = px.bar(
            trend_df,
            x="Forecast Trend",
            y="Count",
            text="Count",
            title="Forecast Trend Distribution",
            color="Forecast Trend"
        )
        fig_trend.update_traces(textposition="outside")
        st.plotly_chart(chart_layout(fig_trend, 450), use_container_width=True)

    st.markdown("---")
    st.subheader("🧠 Pollution Cause Analysis")

    imp_path = "data/processed/feature_importance.csv"

    if os.path.exists(imp_path):
        imp_df = pd.read_csv(imp_path)

        c1, c2 = st.columns([1, 1])

        with c1:
            fig_imp = px.bar(
                imp_df,
                x="Importance",
                y="Feature",
                orientation="h",
                title="Pollution Contribution by Pollutants",
                color="Importance",
                color_continuous_scale="Reds"
            )
            fig_imp.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_imp, use_container_width=True)

        with c2:
            st.markdown("### 🔍 Insights")

            top_feature = imp_df.iloc[0]["Feature"]

            st.write(f"• **Primary pollution driver:** {top_feature}")
            st.write("• PM2.5 and PM10 generally dominate AQI spikes")
            st.write("• Vehicular emissions → NO2 & CO")
            st.write("• Industrial sources → SO2 & NOx")
            st.write("• Seasonal effects impact pollutant concentration")

    else:
        st.warning("Run forecasting.py to generate feature importance.")


# ---------------- MODEL TAB ----------------
with model_tab:
    st.subheader("🤖 Model Performance Comparison")

    model_results = pd.DataFrame({
        "Model": ["Random Forest", "XGBoost", "LSTM"],
        "R² Score": [0.8928, 0.8975, 0.8940],
        "MAE": [27.08, 26.76, 26.34],
        "RMSE": [37.20, 36.38, 37.08],
        "Model Type": ["Machine Learning", "Machine Learning", "Deep Learning"]
    })

# -------- TABLE (FULL WIDTH) --------
    st.markdown("### 📊 Model Performance Table")
    st.dataframe(model_results, use_container_width=True, hide_index=True)

    st.markdown("---")

# -------- CHART (FULL WIDTH) --------
    st.markdown("### 📈 Model Accuracy Comparison")

    fig_model = px.bar(
        model_results,
        x="Model",
        y="R² Score",
        color="Model Type",
        text="R² Score",
    )

    fig_model.update_traces(
        texttemplate="%{text:.3f}",
        textposition="outside"
    )

    fig_model.update_layout(
        height=450,
        xaxis_title="Model",
        yaxis_title="R² Score",
        yaxis=dict(range=[0, 1]),
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    st.plotly_chart(fig_model, use_container_width=True)

# -------- INSIGHT --------
    st.markdown("### 📌 Insight")

    st.info(
        "XGBoost is selected as the best model due to highest R² score and lowest RMSE. "
        "LSTM shows competitive performance, validating temporal learning capability, "
        "while Random Forest provides strong baseline results."
    )

# ---------------- DATA TAB ----------------
with data_tab:
    st.subheader("📋 Complete Station Data")

    data_cols = [
        "station", "AQI", "AQI_Category", "predicted_AQI_tomorrow",
        "AQI_change", "forecast_trend", "dominant_pollutant",
        "dominant_value", "cluster_hotspot_status",
            "cluster_priority",
        "outdoor_decision", "health_advisory", "precautions",
        "travel_advisory", "data_status", "datetime","predicted_AQI_day_1",
        "predicted_AQI_day_2","predicted_AQI_day_3","predicted_AQI_day_4",
    ]

    optional_cols = ["available_pollutants_count", "confidence_score", "confidence_level"]
    data_cols += [col for col in optional_cols if col in df.columns]

    st.dataframe(
        filtered_df[data_cols].sort_values("AQI", ascending=False),
        use_container_width=True,
        hide_index=True
    )

    csv = filtered_df[data_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Dashboard Data as CSV",
        data=csv,
        file_name="smart_air_dashboard_data.csv",
        mime="text/csv"
    )

st.caption(
    "Smart Air Delhi: real-time pollutant-based computed AQI, AI prediction, hotspot detection, advisory, and map-based decision support."
)