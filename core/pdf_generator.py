"""
Localized PDF Report Generator Module for AgriShield AI.
Uses ReportLab with Nirmala TrueType font support to generate printable PDF advisory reports
in English, Telugu (తెలుగు), and Hindi (हिंदी).
"""

import io
import os
import datetime
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from config import TRANSLATIONS


# Register Unicode Font for Indic Scripts (Telugu & Hindi)
FONT_NAME = "Helvetica" # Default fallback
NIRMALA_PATH = "C:\\Windows\\Fonts\\Nirmala.ttc"

if os.path.exists(NIRMALA_PATH):
    try:
        pdfmetrics.registerFont(TTFont('Nirmala', NIRMALA_PATH, subfontIndex=0))
        FONT_NAME = "Nirmala"
        print("[INFO] ReportLab registered Nirmala TrueType font for Telugu & Hindi PDF support.")
    except Exception as e:
        print(f"[WARN] Failed to register Nirmala font: {e}")


class PDFReportGenerator:
    """
    Generates fully localized PDF assessment reports for smallholder farm recordkeeping.
    Supports English, Telugu, and Hindi.
    """

    @staticmethod
    def generate_pdf_report(
        diagnosis_data: Dict[str, Any],
        weather_data: Dict[str, Any],
        decision_data: Dict[str, Any],
        kb_entry: Dict[str, Any],
        lang: str = "en"
    ) -> bytes:
        """
        Creates a localized PDF document in memory and returns bytes.
        """
        t = TRANSLATIONS.get(lang, TRANSLATIONS["en"])

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom Localized Styles
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName=FONT_NAME,
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#1B5E20')
        )
        
        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName=FONT_NAME,
            fontSize=9,
            textColor=colors.HexColor('#555555')
        )

        h2_style = ParagraphStyle(
            'SectionH2',
            parent=styles['Heading2'],
            fontName=FONT_NAME,
            fontSize=12,
            leading=15,
            textColor=colors.HexColor('#2E7D32'),
            spaceBefore=10,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            'BodyDark',
            parent=styles['Normal'],
            fontName=FONT_NAME,
            fontSize=9,
            leading=13,
            textColor=colors.HexColor('#222222')
        )

        elements = []

        # 1. Header & Title
        doc_title_text = f"🛡️ {t['app_title']} — {t['app_tagline']}"
        elements.append(Paragraph(doc_title_text, title_style))
        
        time_str = datetime.datetime.now().strftime('%B %d, %Y - %H:%M')
        loc_str = weather_data.get('location_name', 'Farm Site')
        elements.append(Paragraph(f"Generated: {time_str} | Location: {loc_str}", subtitle_style))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#2E7D32'), spaceAfter=12))

        # 2. Diagnosis Summary Table
        elements.append(Paragraph(f"1. {t['lbl_diagnosis_result']}", h2_style))
        
        conf_val = int(float(diagnosis_data.get('confidence', 0.85)) * 100)
        
        diag_table_data = [
            [Paragraph(f"<b>{t['lbl_target_crop']}</b>", body_style), Paragraph(str(diagnosis_data.get('crop')), body_style)],
            [Paragraph(f"<b>{t['lbl_diagnosed_condition']}</b>", body_style), Paragraph(str(diagnosis_data.get('disease_name')), body_style)],
            [Paragraph(f"<b>{t['lbl_confidence_score']}</b>", body_style), Paragraph(f"{conf_val}% (Softmax Probability)", body_style)],
            [Paragraph(f"<b>{t['lbl_severity_level']}</b>", body_style), Paragraph(str(diagnosis_data.get('severity')), body_style)],
            [Paragraph("<b>Engine Source:</b>", body_style), Paragraph(str(diagnosis_data.get('inference_source', 'Real HF Vision Model')), body_style)]
        ]
        
        diag_table = Table(diag_table_data, colWidths=[160, 370])
        diag_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F8E9')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#C8E6C9')),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(diag_table)
        elements.append(Spacer(1, 12))

        # 3. Live Microclimate & Safety Decision Table
        elements.append(Paragraph(f"2. {t['lbl_action_timing_decision']}", h2_style))
        
        status_color_hex = decision_data.get('status_color', '#EF6C00')
        
        climate_table_data = [
            [Paragraph(f"<b>{t['lbl_live_weather_signals']}:</b>", body_style), 
             Paragraph(f"{t['lbl_temp']}: {weather_data.get('current_temp_c')}°C | {t['lbl_humidity']}: {weather_data.get('current_humidity_pct')}% | {t['lbl_rain_risk']}: {weather_data.get('current_rain_prob_pct')}% | {t['lbl_wind_speed']}: {weather_data.get('current_wind_speed_kmh')} km/h", body_style)],
            [Paragraph(f"<b>{t['lbl_action_timing_decision']}:</b>", body_style), Paragraph(f"<font color='{status_color_hex}'><b>{decision_data.get('status_label')}</b></font>", body_style)],
            [Paragraph(f"<b>{t['lbl_reason']}</b>", body_style), Paragraph(str(decision_data.get('primary_reason')), body_style)],
            [Paragraph(f"<b>{t['lbl_recommended_safe_window']}</b>", body_style), Paragraph(f"<b>{decision_data.get('recommended_window')}</b>", body_style)]
        ]

        climate_table = Table(climate_table_data, colWidths=[160, 370])
        climate_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFFDE7')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#FFF9C4')),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(climate_table)
        elements.append(Spacer(1, 12))

        # 4. Actionable Treatment Plan
        elements.append(Paragraph("3. Agronomic Treatment Plan", h2_style))
        
        elements.append(Paragraph(f"<b>{t['lbl_immediate_steps']}</b>", body_style))
        for step in kb_entry.get("immediate_actions", []):
            elements.append(Paragraph(f"• {step}", body_style))
        elements.append(Spacer(1, 6))

        elements.append(Paragraph(f"<b>{t['lbl_organic_options']}</b>", body_style))
        for org in kb_entry.get("organic_treatment", []):
            elements.append(Paragraph(f"• {org}", body_style))
        elements.append(Spacer(1, 6))

        elements.append(Paragraph(f"<b>{t['lbl_chemical_options']}</b>", body_style))
        for chem in kb_entry.get("chemical_treatment", []):
            elements.append(Paragraph(f"• {chem}", body_style))
        elements.append(Spacer(1, 6))

        elements.append(Paragraph(f"<b>{t['lbl_what_not_to_do']}</b>", body_style))
        for wnd in kb_entry.get("what_not_to_do", []):
            elements.append(Paragraph(f"• {wnd}", body_style))
        elements.append(Spacer(1, 14))

        # 5. Disclaimer
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CCCCCC'), spaceAfter=8))
        disclaimer_style = ParagraphStyle('Disclaimer', parent=styles['Normal'], fontName=FONT_NAME, fontSize=8, textColor=colors.HexColor('#666666'))
        elements.append(Paragraph(t['lbl_disclaimer'], disclaimer_style))

        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
