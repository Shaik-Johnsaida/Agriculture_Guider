"""
Location Service Module for AgriShield AI.
Resolves farmer locations via Open-Meteo Geocoding API, OpenStreetMap Nominatim,
and pre-configured agricultural hubs.
"""

from typing import Dict, Any, Optional
import requests
from config import LOCATION_PRESETS, OPEN_METEO_GEOCODING_URL


class LocationService:
    """
    Location Intelligence Service for resolving city names, GPS coordinates,
    and agricultural presets.
    """

    @staticmethod
    def get_presets() -> Dict[str, Dict[str, Any]]:
        """Returns pre-configured agricultural location hubs."""
        return LOCATION_PRESETS

    @staticmethod
    def search_location(query: str) -> Optional[Dict[str, Any]]:
        """
        Searches for location coordinates by city or region name using Open-Meteo Geocoding.
        Returns dict with keys: name, state, country, lat, lon.
        """
        if not query or len(query.strip()) < 2:
            return None

        # Check if query matches a preset key
        for preset_name, preset_data in LOCATION_PRESETS.items():
            if query.lower() in preset_name.lower():
                return preset_data

        try:
            url = f"{OPEN_METEO_GEOCODING_URL}?name={requests.utils.quote(query)}&count=1&language=en&format=json"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                if results:
                    first = results[0]
                    return {
                        "name": first.get("name", query),
                        "state": first.get("admin1", ""),
                        "country": first.get("country", "India"),
                        "lat": float(first.get("latitude")),
                        "lon": float(first.get("longitude"))
                    }
        except Exception as e:
            print(f"[WARN] Open-Meteo geocoding request failed: {e}")

        # Fallback default: Guntur, AP
        return LOCATION_PRESETS["Guntur, AP (Chili & Cotton Hub)"]

    @staticmethod
    def get_location_by_coords(lat: float, lon: float) -> Dict[str, Any]:
        """Formats location dict from raw coordinates."""
        return {
            "name": f"Coordinates ({round(lat, 4)}, {round(lon, 4)})",
            "state": "Local Farm Site",
            "country": "India",
            "lat": lat,
            "lon": lon
        }
