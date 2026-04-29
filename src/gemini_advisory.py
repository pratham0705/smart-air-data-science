import os
from google import genai

client = genai.Client(api_key="AIzaSyDpnDmVfbiVBaWeA5ySqoMfke0sXslVvP0")

def generate_gemini_advisory(station, aqi, category, pollutant, trend, grap_stage, hotspot):
    prompt = f"""
You are an air quality advisory assistant.

Generate a professional, safe and practical AQI advisory and travel advisory includes travel with which transport is best.

Station: {station}
AQI: {aqi}
AQI Category: {category}
Dominant Pollutant: {pollutant}
Forecast Trend: {trend}
GRAP Stage: {grap_stage}
Hotspot Status: {hotspot}

Output exactly in this format (headings in bold):
Health Advisory:
Precautions:
Travel Advisory:

Keep it simple, non-medical, and suitable for public users.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text