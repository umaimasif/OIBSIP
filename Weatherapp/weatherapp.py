import requests

def get_coordinates(location_query):
    """
    Takes a city name or ZIP code and returns its latitude, longitude, and formatted name.
    """
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_params = {
        "name": location_query,
        "count": 1, 
        "language": "en",
        "format": "json"
    }
    
    try:
        response = requests.get(geo_url, params=geo_params)
        response.raise_for_status()
        data = response.json()
        
       
        if "results" not in data or len(data["results"]) == 0:
            return None
            
        result = data["results"][0]
        return {
            "latitude": result["latitude"],
            "longitude": result["longitude"],
            "name": result.get("name", location_query),
            "country": result.get("country", "")
        }
    except requests.exceptions.RequestException as e:
        print(f"Network error during geocoding: {e}")
        return None

def interpret_weather_code(code):
    """
    Translates WMO weather codes into human-readable conditions.
    """
    weather_mapping = {
        0: "Clear sky",
        1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
        95: "Thunderstorm",
        99: "Thunderstorm with heavy hail"
    }
   
    return weather_mapping.get(code, "Unknown conditions")

def get_weather(lat, lon, unit="celsius"):
    """
    Fetches the current weather for a specific latitude and longitude.
    """
    weather_url = "https://api.open-meteo.com/v1/forecast"
    
    
    weather_params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,weather_code",
        "temperature_unit": unit
    }
    
    try:
        response = requests.get(weather_url, params=weather_params)
        response.raise_for_status()
        data = response.json()
        
        current = data["current"]
     
        temp = current["temperature_2m"]
        humidity = current["relative_humidity_2m"]
        weather_code = current["weather_code"]
        
        return {
            "temperature": temp,
            "humidity": humidity,
            "condition": interpret_weather_code(weather_code)
        }
    except requests.exceptions.RequestException as e:
        print(f"Network error while fetching weather: {e}")
        return None

def main():
    """
    The main flow of our command-line application.
    """
    print("="*40)
    print("🌤️  Welcome to the CLI Weather App! 🌤️")
    print("="*40)
    
    location = input("Enter a city name or ZIP code: ").strip()
    if not location:
        print("Location cannot be empty. Exiting...")
        return
        
    unit_choice = input("Use Fahrenheit? (y/n, default is Celsius): ").strip().lower()
    unit_system = "fahrenheit" if unit_choice == 'y' else "celsius"
    unit_symbol = "°F" if unit_system == "fahrenheit" else "°C"
    
    print("\n🔍 Searching for location...")
    geo_data = get_coordinates(location)
    
    if not geo_data:
        print(f"Could not find coordinates for '{location}'. Please check your spelling.")
        return
        
    print(f" Found: {geo_data['name']}, {geo_data['country']}")
    print(" Fetching current weather data...\n")
    
    weather_data = get_weather(geo_data['latitude'], geo_data['longitude'], unit_system)
    
    if weather_data:
        print("-" * 30)
        print(f"📍 Location:   {geo_data['name']}")
        print(f"🌡️  Temp:       {weather_data['temperature']}{unit_symbol}")
        print(f"💧 Humidity:   {weather_data['humidity']}%")
        print(f"☁️  Condition:  {weather_data['condition']}")
        print("-" * 30)

if __name__ == "__main__":
    main()
