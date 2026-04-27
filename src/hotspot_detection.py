def detect_hotspot(aqi, category):
    if category in ["Very Poor", "Severe"]:
        return "Hotspot"
    elif category == "Poor":
        return "Emerging Hotspot"
    else:
        return "Normal"


def hotspot_priority(aqi):
    if aqi >= 400:
        return "Critical"
    elif aqi >= 300:
        return "High"
    elif aqi >= 200:
        return "Medium"
    else:
        return "Low"