"""
Config module for AgriShield AI.
Contains global application constants, API endpoints, location presets,
weather decision thresholds, and complete multilingual UI dictionaries.
"""

import os

# Application Metadata
APP_NAME = "AgriShield AI"
APP_TAGLINE = "AI-Powered Crop Health & Climate Resilience Advisor"
APP_SUBTAGLINE = "Turn raw field observations into weather-aware agricultural decisions."
VERSION = "1.0.0"

# Weather API (Open-Meteo)
OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
NOMINATIM_GEOCODING_URL = "https://nominatim.openstreetmap.org/search"

# Agronomic Safety Thresholds
THRESHOLDS = {
    "RAIN_PROBABILITY_HIGH": 50.0,      # % probability of rain triggering washout warning
    "RAIN_PROBABILITY_SEVERE": 70.0,    # % rain probability blocking application completely
    "WIND_SPEED_HIGH_KMH": 15.0,        # km/h wind triggering spray drift warning
    "WIND_SPEED_SEVERE_KMH": 25.0,      # km/h wind blocking spraying completely
    "TEMP_MAX_SAFE_C": 35.0,            # °C above which chemical leaf scorch risk is high
    "TEMP_MIN_SAFE_C": 10.0,            # °C below which pesticide uptake drops severely
    "HUMIDITY_SPORULATION_HIGH": 80.0,  # % relative humidity triggering fungal outbreak risk
}

# Default Location Presets (Major Indian Agricultural Hubs)
LOCATION_PRESETS = {
    "Guntur, AP (Chili & Cotton Hub)": {"name": "Guntur", "state": "Andhra Pradesh", "country": "India", "lat": 16.3067, "lon": 80.4365},
    "Nashik, MH (Grape & Tomato Hub)": {"name": "Nashik", "state": "Maharashtra", "country": "India", "lat": 19.9975, "lon": 73.7898},
    "Warangal, TS (Cotton & Rice Hub)": {"name": "Warangal", "state": "Telangana", "country": "India", "lat": 17.9689, "lon": 79.5941},
    "Ludhiana, PB (Wheat & Paddy Hub)": {"name": "Ludhiana", "state": "Punjab", "country": "India", "lat": 30.9010, "lon": 75.8573},
    "Shimla, HP (Apple Orchard Belt)": {"name": "Shimla", "state": "Himachal Pradesh", "country": "India", "lat": 31.1048, "lon": 77.1734},
    "Patna, BR (Rice & Maize Hub)": {"name": "Patna", "state": "Bihar", "country": "India", "lat": 25.5941, "lon": 85.1376},
}

# Multilingual UI Dictionary (English, Telugu, Hindi)
UI_LANGUAGES = {
    "en": "English",
    "te": "తెలుగు (Telugu)",
    "hi": "हिंदी (Hindi)"
}

# BCP-47 Speech Synthesis Codes
SPEECH_LANG_CODES = {
    "en": "en-IN",
    "te": "te-IN",
    "hi": "hi-IN"
}

TRANSLATIONS = {
    "en": {
        "app_title": "AgriShield AI",
        "app_tagline": "AI-Powered Crop Health & Climate Resilience Advisor",
        "app_subtagline": "Turn raw field observations into weather-aware agricultural decisions.",
        "btn_analyze": "🌱 Analyze My Crop",
        "btn_reset": "🔄 Reset Analysis",
        "btn_download_pdf": "📄 Download Printable PDF Report",
        "btn_download_json": "📥 Download Raw JSON Data",
        "btn_listen_audio": "🔊 Listen to Advisory Audio",
        "nav_advisory_tab": "🛡️ Action Decision & Advisory",
        "nav_xai_tab": "🔍 Explainable AI (XAI)",
        "nav_weather_tab": "🌤️ Microclimate Forecast",
        "nav_history_tab": "📜 History & Reports",
        "lbl_step1": "🌾 Step 1: Crop Image Input",
        "lbl_step2": "📍 Step 2: Location Intelligence",
        "lbl_upload": "Upload Crop Leaf Image (JPG, PNG)",
        "lbl_sample_select": "Select Sample Crop Image:",
        "lbl_location_method": "Location Method:",
        "lbl_preset_hub": "Agricultural Hub Preset",
        "lbl_custom_search": "Custom Location Search",
        "lbl_city_input": "Enter City / Town / District:",
        "lbl_judge_demo_mode": "⚡ JUDGE DEMO MODE",
        "lbl_live_pipeline_active": "🟢 LIVE MICROCLIMATE PIPELINE ACTIVE",
        "lbl_real_model_badge": "🤖 REAL HF VISION MODEL (38 PlantVillage Classes)",
        "lbl_demo_preset_badge": "⚡ JUDGE DEMO PRESET MODE",
        "lbl_low_conf_warning": "⚠️ Low Confidence Prediction ({pct}%): The AI model detected ambiguity. Please upload a clearer photo under good natural lighting or consult local extension officers.",
        "lbl_action_timing_decision": "AGRONOMIC ACTION TIMING DECISION",
        "lbl_recommended_safe_window": "⏱️ RECOMMENDED SAFE ACTION TIME WINDOW:",
        "lbl_reason": "Reason:",
        "lbl_diagnosis_result": "AI CROP DIAGNOSIS RESULT",
        "lbl_target_crop": "Crop Species:",
        "lbl_diagnosed_condition": "Diagnosed Condition:",
        "lbl_confidence_score": "Model Softmax Probability:",
        "lbl_severity_level": "Severity Risk Level:",
        "lbl_live_weather_signals": "LIVE LOCAL CLIMATE SIGNALS",
        "lbl_temp": "Temperature",
        "lbl_humidity": "Humidity",
        "lbl_rain_risk": "Rain Risk (6h)",
        "lbl_wind_speed": "Wind Speed",
        "lbl_immediate_steps": "⚡ Immediate Action Steps",
        "lbl_organic_options": "🌿 Organic & Biological Control",
        "lbl_chemical_options": "🧪 Active Ingredients & Spray Options",
        "lbl_what_not_to_do": "⚠️ What NOT to Do",
        "lbl_preventive_measures": "🛡️ Preventive & Cultural Practices",
        "lbl_why_this_recommendation": "Why this recommendation?",
        "lbl_disclaimer": "ℹ️ Agronomic Disclaimer: AgriShield AI provides first-level decision support based on weather signals and vision modeling. Verify active ingredients, registered trade names, and local pre-harvest intervals with extension officers prior to application.",
        "status_safe": "🟢 SUITABLE TO ACT NOW",
        "status_warning": "🟡 WAIT FOR BETTER CONDITIONS",
        "status_danger": "🔴 ACTION NOT RECOMMENDED — DO NOT SPRAY",
        "voice_notice": "Speech synthesis for English initialized."
    },

    "te": {
        "app_title": "అగ్రిషీల్డ్ AI",
        "app_tagline": "AI పైరు ఆరోగ్యం మరియు వాతావరణ నివారణ సలహాదారు",
        "app_subtagline": "పొలం పరిశీలనలను వాతావరణ ఆధారిత వ్యవసాయ నిర్ణయాలుగా మార్చండి.",
        "btn_analyze": "🌱 నా పైరును విశ్లేషించు",
        "btn_reset": "🔄 విశ్లేషణను రీసెట్ చేయి",
        "btn_download_pdf": "📄 ముద్రించదగిన PDF నివేదికను డౌన్‌లోడ్ చేయండి",
        "btn_download_json": "📥 JSON డేటాను డౌన్‌లోడ్ చేయండి",
        "btn_listen_audio": "🔊 సలహాను వాయిస్‌లో వినండి",
        "nav_advisory_tab": "🛡️ చర్య నిర్ణయం మరియు సలహా",
        "nav_xai_tab": "🔍 వివరణాత్మక AI (XAI)",
        "nav_weather_tab": "🌤️ స్థానిక వాతావరణ సూచన",
        "nav_history_tab": "📜 చరిత్ర మరియు నివేదికలు",
        "lbl_step1": "🌾 దశ 1: పైరు ఆకు చిత్రం",
        "lbl_step2": "📍 దశ 2: ప్రాంత వివరాలు",
        "lbl_upload": "ఆకు చిత్రాన్ని అప్‌లోడ్ చేయండి (JPG, PNG)",
        "lbl_sample_select": "సాంపిల్ ఆకు చిత్రాన్ని ఎంచుకోండి:",
        "lbl_location_method": "ప్రాంతం ఎంపిక విధానం:",
        "lbl_preset_hub": "ముఖ్య వ్యవసాయ ప్రాంతం",
        "lbl_custom_search": "ఊరు / పట్టణం వెతకండి",
        "lbl_city_input": "మీ ఊరు/జిల్లా పేరు నమోదు చేయండి:",
        "lbl_judge_demo_mode": "⚡ డెమో మోడ్ (డెమో చిత్రాలు)",
        "lbl_live_pipeline_active": "🟢 ప్రత్యక్ష వాతావరణ వ్యవస్థ ప్రారంభమైంది",
        "lbl_real_model_badge": "🤖 నిజమైన HF విజన్ మోడల్ (38 రకాల పైరు వ్యాధులు)",
        "lbl_demo_preset_badge": "⚡ జడ్జ్ డెమో మోడ్",
        "lbl_low_conf_warning": "⚠️ తక్కువ స్పష్టత నివేదిక ({pct}%): ఆకు చిత్రం స్పష్టంగా లేదు. మంచి వెలుతురులో మరొక చిత్రం తీసి అప్‌లోడ్ చేయండి లేదా స్థానిక వ్యవసాయ అధికారిని సంప్రదించండి.",
        "lbl_action_timing_decision": "వ్యవసాయ మందుల పిచికారీ సమయ నిర్ణయం",
        "lbl_recommended_safe_window": "⏱️ సిఫార్సు చేయబడిన సురక్షిత సమయం:",
        "lbl_reason": "కారణం:",
        "lbl_diagnosis_result": "AI పైరు వ్యాధి నిర్ధారణ నివేదిక",
        "lbl_target_crop": "పైరు రకం:",
        "lbl_diagnosed_condition": "నిర్ధారించిన వ్యాధి:",
        "lbl_confidence_score": "AI ఖచ్చితత్వ శాతం:",
        "lbl_severity_level": "తీవ్రత స్థాయి:",
        "lbl_live_weather_signals": "ప్రస్తుత స్థానిక వాతావరణ వివరాలు",
        "lbl_temp": "ఉష్ణోగ్రత",
        "lbl_humidity": "గాలిలో తేమ",
        "lbl_rain_risk": "వర్ష సూచన (6 గంటలు)",
        "lbl_wind_speed": "గాలి వేగం",
        "lbl_immediate_steps": "⚡ తక్షణ నివారణ చర్యలు",
        "lbl_organic_options": "🌿 సేంద్రీయ మరియు జైవిక నివారణ",
        "lbl_chemical_options": "🧪 రసాయన మందులు మరియు మోతాదు సూచనలు",
        "lbl_what_not_to_do": "⚠️ ఏమి చేయకూడదు",
        "lbl_preventive_measures": "🛡️ భవిష్యత్తు ముందస్తు జాగ్రత్తలు",
        "lbl_why_this_recommendation": "ఈ సిఫార్సుకు కారణం ఏమిటి?",
        "lbl_disclaimer": "ℹ️ గమనిక: ఈ AI సలహా వాతావరణం మరియు ఆకు చిత్ర విశ్లేషణ ఆధారంగా ఇవ్వబడింది. మందులు పిచికారీ చేసే ముందు స్థానిక వ్యవసాయ అధికారుల సలహా తీసుకోండి.",
        "status_safe": "🟢 ఇప్పుడు మందులు పిచికారీ చేయడానికి అనుకూలం",
        "status_warning": "🟡 మెరుగైన వాతావరణం కోసం వేచి ఉండండి",
        "status_danger": "🔴 ఇప్పుడు పిచికారీ చేయడం తగదు — వాతావరణ ప్రమాదం",
        "voice_notice": "తెలుగు వాయిస్ అసిస్టెంట్ సిద్ధంగా ఉంది."
    },

    "hi": {
        "app_title": "एग्रीशील्ड AI",
        "app_tagline": "AI-संचालित फसल स्वास्थ्य और मौसम सलाहकार",
        "app_subtagline": "खेत के अवलोकनों को मौसम-जागरूक कृषि निर्णयों में बदलें।",
        "btn_analyze": "🌱 मेरी फसल का विश्लेषण करें",
        "btn_reset": "🔄 विश्लेषण रीसेट करें",
        "btn_download_pdf": "📄 प्रिंट करने योग्य पीडीएफ रिपोर्ट डाउनलोड करें",
        "btn_download_json": "📥 कच्चा JSON डेटा डाउनलोड करें",
        "btn_listen_audio": "🔊 सलाह ऑडियो सुनें",
        "nav_advisory_tab": "🛡️ कार्रवाई निर्णय और सलाह",
        "nav_xai_tab": "🔍 व्याख्यात्मक AI (XAI)",
        "nav_weather_tab": "🌤️ स्थानीय मौसम पूर्वानुमान",
        "nav_history_tab": "📜 इतिहास और रिपोर्ट",
        "lbl_step1": "🌾 चरण 1: फसल पत्ती छवि",
        "lbl_step2": "📍 चरण 2: स्थान बुद्धिमत्ता",
        "lbl_upload": "पत्ती की छवि अपलोड करें (JPG, PNG)",
        "lbl_sample_select": "नमूना पत्ती चित्र चुनें:",
        "lbl_location_method": "स्थान चयन विधि:",
        "lbl_preset_hub": "प्रमुख कृषि क्षेत्र",
        "lbl_custom_search": "शहर / स्थान खोजें",
        "lbl_city_input": "अपना शहर/जिला दर्ज करें:",
        "lbl_judge_demo_mode": "⚡ जज डेमो मोड",
        "lbl_live_pipeline_active": "🟢 लाइव मौसम पाइपलाइन सक्रिय",
        "lbl_real_model_badge": "🤖 वास्तविक HF विजन मॉडल (38 फसल रोग)",
        "lbl_demo_preset_badge": "⚡ जज डेमो मोड",
        "lbl_low_conf_warning": "⚠️ कम विश्वास भविष्यवाणी ({pct}%): छवि स्पष्ट नहीं है। कृपया प्राकृतिक रोशनी में बेहतर फोटो अपलोड करें या स्थानीय कृषि विशेषज्ञ से संपर्क करें।",
        "lbl_action_timing_decision": "कृषि स्प्रे समय निर्णय",
        "lbl_recommended_safe_window": "⏱️ अनुशंसित सुरक्षित समय खिड़की:",
        "lbl_reason": "कारण:",
        "lbl_diagnosis_result": "AI फसल रोग निदान परिणाम",
        "lbl_target_crop": "फसल का प्रकार:",
        "lbl_diagnosed_condition": "पहचाना गया रोग:",
        "lbl_confidence_score": "मॉडल सटीकता प्रतिशत:",
        "lbl_severity_level": "गंभीरता का स्तर:",
        "lbl_live_weather_signals": "लाइव स्थानीय मौसम संकेत",
        "lbl_temp": "तापमान",
        "lbl_humidity": "आर्द्रता",
        "lbl_rain_risk": "वर्षा जोखिम (6 घंटे)",
        "lbl_wind_speed": "हवा की गति",
        "lbl_immediate_steps": "⚡ तत्काल कार्रवाई चरण",
        "lbl_organic_options": "🌿 जैविक और प्राकृतिक नियंत्रण",
        "lbl_chemical_options": "🧪 रसायनिक स्प्रे और सावधानियां",
        "lbl_what_not_to_do": "⚠️ क्या न करें",
        "lbl_preventive_measures": "🛡️ भविष्य के निवारक उपाय",
        "lbl_why_this_recommendation": "इस सिफारिश का कारण क्या है?",
        "lbl_disclaimer": "ℹ️ कृषि अस्वीकरण: एग्रीशील्ड AI मौसम संकेतों और विजन मॉडलिंग पर आधारित सलाह प्रदान करता है। छिड़काव से पहले हमेशा उत्पाद लेबल और स्थानीय विशेषज्ञों से पुष्टि करें।",
        "status_safe": "🟢 अभी दवा छिड़कना उपयुक्त है",
        "status_warning": "🟡 बेहतर मौसम की प्रतीक्षा करें",
        "status_danger": "🔴 अभी दवा न छिड़कें — मौसम जोखिम",
        "voice_notice": "हिंदी वॉइस असिस्टेंट तैयार है।"
    }
}
