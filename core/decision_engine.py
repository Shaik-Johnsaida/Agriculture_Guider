"""
Agronomic Decision Engine Module for AgriShield AI.
Combines crop diagnosis with real-time microclimate signals to answer:
"Is it safe to act now?" and calculates the optimal Safe Action Window.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from config import THRESHOLDS
from core.disease_classifier import CropDiagnosis
from core.weather_service import WeatherData, HourlyForecastPoint


@dataclass
class SafeActionWindow:
    is_safe_now: bool
    status_code: str             # "SAFE", "WARNING", "DANGER"
    status_label: str            # e.g., "🟢 SAFE TO ACT NOW"
    status_color: str            # Hex code
    primary_reason: str          # Agronomic explanation why
    recommended_window: str      # e.g., "Tomorrow 07:00 AM – 11:00 AM"
    window_start_time: str
    window_end_time: str
    risk_factors: List[str]      # Active hazards (Washout, Wind Drift, Heat Scorch, etc.)
    spraying_safety_score: int   # 0 to 100 safety score index


class WeatherDecisionEngine:
    """
    Deterministic Agronomic Weather Decision Engine.
    Enforces physics-based and agricultural safety thresholds for crop spraying.
    """

    @staticmethod
    def evaluate_action_safety(diagnosis: CropDiagnosis, weather: WeatherData) -> SafeActionWindow:
        """
        Evaluates current microclimate safety for crop treatment and calculates
        the next optimal safe action window from hourly forecast data.
        """
        risk_factors = []
        is_safe_now = True
        status_code = "SAFE"
        
        # 1. Rain Washout Risk (Next 6 hours check)
        rain_risk_6h = False
        max_rain_prob_6h = weather.current_rain_prob_pct
        for point in weather.hourly_forecast[:6]:
            if point.rain_prob_pct > max_rain_prob_6h:
                max_rain_prob_6h = point.rain_prob_pct
            if point.rain_prob_pct >= THRESHOLDS["RAIN_PROBABILITY_HIGH"] or point.rainfall_mm > 0.5:
                rain_risk_6h = True

        if rain_risk_6h:
            is_safe_now = False
            risk_factors.append(f"🌧️ Washout Hazard: Rain probability reaches {int(max_rain_prob_6h)}% within 6 hours. Chemical spray will wash off.")

        # 2. Wind Drift Risk
        if weather.current_wind_speed_kmh >= THRESHOLDS["WIND_SPEED_HIGH_KMH"]:
            is_safe_now = False
            risk_factors.append(f"💨 Spray Drift Hazard: Wind speed is {round(weather.current_wind_speed_kmh, 1)} km/h (Limit: 15 km/h). Spraying will cause drift off-target.")

        # 3. High Temperature Scorch Risk
        if weather.current_temp_c >= THRESHOLDS["TEMP_MAX_SAFE_C"]:
            is_safe_now = False
            risk_factors.append(f"🌡️ Heat Scorch Hazard: Temperature is {round(weather.current_temp_c, 1)}°C. High evaporation risks crop foliage burn.")

        # 4. Fungal Sporulation Humidity Risk (Warning context)
        if weather.current_humidity_pct >= THRESHOLDS["HUMIDITY_SPORULATION_HIGH"] and 20 <= weather.current_temp_c <= 30:
            risk_factors.append(f"💧 High Humidity Outbreak Risk: Relative humidity ({int(weather.current_humidity_pct)}%) accelerates spore germination.")

        # If condition is healthy leaf, spraying is not needed
        if diagnosis.disease_id == "healthy_leaf":
            return SafeActionWindow(
                is_safe_now=True,
                status_code="SAFE",
                status_label="🟢 NO CHEMICAL SPRAY REQUIRED",
                status_color="#2E7D32",
                primary_reason="Crop is currently healthy. Maintain regular irrigation and preventative monitoring.",
                recommended_window="Routine Monitoring",
                window_start_time="Immediate",
                window_end_time="Ongoing",
                risk_factors=["✅ Foliage intact with no active pathogen pressure."],
                spraying_safety_score=100
            )

        # Determine overall status code & label
        if not is_safe_now:
            if max_rain_prob_6h >= THRESHOLDS["RAIN_PROBABILITY_SEVERE"] or weather.current_wind_speed_kmh >= THRESHOLDS["WIND_SPEED_SEVERE_KMH"]:
                status_code = "DANGER"
                status_label = "⛔ DANGEROUS — DO NOT SPRAY NOW"
                status_color = "#C62828"
                primary_reason = f"Imminent rain ({int(max_rain_prob_6h)}%) and high wind speed ({round(weather.current_wind_speed_kmh, 1)} km/h) will waste chemicals and damage surrounding crops."
            else:
                status_code = "WARNING"
                status_label = "⚠️ ACTION NOT RECOMMENDED — WAIT FOR DRY WINDOW"
                status_color = "#EF6C00"
                primary_reason = f"Current weather presents risks (Rain prob: {int(max_rain_prob_6h)}%, Wind: {round(weather.current_wind_speed_kmh, 1)} km/h). Wait for the recommended window."
        else:
            status_code = "SAFE"
            status_label = "🟢 SAFE TO ACT NOW"
            status_color = "#2E7D32"
            primary_reason = "Current weather conditions are dry, with low wind speed and mild temperature suitable for immediate treatment application."

        # Calculate Next Safe Action Window from Hourly Forecast
        safe_window_str, win_start, win_end = WeatherDecisionEngine._calculate_next_dry_window(weather.hourly_forecast)

        # Calculate Spraying Safety Score (0-100)
        safety_score = WeatherDecisionEngine._compute_safety_score(weather)

        return SafeActionWindow(
            is_safe_now=is_safe_now,
            status_code=status_code,
            status_label=status_label,
            status_color=status_color,
            primary_reason=primary_reason,
            recommended_window=safe_window_str,
            window_start_time=win_start,
            window_end_time=win_end,
            risk_factors=risk_factors if risk_factors else ["✅ Weather parameters are within optimal agronomic thresholds."],
            spraying_safety_score=safety_score
        )

    @staticmethod
    def _calculate_next_dry_window(forecast: List[HourlyForecastPoint]) -> tuple:
        """Scans forecast points to pinpoint next optimal 3-4 hour dry window."""
        if not forecast:
            return "Tomorrow morning: 07:00 AM – 10:00 AM", "07:00", "10:00"

        best_start = None
        best_count = 0

        # Scan for contiguous daylight hours (06:00 to 18:00) where rain prob < 25% and wind < 14 km/h
        for i, pt in enumerate(forecast):
            if 6 <= pt.hour <= 18 and pt.rain_prob_pct < 25.0 and pt.wind_speed_kmh < 14.0 and 15.0 <= pt.temp_c <= 32.0:
                if best_start is None:
                    best_start = pt
                    best_count = 1
                else:
                    best_count += 1
                    if best_count >= 3:
                        end_pt = pt
                        start_time = best_start.time_str
                        end_time = end_pt.time_str
                        window_desc = f"{start_time} to {end_time.split(',')[-1].strip()} (Low wind: {round(best_start.wind_speed_kmh, 1)} km/h, Rain risk: {int(best_start.rain_prob_pct)}%)"
                        return window_desc, start_time, end_time
            else:
                best_start = None
                best_count = 0

        # Default fallback window if no perfect window found in 48h
        pt_f = forecast[min(18, len(forecast)-1)]
        return f"{pt_f.time_str} (Predicted dry interval)", pt_f.time_str, "End of slot"

    @staticmethod
    def _compute_safety_score(weather: WeatherData) -> int:
        """Computes a 0 to 100 Spraying Safety Index."""
        score = 100
        # Deduct for rain
        score -= min(50, int(weather.current_rain_prob_pct * 0.7))
        # Deduct for wind
        if weather.current_wind_speed_kmh > 10:
            score -= min(30, int((weather.current_wind_speed_kmh - 10) * 2.5))
        # Deduct for extreme temp
        if weather.current_temp_c > 32:
            score -= int((weather.current_temp_c - 32) * 5)
        return max(5, min(100, score))
