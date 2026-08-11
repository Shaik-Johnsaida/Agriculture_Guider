"""
Advisory Generator Module for AgriShield AI.
Formats structured diagnosis + weather intelligence + safe action timing
into a simple, multi-section, multilingual farmer advisory with native TTS speech script generation.
"""

from typing import Dict, Any
from config import TRANSLATIONS, SPEECH_LANG_CODES
from core.disease_classifier import CropDiagnosis
from core.weather_service import WeatherData
from core.decision_engine import SafeActionWindow


class AdvisoryGenerator:
    """
    Generates actionable, farmer-friendly advisories with complete multilingual support
    and native text-to-speech audio script generation.
    """

    @staticmethod
    def generate_advisory(
        diagnosis: CropDiagnosis,
        weather: WeatherData,
        safety_window: SafeActionWindow,
        lang: str = "en"
    ) -> Dict[str, Any]:
        """
        Builds structured advisory dictionary formatted in target language.
        """
        t = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
        bcp47_code = SPEECH_LANG_CODES.get(lang, "en-IN")

        conf_pct = int(diagnosis.confidence * 100)

        # Dynamic Status Translation
        if safety_window.status_code == "SAFE":
            status_trans = t["status_safe"]
        elif safety_window.status_code == "WARNING":
            status_trans = t["status_warning"]
        else:
            status_trans = t["status_danger"]

        # Native Spoken Audio Scripts
        if lang == "te":
            headline = f"పైరు: {diagnosis.crop} | వ్యాధి: {diagnosis.disease_name}"
            timing_advice = f"ప్రస్తుత సూచన: {status_trans}. {safety_window.primary_reason}"
            speech_text = (
                f"అగ్రిషీల్డ్ సలహా. పైరు {diagnosis.crop}. "
                f"నిర్ధారించబడిన వ్యాధి {diagnosis.disease_name}, ఖచ్చితత్వం {conf_pct} శాతం. "
                f"ప్రస్తుత సూచన: {status_trans}. "
                f"కారణం: {safety_window.primary_reason}. "
                f"సిఫార్సు చేయబడిన సురక్షిత సమయం: {safety_window.recommended_window}."
            )
        elif lang == "hi":
            headline = f"फसल: {diagnosis.crop} | बीमारी: {diagnosis.disease_name}"
            timing_advice = f"वर्तमान सलाह: {status_trans}। {safety_window.primary_reason}"
            speech_text = (
                f"एग्रीशील्ड सलाह। फसल {diagnosis.crop}। "
                f"पहचाना गया रोग {diagnosis.disease_name}, सटीकता {conf_pct} प्रतिशत। "
                f"वर्तमान सलाह: {status_trans}। "
                f"कारण: {safety_window.primary_reason}। "
                f"अनुशंसित सुरक्षित समय: {safety_window.recommended_window}।"
            )
        else:
            headline = f"Crop: {diagnosis.crop} | Diagnosis: {diagnosis.disease_name}"
            timing_advice = f"Action Status: {status_trans}. {safety_window.primary_reason}"
            speech_text = (
                f"AgriShield Advisory for {diagnosis.crop}. "
                f"Detected condition is {diagnosis.disease_name} with {conf_pct} percent confidence. "
                f"Current status is: {status_trans}. {safety_window.primary_reason} "
                f"Recommended safe spraying window: {safety_window.recommended_window}."
            )

        return {
            "headline": headline,
            "timing_advice": timing_advice,
            "speech_text": speech_text,
            "bcp47_code": bcp47_code,
            "lang": lang,
            "labels": t
        }
