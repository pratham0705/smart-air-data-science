def generate_advisory(aqi, category, pollutant):
    pollutant = str(pollutant).upper()

    if category == "Good":
        return {
            "outdoor_decision": "Safe to go outside",
            "health_advisory": "Air quality is good. Normal outdoor activity is safe.",
            "precautions": "No special precautions required.",
            "travel_advisory": "Travel is safe."
        }

    elif category == "Satisfactory":
        return {
            "outdoor_decision": "Generally safe",
            "health_advisory": "Air quality is acceptable, but very sensitive people should avoid prolonged outdoor exertion.",
            "precautions": "Carry a mask if you are sensitive to pollution.",
            "travel_advisory": "Travel is mostly safe."
        }

    elif category == "Moderate":
        return {
            "outdoor_decision": "Go outside with precautions",
            "health_advisory": f"Moderate pollution level. {pollutant} is the dominant pollutant.",
            "precautions": "Avoid heavy outdoor exercise. Sensitive groups should use an N95 mask.",
            "travel_advisory": "Prefer metro or low-traffic routes."
        }

    elif category == "Poor":
        return {
            "outdoor_decision": "Avoid unnecessary outdoor activity",
            "health_advisory": f"Poor air quality. {pollutant} is likely causing health risk.",
            "precautions": "Wear N95 mask. Avoid jogging, cycling, and long exposure.",
            "travel_advisory": "Avoid high-traffic routes and prefer public transport."
        }

    elif category == "Very Poor":
        return {
            "outdoor_decision": "Stay indoors if possible",
            "health_advisory": f"Very poor air quality. {pollutant} is the major pollutant.",
            "precautions": "Use N95 mask outdoors. Keep windows closed. Use air purifier if available.",
            "travel_advisory": "Avoid unnecessary travel. Prefer metro and enclosed transport."
        }

    elif category == "Severe":
        return {
            "outdoor_decision": "Do not go outside unless necessary",
            "health_advisory": f"Severe air pollution. {pollutant} level is dangerous.",
            "precautions": "Avoid outdoor exposure. Use N95/N99 mask if travel is unavoidable.",
            "travel_advisory": "Avoid travel. If urgent, choose shortest low-exposure route."
        }

    else:
        return {
            "outdoor_decision": "Unknown",
            "health_advisory": "Insufficient data to generate advisory.",
            "precautions": "Check nearest station manually.",
            "travel_advisory": "No travel advisory available."
        }