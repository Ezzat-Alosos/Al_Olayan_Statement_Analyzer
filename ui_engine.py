"""
محرك واجهة المستخدم - UI Engine
يجمع مكونات الواجهة، إدارة الجلسة، والأنماط
"""

import streamlit as st
from typing import Optional, Any, Dict
from config import COLORS, FONT_URL, FONT_FAMILY, INDICATOR_COLORS

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. Session Manager (إدارة الجلسة)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def init_session_state() -> None:
    defaults = {
        "app_state": "welcome", "wizard_step": 1,
        "uploaded_file": None, "file_name": "", "file_type": "",
        "all_sheets": [], "selected_sheet": None,
        "raw_dataframe": None, "header_row": 0, "preview_df": None,
        "cleaned_df": None, "column_mapping": {}, "mapped_data": {},
        "analysis_results": None, "kpi_data": None,
        "financial_ratios": None, "horizontal_analysis": None,
        "vertical_analysis": None, "health_score": None,
        "rule_comments": None, "strengths": [], "weaknesses": [],
        "summary_text": "", "company_name": "", "periods": [], "num_periods": 0,
        "show_about": False, "show_settings": False, "analysis_complete": False,
        "using_demo": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state: st.session_state[key] = value

def get_state(key: str, default: Any = None) -> Any:
    return st.session_state.get(key, default)

def set_state(key: str, value: Any) -> None:
    st.session_state[key] = value

def reset_state() -> None:
    # قائمة بالمفاتيح التي يجب الحفاظ عليها (مثل مفاتيح Streamlit الخاصة)
    system_keys = ["_st", "__st"]
    
    for key in list(st.session_state.keys()):
        # الحفاظ على المفاتيح الداخلية أو المفاتيح النظامية
        if not key.startswith("_") and key not in system_keys:
            del st.session_state[key]
    init_session_state()

def is_analysis_complete() -> bool:
    return st.session_state.get("analysis_complete", False)

def store_analysis_results(results: dict) -> None:
    for key, value in results.items(): st.session_state[key] = value
    st.session_state["analysis_complete"] = True

def get_mapped_data() -> Optional[dict]:
    return st.session_state.get("mapped_data")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. Styles (أنماط CSS)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def get_main_css() -> str:
    return f"""
    <style>
        @import url('{FONT_URL}');
        * {{ font-family: '{FONT_FAMILY}', sans-serif !important; }}
        .main .block-container {{ padding-top: 1rem; padding-bottom: 2rem; max-width: 1400px; }}
        .stApp {{ direction: rtl; }}
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        .app-header {{
            background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
            padding: 1.5rem 2rem; border-radius: 12px; margin-bottom: 1rem; text-align: center;
            box-shadow: 0 4px 15px rgba(27, 58, 92, 0.2);
        }}
        .app-header h1 {{ color: white; font-size: 2rem; font-weight: 700; }}
        .app-header p {{ color: rgba(255, 255, 255, 0.85); font-size: 1rem; }}
        .kpi-card {{ background: white; border: 1px solid {COLORS['border']}; border-radius: 10px; padding: 1.2rem; text-align: center; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04); min-height: 120px; }}
        .kpi-card .kpi-value {{ font-size: 1.6rem; font-weight: 700; color: {COLORS['primary']}; }}
        .kpi-card .kpi-label {{ font-size: 0.85rem; color: {COLORS['text_secondary']}; }}
        .kpi-change.positive {{ color: {INDICATOR_COLORS['positive']}; }}
        .kpi-change.negative {{ color: {INDICATOR_COLORS['negative']}; }}
        .welcome-screen {{ text-align: center; padding: 3rem 2rem; background: {COLORS['surface']}; border-radius: 16px; border: 2px dashed {COLORS['border']}; margin: 2rem 0; }}
        .ratio-card {{ background: white; border: 1px solid {COLORS['border']}; border-radius: 10px; padding: 1rem; margin-bottom: 0.8rem; border-right: 4px solid {COLORS['primary']}; }}
        .analysis-comment {{ background: {COLORS['surface']}; border-right: 4px solid {COLORS['secondary']}; border-radius: 8px; padding: 1rem 1.2rem; margin: 0.8rem 0; }}
        .health-score-container {{ text-align: center; padding: 2rem; background: white; border-radius: 12px; border: 1px solid {COLORS['border']}; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05); }}
        .health-score-value {{ font-size: 3rem; font-weight: 800; }}
        .health-score-label {{ font-size: 1.2rem; font-weight: 600; }}
    </style>
    """

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. Components (مكونات واجهة المستخدم)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def render_header():
    st.markdown("""<div class="app-header"><h1>📊 العليان لتحليل القوائم المالية</h1><p>منصة ذكاء أعمال لتحليل القوائم المالية واتخاذ القرار</p></div>""", unsafe_allow_html=True)

def render_kpi_card(label: str, value: str, change: Optional[str] = None, change_type: str = "neutral"):
    change_html = ""
    if change:
        css_class = "positive" if change_type == "positive" else "negative" if change_type == "negative" else ""
        arrow = "↑" if change_type == "positive" else "↓" if change_type == "negative" else ""
        change_html = f'<p class="kpi-change {css_class}">{arrow} {change}</p>'
    st.markdown(f"""<div class="kpi-card"><p class="kpi-label">{label}</p><p class="kpi-value">{value}</p>{change_html}</div>""", unsafe_allow_html=True)

def render_welcome_screen():
    st.markdown("""<div class="welcome-screen"><div class="welcome-icon">📊</div><h2>مرحباً بك في برنامج العليان لتحليل القوائم المالية</h2><p>يقوم البرنامج بتحليل القوائم المالية وتحويلها إلى مؤشرات ورسوم بيانية وتقارير احترافية خلال ثوانٍ.</p></div>""", unsafe_allow_html=True)

def render_ratio_card(name: str, value: float, status: str, color: str, description: str = "", is_percentage: bool = False, is_amount: bool = False):
    if is_percentage: formatted_value = f"{value * 100:.1f}%"
    elif is_amount: formatted_value = f"{value:,.0f}"
    else: formatted_value = f"{value:.2f}"
    st.markdown(f"""<div class="ratio-card" style="border-right-color: {color};"><div class="ratio-name">{name}</div><div class="ratio-value" style="color: {color};">{formatted_value}</div><div style="font-size: 0.8rem; color: {color}; font-weight: 600;">{status}</div><div class="ratio-desc">{description}</div></div>""", unsafe_allow_html=True)

def render_analysis_comment(comment: str):
    st.markdown(f"""<div class="analysis-comment">💡 {comment}</div>""", unsafe_allow_html=True)

def render_strength_item(text: str):
    st.markdown(f"""<div class="strength-item">✅ {text}</div>""", unsafe_allow_html=True)

def render_weakness_item(text: str):
    st.markdown(f"""<div class="weakness-item">⚠️ {text}</div>""", unsafe_allow_html=True)

def render_health_score(score: int, label: str, color: str):
    st.markdown(f"""<div class="health-score-container"><div class="health-score-value" style="color: {color};">{score}</div><div class="health-score-label" style="color: {color};">/ 100</div><div class="health-score-label" style="color: {color}; margin-top: 0.5rem;">{label}</div></div>""", unsafe_allow_html=True)

def render_about_dialog():
    st.markdown("""<div class="about-section"><h2>📊 العليان لتحليل القوائم المالية</h2><p><strong>الإصدار:</strong> 1.0.0</p><p><strong>الوصف:</strong> منصة ذكاء أعمال متكاملة لتحليل القوائم المالية واتخاذ القرار</p><hr><p><strong>المميزات:</strong></p><p>• تحليل الميزانية العمومية وقائمة الدخل والتدفقات النقدية</p><p>• حساب أكثر من 20 نسبة مالية</p><p>• رسوم بيانية تفاعلية احترافية</p><p>• تقارير PDF و Excel جاهزة للإرسال</p><p>• تعليقات وتوصيات ذكية</p><p>• درجة الصحة المالية</p></div>""", unsafe_allow_html=True)