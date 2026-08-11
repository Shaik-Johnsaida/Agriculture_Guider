"""
Weather Service Module for AgriShield AI.
Fetches real-time weather and 48-hour hourly forecasts from Open-Meteo API.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import datetime
import requests
from config import OPEN_METEO_FORECAST_URL


@dataclass
class HourlyForecastPoint:
    time_str: str          # e.g. "2026-08-11 14:00"
    hour: int              # e.g. 14
    temp_c: float          # °C
    humidity_pct: float    # %
    rain_prob_pct: float   # %
    rainfall_mm: float     # mm
    wind_speed_kmh: float  # km/h
    uv_index: float        # UV index scale


@dataclass
class WeatherData:
    location_name: str
    latitude: float
    longitude: float
    current_temp_c: float
    current_humidity_pct: float
    current_rain_prob_pct: float
    current_rainfall_mm: float
    current_wind_speed_kmh: float
    condition_text: str
    hourly_forecast: List[HourlyForecastPoint]
    is_live: bool = True


class WeatherService:
    """
    Real-Time Weather Intelligence Client for AgriShield AI.
    Integrates with Open-Meteo API with offline demo fallback resilience.
    """

    @staticmethod
    def get_weather(lat: float, lon: float, location_name: str = "Farm Location") -> WeatherData:
        """
        Fetches live weather & 48h forecast from Open-Meteo API.
        Falls back to realistic demo weather data if network is unavailable.
        """
        try:
            params = {
                "latitude": lat,
                "longitude": lon,
                "current_weather": "true",
                "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,precipitation,wind_speed_10m,uv_index,weather_code",
                "timezone": "auto",
                "forecast_days": 3
            }
            
            response = requests.get(OPEN_METEO_FORECAST_URL, params=params, timeout=6)
            
            if response.status_code == 200:
                data = response.json()
                current = data.get("current_weather", {})
                hourly = data.get("hourly", {})
                
                times = hourly.get("time", [])
                temps = hourly.get("temperature_2m", [])
                humidities = hourly.get("relative_humidity_2m", [])
                rain_probs = hourly.get("precipitation_probability", [])
                rainfalls = hourly.get("precipitation", [])
                winds = hourly.get("wind_speed_10m", [])
                uvs = hourly.get("uv_index", [0] * len(times))

                forecast_points = []
                for i in range(min(48, len(times))):
                    t_str = times[i]
                    dt = datetime.datetime.fromisoformat(t_str)
                    forecast_points.append(
                        HourlyForecastPoint(
                            time_str=dt.strftime("%b %d, %H:00"),
                            hour=dt.hour,
                            temp_c=float(temps[i]),
                            humidity_pct=float(humidities[i]) if i < len(humidities) else 70.0,
                            rain_prob_pct=float(rain_probs[i]) if i < len(rain_probs) else 10.0,
                            rainfall_mm=float(rainfalls[i]) if i < len(rainfalls) else 0.0,
                            wind_speed_kmh=float(winds[i]) if i < len(winds) else 8.0,
                            uv_index=float(uvs[i]) if i < len(uvs) else 4.0
                        )
                    )

                # Determine condition text from WMO weather code
                wcode = current.get("weathercode", 0)
                condition_text = WeatherService._wmo_code_to_text(wcode)

                # Get current rain prob from current hour forecast point
                cur_rain_prob = forecast_points[0].rain_prob_pct if forecast_points else 15.0
                cur_humidity = forecast_points[0].humidity_pct if forecast_points else 72.0

                return WeatherData(
                    location_name=location_name,
                    latitude=lat,
                    longitude=lon,
                    current_temp_c=float(current.get("temperature", 28.5)),
                    current_humidity_pct=float(cur_humidity),
                    current_rain_prob_pct=float(cur_rain_prob),
                    current_rainfall_mm=float(forecast_points[0].rainfall_mm) if forecast_points else 0.0,
                    current_wind_speed_kmh=float(current.get("windspeed", 10.5)),
                    condition_text=condition_text,
                    hourly_forecast=forecast_points,
                    is_live=True
                )
        except Exception as e:
            print(f"[WARN] Weather API request failed ({e}). Using demo fallback weather.")

        # Fallback realistic weather data
        return WeatherService._get_fallback_weather(lat, lon, location_name)

    @staticmethod
    def _wmo_code_to_text(code: int) -> str:
        """Converts WMO weather code to clear English description."""
        wmo_map = {
            0: "Clear Sky ☀️",
            1: "Mainly Clear 🌤️",
            2: "Partly Cloudy ⛅",
            3: "Overcast ☁️",
            45: "Foggy 🌫️",
            51: "Light Drizzle 🌧️",
            61: "Slight Rain 🌦️",
            63: "Moderate Rain 🌧️",
            65: "Heavy Rain ⛈️",
            80: "Rain Showers 🌦️",
            95: "Thunderstorm 🌩️"
        }
        return wmo_map.get(code, "Partly Cloudy ⛅")

    @staticmethod
    def _get_fallback_weather(lat: float, lon: float, location_name: str) -> WeatherData:
        """Generates realistic demo weather data for hackathon demo resilience."""
        now = datetime.datetime.now()
        forecast_points = []
        
        # Simulate approaching rainy front in 4-6 hours for dynamic demo reasoning!
        for i in range(48):
            future_dt = now + datetime.timedelta(hours=i)
            # High rain probability around hours 3-8
            if 3 <= i <= 8:
                r_prob = 78.0
                r_mm = 4.2
                wind = 18.5
                temp = 25.0
                hum = 88.0
            elif 18 <= i <= 24: # Tomorrow morning dry window
                r_prob = 10.0
                r_mm = 0.0
                wind = 7.5
                temp = 23.5
                hum = 68.0
            else:
                r_prob = 25.0
                r_mm = 0.2
                wind = 11.0
                temp = 28.0
                hum = 74.0

            forecast_points.append(
                HourlyForecastPoint(
                    time_str=future_dt.strftime("%b %d, %H:00"),
                    hour=future_dt.hour,
                    temp_c=temp,
                    humidity_pct=hum,
                    rain_prob_pct=r_prob,
                    rainfall_mm=r_mm,
                    wind_speed_kmh=wind,
                    uv_index=5.0
                )
            )

        return WeatherData(
            location_name=location_name,
            latitude=lat,
            longitude=lon,
            current_temp_c=27.5,
            current_humidity_pct=76.0,
            current_rain_prob_pct=65.0,  # High rain risk for demo!
            current_rainfall_mm=1.5,
            current_wind_speed_kmh=16.2, # High wind for demo!
            condition_text="Pre-Rain Clouds 🌧️",
            hourly_forecast=forecast_points,
            is_live=False
        )
