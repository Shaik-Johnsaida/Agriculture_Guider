"""
Unit Test Suite for AgriShield AI Core Pipeline.
Tests HuggingFace disease model, weather service, decision engine,
multilingual advisory generator, and localized ReportLab PDF generator (English, Telugu, Hindi).
"""

import sys
import os
import unittest
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.disease_classifier import DiseaseClassifier, CropDiagnosis
from core.explainability import XAIExplainer
from core.location_service import LocationService
from core.weather_service import WeatherService, WeatherData, HourlyForecastPoint
from core.decision_engine import WeatherDecisionEngine, SafeActionWindow
from core.advisory_generator import AdvisoryGenerator
from core.pdf_generator import PDFReportGenerator


class TestAgriShieldPipeline(unittest.TestCase):

    def setUp(self):
        self.classifier = DiseaseClassifier()
        self.test_img = Image.new("RGB", (224, 224), color=(40, 150, 40))

    def test_disease_classifier(self):
        diagnosis = self.classifier.analyze_image(self.test_img, filename_hint="tomato_late_blight.png")
        self.assertIsInstance(diagnosis, CropDiagnosis)
        self.assertIsInstance(diagnosis.confidence, float)
        self.assertGreaterEqual(diagnosis.confidence, 0.0)
        self.assertLessEqual(diagnosis.confidence, 1.0)

    def test_explainability(self):
        heatmap_pil, side_by_side_pil = XAIExplainer.generate_gradcam(self.test_img, model=self.classifier.model)
        self.assertIsNotNone(heatmap_pil)
        self.assertIsNotNone(side_by_side_pil)
        self.assertEqual(heatmap_pil.size, self.test_img.size)

    def test_location_service(self):
        presets = LocationService.get_presets()
        self.assertIn("Guntur, AP (Chili & Cotton Hub)", presets)
        guntur = presets["Guntur, AP (Chili & Cotton Hub)"]
        self.assertEqual(guntur["lat"], 16.3067)

    def test_weather_fallback(self):
        weather = WeatherService.get_weather(lat=16.3067, lon=80.4365, location_name="Guntur")
        self.assertIsInstance(weather, WeatherData)
        self.assertGreater(len(weather.hourly_forecast), 10)
        self.assertIsInstance(weather.current_temp_c, float)

    def test_decision_engine_high_rain_warning(self):
        mock_forecast = [
            HourlyForecastPoint(time_str="Aug 11, 14:00", hour=14, temp_c=28.0, humidity_pct=85.0, rain_prob_pct=75.0, rainfall_mm=2.5, wind_speed_kmh=10.0, uv_index=4.0),
            HourlyForecastPoint(time_str="Aug 11, 15:00", hour=15, temp_c=27.0, humidity_pct=88.0, rain_prob_pct=80.0, rainfall_mm=3.0, wind_speed_kmh=12.0, uv_index=3.0),
            HourlyForecastPoint(time_str="Aug 12, 07:00", hour=7, temp_c=22.0, humidity_pct=65.0, rain_prob_pct=5.0, rainfall_mm=0.0, wind_speed_kmh=6.0, uv_index=2.0),
            HourlyForecastPoint(time_str="Aug 12, 08:00", hour=8, temp_c=23.0, humidity_pct=62.0, rain_prob_pct=5.0, rainfall_mm=0.0, wind_speed_kmh=6.5, uv_index=3.0),
            HourlyForecastPoint(time_str="Aug 12, 09:00", hour=9, temp_c=24.0, humidity_pct=60.0, rain_prob_pct=5.0, rainfall_mm=0.0, wind_speed_kmh=7.0, uv_index=4.0),
        ]
        mock_weather = WeatherData(
            location_name="Test Site",
            latitude=16.3,
            longitude=80.4,
            current_temp_c=28.0,
            current_humidity_pct=85.0,
            current_rain_prob_pct=75.0,
            current_rainfall_mm=2.5,
            current_wind_speed_kmh=10.0,
            condition_text="Rain Imminent",
            hourly_forecast=mock_forecast,
            is_live=True
        )

        diagnosis = self.classifier.analyze_image(self.test_img, force_demo_id="tomato_late_blight")
        safety_window = WeatherDecisionEngine.evaluate_action_safety(diagnosis, mock_weather)

        self.assertFalse(safety_window.is_safe_now)
        self.assertIn(safety_window.status_code, ["WARNING", "DANGER"])

    def test_localized_pdf_generator(self):
        diag_data = {"crop": "Tomato", "disease_name": "Late Blight", "confidence": 0.91, "severity": "Severe"}
        weath_data = {"location_name": "Guntur", "current_temp_c": 27.5, "current_humidity_pct": 76.0, "current_rain_prob_pct": 65.0, "current_wind_speed_kmh": 16.2}
        dec_data = {"status_label": "⚠️ ACTION NOT RECOMMENDED", "status_color": "#EF6C00", "primary_reason": "High rain risk", "recommended_window": "Tomorrow 07:00 AM - 11:00 AM"}
        kb = {"immediate_actions": ["Prune leaves"], "organic_treatment": ["Neem oil"], "chemical_treatment": ["Mancozeb"], "what_not_to_do": ["Do not spray in rain"]}

        # Test English PDF
        pdf_en = PDFReportGenerator.generate_pdf_report(diag_data, weath_data, dec_data, kb, lang="en")
        self.assertGreater(len(pdf_en), 1000)

        # Test Telugu PDF
        pdf_te = PDFReportGenerator.generate_pdf_report(diag_data, weath_data, dec_data, kb, lang="te")
        self.assertGreater(len(pdf_te), 1000)

        # Test Hindi PDF
        pdf_hi = PDFReportGenerator.generate_pdf_report(diag_data, weath_data, dec_data, kb, lang="hi")
        self.assertGreater(len(pdf_hi), 1000)


if __name__ == "__main__":
    unittest.main()
