"""
Weather service using OpenWeatherMap API.
Two-step process: geocoding to get coordinates, then fetch weather data.
"""

import requests
from typing import Tuple, Dict
from core.config import get_settings


settings = get_settings()


class WeatherServiceError(Exception):
    """Base exception for weather service errors."""
    pass


class CityNotFoundError(WeatherServiceError):
    """Raised when geocoding returns no results."""
    pass


class WeatherAPIError(WeatherServiceError):
    """Raised when weather API call fails."""
    pass


def get_coordinates(city: str) -> Tuple[float, float]:
    """
    Get latitude and longitude for a city using OpenWeatherMap Geocoding API.
    
    Args:
        city: City name, optionally with country code (e.g., "London", "Chennai,IN")
    
    Returns:
        Tuple of (latitude, longitude)
    
    Raises:
        CityNotFoundError: If city is not found
        WeatherAPIError: If API call fails
    """
    try:
        params = {
            "q": city,
            "limit": 1,  # Get only the first result
            "appid": settings.openweather_api_key
        }
        
        response = requests.get(
            settings.openweather_geo_url,
            params=params,
            timeout=settings.api_timeout
        )
        response.raise_for_status()
        
        data = response.json()
        
        if not data or len(data) == 0:
            raise CityNotFoundError(f"City '{city}' not found")
        
        # Get first result
        result = data[0]
        lat = result["lat"]
        lon = result["lon"]
        
        return lat, lon
        
    except CityNotFoundError:
        raise
    except requests.exceptions.Timeout:
        raise WeatherAPIError("Weather service timeout")
    except requests.exceptions.RequestException as e:
        raise WeatherAPIError(f"Weather API request failed: {str(e)}")
    except (KeyError, ValueError) as e:
        raise WeatherAPIError(f"Invalid API response: {str(e)}")


def kelvin_to_celsius(kelvin: float) -> float:
    """Convert temperature from Kelvin to Celsius."""
    return round(kelvin - 273.15, 1)


def get_weather(lat: float, lon: float) -> Dict:
    """
    Get weather data for given coordinates.
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        Dictionary with weather data:
        - city: City name
        - country: Country code
        - condition: Weather condition (e.g., "Clear", "Haze")
        - description: Detailed description
        - temperature: Temperature in Celsius
        - feels_like: Feels like temperature in Celsius
        - humidity: Humidity percentage
        - wind_speed: Wind speed in m/s
    
    Raises:
        WeatherAPIError: If API call fails
    """
    try:
        params = {
            "lat": lat,
            "lon": lon,
            "appid": settings.openweather_api_key
        }
        
        response = requests.get(
            settings.openweather_weather_url,
            params=params,
            timeout=settings.api_timeout
        )
        response.raise_for_status()
        
        data = response.json()
        
        # Extract relevant weather information
        weather_data = {
            "city": data.get("name", "Unknown"),
            "country": data.get("sys", {}).get("country", "Unknown"),
            "condition": data["weather"][0]["main"],
            "description": data["weather"][0]["description"],
            "temperature": kelvin_to_celsius(data["main"]["temp"]),
            "feels_like": kelvin_to_celsius(data["main"]["feels_like"]),
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
        }
        
        return weather_data
        
    except requests.exceptions.Timeout:
        raise WeatherAPIError("Weather service timeout")
    except requests.exceptions.RequestException as e:
        raise WeatherAPIError(f"Weather API request failed: {str(e)}")
    except (KeyError, ValueError) as e:
        raise WeatherAPIError(f"Invalid API response: {str(e)}")


def get_weather_for_city(city: str) -> Dict:
    """
    Convenience function to get weather for a city in one call.
    
    Args:
        city: City name, optionally with country code
    
    Returns:
        Weather data dictionary
    
    Raises:
        CityNotFoundError: If city is not found
        WeatherAPIError: If API call fails
    """
    lat, lon = get_coordinates(city)
    return get_weather(lat, lon)
