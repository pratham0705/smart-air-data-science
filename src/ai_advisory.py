import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_ai_advisory(station, aqi, category, pollutant, trend, grap_stage, hotspot):
    prompt = f"""
You are an air quality advisory assistant.

Generate a short, safe, practical advisory for this AQI condition.

Station: {station}
AQI: {aqi}
AQI Category: {category}
Dominant Pollutant: {pollutant}
Forecast Trend: {trend}
GRAP Stage: {grap_stage}
Hotspot Status: {hotspot}

Give output in exactly this format:
Health Advisory:
Precautions:
Travel Advisory:

Keep it simple, non-medical, and suitable for public users.
Do not mention emergency treatment.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You generate safe public air-quality advisories."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=180
    )

    return response.choices[0].message.content