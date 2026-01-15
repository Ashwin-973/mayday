import requests

OPENWEATHER_KEY=""
def geocode_city(city):
    url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {
        "q": city,
        "limit": 1,
        "appid": OPENWEATHER_KEY
    }

    r = requests.get(url, params=params)
    data = r.json()

    if not data:
        return None

    return {
        "lat": data[0]["lat"],
        "lon": data[0]["lon"],
        "name": data[0]["name"],
        "country": data[0]["country"]
    }

def kelvin_to_celsius(k):
    return round(k - 273.15, 1)


def get_weather(lat, lon):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_KEY
    }

    r = requests.get(url, params=params)
    data = r.json()

    if str(data.get("cod")) != "200":
        return None

    return {
        "condition": data["weather"][0]["description"],
        "temp": kelvin_to_celsius(data["main"]["temp"]),
        "feels_like": kelvin_to_celsius(data["main"]["feels_like"]),
        "humidity": data["main"]["humidity"],
        "wind": data["wind"]["speed"],
        "city": data["name"],
        "country": data["sys"]["country"]
    }




print(get_weather(geocode_city("chennai")["lat"], geocode_city("chennai")["lon"]))