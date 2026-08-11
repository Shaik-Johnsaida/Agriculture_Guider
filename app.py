"""
AgriShield AI — Main Streamlit Web Application
AI-Powered Crop Health & Climate Resilience Advisor for Hack2Skill Hackathon.
Fully Multilingual (English, Telugu, Hindi) with State Persistence, Localized PDF Export, and Robust Browser TTS Audio.
"""

import json
import os
import time
import datetime
from PIL import Image
import numpy as np
import streamlit as st

from config import (
    APP_NAME, APP_TAGLINE, APP_SUBTAGLINE, VERSION,
    UI_LANGUAGES, SPEECH_LANG_CODES, TRANSLATIONS, LOCATION_PRESETS
)
from core.disease_classifier import DiseaseClassifier
from core.explainability import XAIExplainer
from core.location_service import LocationService
from core.weather_service import WeatherService
from core.decision_engine import WeatherDecisionEngine
from core.advisory_generator import AdvisoryGenerator
from core.pdf_generator import PDFReportGenerator


# Streamlit Page Setup
st.set_page_config(
    page_title="AgriShield AI — Crop Health & Climate Advisor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS Styling
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Initialize Core AI & Data Services (Cached)
@st.cache_resource
def get_classifier():
    return DiseaseClassifier()

classifier = get_classifier()

# Session State Setup for Persistent Analysis & History
if "history" not in st.session_state:
    st.session_state.history = []

if "current_analysis" not in st.session_state:
    st.session_state.current_analysis = None

if "selected_lang" not in st.session_state:
    st.session_state.selected_lang = "en"


# --- TOP NAVIGATION & BRANDING BANNER ---
st.markdown("""
<div class="glass-card glass-card-accent" style="padding: 20px; margin-bottom: 15px;">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
        <div>
            <div class="brand-title">🛡️ AgriShield AI</div>
            <div class="brand-tagline">AI-Powered Crop Health & Climate Resilience Advisor</div>
            <div class="brand-subtagline">Turn raw field observations into weather-aware agricultural decisions.</div>
        </div>
        <div>
            <span style="background: rgba(46, 125, 50, 0.35); border: 1px solid #4CAF50; color: #81C784; padding: 8px 16px; border-radius: 20px; font-weight: 700; font-size: 0.85rem;">
                🟢 LIVE MICROCLIMATE PIPELINE ACTIVE
            </span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Top Control Strip (Language Selector & Demo Mode Toggle)
col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2.5, 2.5, 4])

with col_ctrl1:
    selected_lang_code = st.selectbox(
        "🌐 Language / భాష / भाषा",
        options=["en", "te", "hi"],
        format_func=lambda x: UI_LANGUAGES[x],
        index=["en", "te", "hi"].index(st.session_state.selected_lang)
    )
    st.session_state.selected_lang = selected_lang_code

t = TRANSLATIONS[selected_lang_code]
speech_bcp47 = SPEECH_LANG_CODES[selected_lang_code]

with col_ctrl2:
    demo_mode = st.toggle(f"⚡ {t['lbl_judge_demo_mode']}", value=True)

with col_ctrl3:
    st.caption(f"_{t['app_subtagline']}_")


# --- SIDEBAR: FIELD CROP & LOCATION INPUTS ---
st.sidebar.markdown(f"### {t['lbl_step1']}")

uploaded_file = None
force_demo_id = ""
filename_hint = ""
input_image = None

sample_mapping = {
    "Tomato Late Blight (Phytophthora)": ("tomato_late_blight.png", "tomato_late_blight"),
    "Rice Brown Spot (Bipolaris)": ("rice_brown_spot.png", "rice_brown_spot"),
    "Cotton Leaf Curl Virus (CLCuV)": ("cotton_leaf_curl.png", "cotton_leaf_curl"),
    "Corn Common Rust (Puccinia)": ("corn_common_rust.png", "corn_common_rust"),
    "Healthy Tomato Foliage": ("healthy_leaf.png", "healthy_leaf"),
}

if demo_mode:
    st.sidebar.info(f"💡 **Demo Mode**: {t['lbl_sample_select']}")
    selected_sample_label = st.sidebar.selectbox(t["lbl_sample_select"], list(sample_mapping.keys()))
    sample_filename, force_demo_id = sample_mapping[selected_sample_label]
    sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_images", sample_filename)
    
    if os.path.exists(sample_path):
        input_image = Image.open(sample_path)
        filename_hint = sample_filename
else:
    uploaded_file = st.sidebar.file_uploader(
        t["lbl_upload"],
        type=["jpg", "jpeg", "png"],
        help="Upload a clear photo of the affected crop leaf."
    )
    if uploaded_file is not None:
        input_image = Image.open(uploaded_file)
        filename_hint = uploaded_file.name

# Sidebar Image Preview
if input_image is not None:
    st.sidebar.image(input_image, caption="Field Observation Photo", use_container_width=True)
else:
    st.sidebar.warning("Please upload a leaf image or select a sample image above.")

st.sidebar.markdown("---")
st.sidebar.markdown(f"### {t['lbl_step2']}")

location_mode = st.sidebar.radio(
    t["lbl_location_method"],
    [t["lbl_preset_hub"], t["lbl_custom_search"]],
    index=0
)

selected_location_info = None

if location_mode == t["lbl_preset_hub"]:
    preset_choice = st.sidebar.selectbox("Select Agricultural Hub:", list(LOCATION_PRESETS.keys()))
    selected_location_info = LOCATION_PRESETS[preset_choice]
else:
    city_query = st.sidebar.text_input(t["lbl_city_input"], value="Guntur")
    if city_query:
        selected_location_info = LocationService.search_location(city_query)

if selected_location_info:
    st.sidebar.success(
        f"📍 **{selected_location_info['name']}**, {selected_location_info.get('state', '')}\n"
        f"Lat: `{round(selected_location_info['lat'], 4)}` | Lon: `{round(selected_location_info['lon'], 4)}`"
    )

st.sidebar.markdown("---")
col_sb_btn1, col_sb_btn2 = st.sidebar.columns(2)
with col_sb_btn1:
    analyze_clicked = st.button(t["btn_analyze"], use_container_width=True, type="primary")
with col_sb_btn2:
    reset_clicked = st.button(t["btn_reset"], use_container_width=True)

if reset_clicked:
    st.session_state.current_analysis = None
    st.rerun()


# --- TRIGGER PIPELINE ANALYSIS ---
if analyze_clicked and input_image is not None and selected_location_info is not None:
    t_start = time.time()

    # 1. Execute AI Crop Diagnosis
    diagnosis = classifier.analyze_image(
        input_image,
        filename_hint=filename_hint,
        force_demo_id=force_demo_id if demo_mode else ""
    )

    # 2. Generate Genuine PyTorch Grad-CAM Heatmap
    heatmap_pil, side_by_side_pil = XAIExplainer.generate_gradcam(input_image, model=classifier.model)
    xai_markdown = XAIExplainer.get_evidence_breakdown(diagnosis)

    # 3. Fetch Live Local Microclimate Weather Intelligence
    t_weather_start = time.time()
    weather = WeatherService.get_weather(
        lat=selected_location_info["lat"],
        lon=selected_location_info["lon"],
        location_name=selected_location_info["name"]
    )
    weather_ms = round((time.time() - t_weather_start) * 1000, 1)

    # 4. Execute Agronomic Weather Decision Engine
    safety_window = WeatherDecisionEngine.evaluate_action_safety(diagnosis, weather)
    total_latency_ms = round((time.time() - t_start) * 1000, 1)

    # Save Analysis State into Session State so changing language does NOT reset results!
    st.session_state.current_analysis = {
        "diagnosis": diagnosis,
        "weather": weather,
        "safety_window": safety_window,
        "input_image": input_image,
        "heatmap_pil": heatmap_pil,
        "side_by_side_pil": side_by_side_pil,
        "xai_markdown": xai_markdown,
        "weather_ms": weather_ms,
        "total_latency_ms": total_latency_ms,
        "selected_location_info": selected_location_info
    }

    # Save to Session History Log
    history_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "crop": diagnosis.crop,
        "disease": diagnosis.disease_name,
        "location": weather.location_name,
        "status": safety_window.status_code,
        "window": safety_window.recommended_window
    }
    if not any(h["disease"] == history_entry["disease"] and h["timestamp"] == history_entry["timestamp"] for h in st.session_state.history):
        st.session_state.history.append(history_entry)


# --- RENDER DASHBOARD RESULTS FROM SESSION STATE ---
if st.session_state.current_analysis is not None:
    analysis = st.session_state.current_analysis
    diagnosis = analysis["diagnosis"]
    weather = analysis["weather"]
    safety_window = analysis["safety_window"]
    input_image = analysis["input_image"]
    heatmap_pil = analysis["heatmap_pil"]
    side_by_side_pil = analysis["side_by_side_pil"]
    xai_markdown = analysis["xai_markdown"]
    weather_ms = analysis["weather_ms"]
    total_latency_ms = analysis["total_latency_ms"]

    # Re-generate advisory data in current language dynamically!
    advisory_data = AdvisoryGenerator.generate_advisory(
        diagnosis=diagnosis,
        weather=weather,
        safety_window=safety_window,
        lang=selected_lang_code
    )

    # Determine Translated Status Badge & Text
    if safety_window.status_code == "SAFE":
        status_badge_html = f'<span class="badge-safe">{t["status_safe"]}</span>'
    elif safety_window.status_code == "WARNING":
        status_badge_html = f'<span class="badge-warning">{t["status_warning"]}</span>'
    else:
        status_badge_html = f'<span class="badge-danger">{t["status_danger"]}</span>'

    # Render Main Workspace Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        t["nav_advisory_tab"],
        t["nav_xai_tab"],
        t["nav_weather_tab"],
        t["nav_history_tab"]
    ])

    # =========================================================
    # TAB 1: ACTION DECISION & ADVISORY (PRIORITY #1 TO #5)
    # =========================================================
    with tab1:
        
        # ----------------------------------------------------
        # PRIORITY #1: AGRONOMIC ACTION TIMING DECISION (TOP BANNER)
        # ----------------------------------------------------
        st.markdown(f"""
        <div class="glass-card" style="border-left: 8px solid {safety_window.status_color};">
            <div style="font-size: 0.85rem; color: #94A3B8; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">{t["lbl_action_timing_decision"]}</div>
            <div style="margin-top: 10px; margin-bottom: 14px;">
                {status_badge_html}
            </div>
            <p style="font-size: 1.15rem; color: #E2E8F0; margin-bottom: 16px; leading: 1.5;">
                <strong>{t["lbl_reason"]}</strong> {safety_window.primary_reason}
            </p>
            <div style="background: rgba(0, 0, 0, 0.35); padding: 18px; border-radius: 12px; border: 1px dashed rgba(255, 255, 255, 0.2);">
                <div style="font-size: 0.9rem; color: #81C784; font-weight: 700; text-transform: uppercase;">{t["lbl_recommended_safe_window"]}</div>
                <div style="font-size: 1.5rem; font-weight: 800; color: #FFFFFF; margin-top: 4px;">{safety_window.recommended_window}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ----------------------------------------------------
        # PRIORITY #2: AI CROP DIAGNOSIS CARD
        # ----------------------------------------------------
        if diagnosis.inference_source == "REAL_MODEL_INFERENCE":
            source_badge = f'<span style="background: rgba(33, 150, 243, 0.2); border: 1px solid #2196F3; color: #64B5F6; padding: 4px 12px; border-radius: 12px; font-weight: 700; font-size: 0.8rem;">{t["lbl_real_model_badge"]}</span>'
        else:
            source_badge = f'<span style="background: rgba(255, 152, 0, 0.2); border: 1px solid #FF9800; color: #FFB74D; padding: 4px 12px; border-radius: 12px; font-weight: 700; font-size: 0.8rem;">{t["lbl_demo_preset_badge"]}</span>'

        if diagnosis.is_low_confidence:
            st.warning(t["lbl_low_conf_warning"].format(pct=int(diagnosis.confidence * 100)))

        st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
                <div>
                    <span style="color: #81C784; font-size: 0.85rem; text-transform: uppercase; font-weight: 700;">{t["lbl_diagnosis_result"]}</span>
                    <h2 style="margin: 4px 0; color: #FFFFFF; font-size: 1.8rem;">{diagnosis.disease_name}</h2>
                    <div style="font-size: 1rem; color: #94A3B8;">{t["lbl_target_crop"]} <strong style="color: #E2E8F0;">{diagnosis.crop}</strong> | {source_badge}</div>
                </div>
                <div style="text-align: right; margin-top: 5px;">
                    <div style="font-size: 0.85rem; color: #94A3B8;">{t["lbl_confidence_score"]}</div>
                    <div style="font-size: 2.2rem; font-weight: 800; color: {'#4CAF50' if not diagnosis.is_low_confidence else '#FF9800'};">{int(diagnosis.confidence * 100)}%</div>
                    <span style="background: rgba(255, 152, 0, 0.2); border: 1px solid #FF9800; color: #FFB74D; padding: 4px 12px; border-radius: 12px; font-weight: 700; font-size: 0.8rem;">
                        {t["lbl_severity_level"]} {diagnosis.severity}
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ----------------------------------------------------
        # PRIORITY #3: LIVE CLIMATE SIGNALS GRID
        # ----------------------------------------------------
        st.markdown(f"#### {t['lbl_live_weather_signals']}")
        col_w1, col_w2, col_w3, col_w4 = st.columns(4)
        with col_w1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-val">🌡️ {round(weather.current_temp_c, 1)}°C</div>
                <div class="metric-lbl">{t['lbl_temp']}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_w2:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-val">💧 {int(weather.current_humidity_pct)}%</div>
                <div class="metric-lbl">{t['lbl_humidity']}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_w3:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-val">🌧️ {int(weather.current_rain_prob_pct)}%</div>
                <div class="metric-lbl">{t['lbl_rain_risk']}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_w4:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-val">💨 {round(weather.current_wind_speed_kmh, 1)} <span style="font-size: 0.9rem;">km/h</span></div>
                <div class="metric-lbl">{t['lbl_wind_speed']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ----------------------------------------------------
        # PRIORITY #4: ACTIONABLE FARMER TREATMENT PLAN
        # ----------------------------------------------------
        kb_entry = classifier.kb_data.get(diagnosis.disease_id, classifier.kb_data.get("tomato_late_blight"))
        col_t1, col_t2 = st.columns(2)

        with col_t1:
            st.markdown(f"""
            <div class="glass-card">
                <h3 style="color: #81C784; margin-top: 0;">{t['lbl_immediate_steps']}</h3>
            """, unsafe_allow_html=True)
            for step in kb_entry.get("immediate_actions", []):
                st.markdown(f"- {step}")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown(f"""
            <div class="glass-card">
                <h3 style="color: #81C784; margin-top: 0;">{t['lbl_organic_options']}</h3>
            """, unsafe_allow_html=True)
            for org in kb_entry.get("organic_treatment", []):
                st.markdown(f"- {org}")
            st.markdown("</div>", unsafe_allow_html=True)

        with col_t2:
            st.markdown(f"""
            <div class="glass-card">
                <h3 style="color: #4CAF50; margin-top: 0;">{t['lbl_chemical_options']}</h3>
            """, unsafe_allow_html=True)
            for chem in kb_entry.get("chemical_treatment", []):
                st.markdown(f"- {chem}")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown(f"""
            <div class="glass-card" style="border-left: 4px solid #F44336;">
                <h3 style="color: #FF7043; margin-top: 0;">{t['lbl_what_not_to_do']}</h3>
            """, unsafe_allow_html=True)
            for wnd in kb_entry.get("what_not_to_do", []):
                st.markdown(f"- {wnd}")
            st.markdown("</div>", unsafe_allow_html=True)

        # ----------------------------------------------------
        # PRIORITY #5: FARMER VOICE ASSISTANT PLAYER (BCP-47 TAG & VOL 1.0)
        # ----------------------------------------------------
        st.markdown(f"### {t['btn_listen_audio']} (Farmer Voice Assistant)")
        speech_script = advisory_data["speech_text"].replace("'", "\\'").replace('"', '\\"').replace("\n", " ")
        
        tts_html = f"""
        <div style="margin-bottom: 20px;">
            <button onclick="speakAdvisory()" style="background: linear-gradient(135deg, #2E7D32 0%, #1B5E20 100%); color: white; border: none; padding: 14px 28px; border-radius: 12px; font-weight: bold; cursor: pointer; font-size: 1.05rem; display: flex; align-items: center; gap: 10px; width: 100%; justify-content: center; box-shadow: 0 4px 15px rgba(46, 125, 50, 0.4);">
                🔊 {t['btn_listen_audio']} ({UI_LANGUAGES[selected_lang_code]})
            </button>
            <div id="voiceNotice" style="margin-top: 10px; font-size: 0.88rem; color: #94A3B8; text-align: center; font-weight: 600;"></div>
            <script>
                function speakAdvisory() {{
                    if ('speechSynthesis' in window) {{
                        window.speechSynthesis.cancel();
                        var utterance = new SpeechSynthesisUtterance("{speech_script}");
                        utterance.lang = "{speech_bcp47}";
                        utterance.volume = 1.0;
                        utterance.rate = 0.85;
                        utterance.pitch = 1.0;
                        
                        var targetLang = "{selected_lang_code}";
                        var targetBcp = "{speech_bcp47}".toLowerCase();
                        var noticeDiv = document.getElementById("voiceNotice");
                        
                        function assignVoiceAndSpeak() {{
                            var voices = window.speechSynthesis.getVoices();
                            var matchedVoice = voices.find(function(v) {{
                                var l = v.lang.toLowerCase().replace('_', '-');
                                return l === targetBcp || l.startsWith(targetLang);
                            }});
                            
                            if (matchedVoice) {{
                                utterance.voice = matchedVoice;
                                noticeDiv.innerHTML = "<span style='color: #81C784;'>🔊 Playing audio in " + matchedVoice.name + " (" + matchedVoice.lang + ")</span>";
                            }} else {{
                                noticeDiv.innerHTML = "<span style='color: #FFB74D;'>ℹ️ Notice: " + "{UI_LANGUAGES[selected_lang_code]}" + " speech voice is not installed in this browser/OS. Text advisory above is fully translated.</span>";
                            }}
                            window.speechSynthesis.speak(utterance);
                        }}
                        
                        if (window.speechSynthesis.getVoices().length > 0) {{
                            assignVoiceAndSpeak();
                        }} else {{
                            window.speechSynthesis.onvoiceschanged = assignVoiceAndSpeak;
                            setTimeout(assignVoiceAndSpeak, 300);
                        }}
                    }} else {{
                        alert("Text-to-speech is not supported in this browser.");
                    }}
                }}
            </script>
        </div>
        """
        st.components.v1.html(tts_html, height=100)

        # Latency Benchmark Drawer
        with st.expander("⚡ System Latency & Performance Diagnostics", expanded=False):
            st.markdown(f"""
            - **Model Inference Latency:** `{diagnosis.inference_time_ms} ms`
            - **Weather API Fetch Latency:** `{weather_ms} ms`
            - **Total Pipeline Latency:** `{total_latency_ms} ms`
            - **Supported Disease Classes:** `38 Verified PlantVillage Classes`
            """)

        # Responsible Guidance Disclaimer
        st.info(t["lbl_disclaimer"])

    # =========================================================
    # TAB 2: EXPLAINABLE AI (XAI)
    # =========================================================
    with tab2:
        st.markdown(f"### {t['nav_xai_tab']}")
        
        col_xai1, col_xai2 = st.columns(2)
        with col_xai1:
            st.image(input_image, caption="Original Field Observation Photo", use_container_width=True)
        with col_xai2:
            st.image(heatmap_pil, caption="AI Grad-CAM Saliency Heatmap (Red/Amber = High Spot Focus)", use_container_width=True)

        st.markdown("---")
        st.image(side_by_side_pil, caption="Side-by-Side Diagnostic Verification (Original vs AI Saliency Contour Map)", use_container_width=True)
        
        st.markdown("---")
        st.markdown(xai_markdown)

    # =========================================================
    # TAB 3: MICROCLIMATE FORECAST
    # =========================================================
    with tab3:
        st.markdown(f"### 🌤️ 48-Hour Microclimate Forecast for {weather.location_name}")
        
        hours_list = [p.time_str for p in weather.hourly_forecast[:24]]
        temps_list = [p.temp_c for p in weather.hourly_forecast[:24]]
        rain_list = [p.rain_prob_pct for p in weather.hourly_forecast[:24]]
        wind_list = [p.wind_speed_kmh for p in weather.hourly_forecast[:24]]

        st.markdown("#### 🌧️ Precipitation Washout Risk (%) Over Next 24 Hours")
        st.bar_chart({"Rain Probability (%)": rain_list}, height=220)

        col_fc1, col_fc2 = st.columns(2)
        with col_fc1:
            st.markdown("#### 🌡️ Temperature (°C) Timeline")
            st.line_chart({"Temperature (°C)": temps_list}, height=200)
        with col_fc2:
            st.markdown("#### 💨 Wind Speed (km/h) Timeline")
            st.line_chart({"Wind Speed (km/h)": wind_list}, height=200)

    # =========================================================
    # TAB 4: HISTORY & LOCALIZED PDF EXPORT
    # =========================================================
    with tab4:
        st.markdown(f"### {t['nav_history_tab']}")
        
        if st.session_state.history:
            st.dataframe(st.session_state.history, use_container_width=True)
        else:
            st.info("No saved history yet in this session.")

        st.markdown("---")
        st.markdown("### 📥 Download Localized Reports")

        col_exp1, col_exp2 = st.columns(2)

        with col_exp1:
            # Generate ReportLab Localized PDF (English, Telugu, or Hindi)
            pdf_bytes = PDFReportGenerator.generate_pdf_report(
                diagnosis_data={
                    "crop": diagnosis.crop,
                    "disease_name": diagnosis.disease_name,
                    "confidence": diagnosis.confidence,
                    "severity": diagnosis.severity,
                    "inference_source": diagnosis.inference_source
                },
                weather_data={
                    "location_name": weather.location_name,
                    "current_temp_c": weather.current_temp_c,
                    "current_humidity_pct": weather.current_humidity_pct,
                    "current_rain_prob_pct": weather.current_rain_prob_pct,
                    "current_wind_speed_kmh": weather.current_wind_speed_kmh
                },
                decision_data={
                    "status_label": safety_window.status_label,
                    "status_color": safety_window.status_color,
                    "primary_reason": safety_window.primary_reason,
                    "recommended_window": safety_window.recommended_window
                },
                kb_entry=kb_entry,
                lang=selected_lang_code
            )

            st.download_button(
                label=t["btn_download_pdf"],
                data=pdf_bytes,
                file_name=f"agrishield_{selected_lang_code}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )

        with col_exp2:
            report_json = json.dumps({
                "app": APP_NAME,
                "version": VERSION,
                "timestamp": datetime.datetime.now().isoformat(),
                "lang": selected_lang_code,
                "location": selected_location_info,
                "diagnosis": {
                    "crop": diagnosis.crop,
                    "disease": diagnosis.disease_name,
                    "confidence": diagnosis.confidence,
                    "severity": diagnosis.severity,
                    "inference_source": diagnosis.inference_source
                },
                "weather": {
                    "temp_c": weather.current_temp_c,
                    "humidity_pct": weather.current_humidity_pct,
                    "rain_prob_pct": weather.current_rain_prob_pct,
                    "wind_speed_kmh": weather.current_wind_speed_kmh
                },
                "decision": {
                    "status": safety_window.status_code,
                    "label": safety_window.status_label,
                    "recommended_window": safety_window.recommended_window,
                    "reason": safety_window.primary_reason
                }
            }, indent=2)

            st.download_button(
                label=t["btn_download_json"],
                data=report_json,
                file_name=f"agrishield_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
                use_container_width=True
            )

else:
    st.info("👈 Please select a sample leaf image or upload a photo in the sidebar to run the analysis.")
