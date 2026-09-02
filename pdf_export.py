from __future__ import annotations

import os
import io
from datetime import datetime
from io import BytesIO
from typing import List, Dict, Optional

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
import time

# استيراد مكتبات اللغة العربية
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_ARABIC = True
except ImportError:
    HAS_ARABIC = False
    arabic_reshaper = None
    get_display = None

# استيراد Plotly للتحويل
try:
    import plotly.io as pio
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False


def _find_arabic_font() -> str:
    """البحث عن خط عربي في النظام."""
    import platform
    
    font_paths = []
    
    # مسارات حسب نظام التشغيل
    if platform.system() == "Windows":
        font_paths = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/tahoma.ttf",
            "C:/Windows/Fonts/times.ttf",
            "C:/Windows/Fonts/seguiemj.ttf",
        ]
    elif platform.system() == "Darwin":
        font_paths = [
            "/System/Library/Fonts/Arial.ttf",
            "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Times.ttc",
            "/System/Library/Fonts/Helvetica.ttc",
        ]
    else:
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        ]
    
    # مسارات محلية في مجلد المشروع
    project_dir = os.path.dirname(os.path.abspath(__file__))
    font_paths.extend([
        os.path.join(project_dir, 'fonts', 'Tajawal-Regular.ttf'),
        os.path.join(project_dir, 'fonts', 'Cairo-Regular.ttf'),
        os.path.join(project_dir, 'fonts', 'arial.ttf'),
        os.path.join(project_dir, 'arial.ttf'),
        os.path.join(project_dir, 'tahoma.ttf'),
    ])
    
    for path in font_paths:
        if os.path.exists(path):
            return path
    
    return None


def _register_arabic_font() -> str:
    """تسجيل الخط العربي."""
    font_path = _find_arabic_font()
    
    if font_path:
        try:
            pdfmetrics.registerFont(TTFont('ArabicFont', font_path))
            print(f"✅ تم تحميل الخط: {font_path}")
            return "ArabicFont"
        except Exception as e:
            print(f"⚠️ فشل تحميل الخط {font_path}: {e}")
    
    print("⚠️ لم يتم العثور على خط عربي! سيتم استخدام الخط الافتراضي Helvetica.")
    return "Helvetica"


FONT_NAME = _register_arabic_font()


def ar(text) -> str:
    """معالجة النص العربي."""
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    
    if HAS_ARABIC:
        try:
            reshaped = arabic_reshaper.reshape(text)
            return get_display(reshaped)
        except Exception:
            return text
    return text


def _shorten_text(text, max_len=10):
    """تقصير النص للعرض في المخططات."""
    text = str(text)
    return text[:max_len] + ".." if len(text) > max_len else text


# ============================================================
# دوال إنشاء المخططات - ترجع BytesIO دائماً
# ============================================================

def _fig_to_bytesio(fig) -> BytesIO:
    """تحويل matplotlib figure إلى BytesIO."""
    img_buffer = BytesIO()
    fig.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    img_buffer.seek(0)
    return img_buffer


def _create_bar_chart_pdf(data, x_col, y_col, title) -> BytesIO:
    """إنشاء مخطط شريطي للـ PDF."""
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    x = data[x_col].astype(str).apply(lambda t: _shorten_text(t, 12)).tolist()
    y = data[y_col].tolist()
    plot_colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(x)))[::-1]
    bars = ax.bar(x, y, color=plot_colors, edgecolor='darkblue', linewidth=0.5)
    max_y = max(y) if y else 1
    for bar, val in zip(bars, y):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max_y * 0.02, 
                f'{val:,.0f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.set_ylabel('القيمة', fontsize=11, fontweight='bold')
    ax.set_title(title, fontsize=13, fontweight='bold', pad=15)
    plt.xticks(rotation=45, ha='right', fontsize=9)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    return _fig_to_bytesio(fig)


def _create_pie_chart_pdf(data, x_col, y_col, title) -> BytesIO:
    """إنشاء مخطط دائري للـ PDF."""
    fig, ax = plt.subplots(figsize=(8, 6.5), dpi=300)
    data = data.sort_values(y_col, ascending=False)
    labels = data[x_col].astype(str).apply(lambda t: _shorten_text(t, 12)).tolist()
    values = data[y_col].tolist()
    if sum(values) > 0:
        plot_colors = plt.cm.Blues(np.linspace(0.3, 0.9, len(labels)))[::-1]
        wedges, texts, autotexts = ax.pie(
            values, labels=labels, 
            autopct=lambda p: f'{p:.1f}%' if p > 3 else '', 
            colors=plot_colors, startangle=90, 
            wedgeprops={'edgecolor': 'white', 'linewidth': 1.5}
        )
        ax.set_title(title, fontsize=13, fontweight='bold', pad=15)
        for text in texts:
            text.set_fontsize(9)
        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')
            autotext.set_color('white')
        ax.set_aspect('equal')
    plt.tight_layout()
    return _fig_to_bytesio(fig)


def _create_bar_comparison_pdf(data, title) -> BytesIO:
    """مخطط مقارنة للسنوات (Grouped Bar) للـ PDF."""
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    years = data.columns[1:].tolist()
    labels = data.iloc[:, 0].tolist()
    x = np.arange(len(labels))
    width = 0.35
    for i, year in enumerate(years):
        values = data[year].tolist()
        offset = width * i - (len(years)-1) * width / 2
        bars = ax.bar(x + offset, values, width, label=str(year), 
                      color=plt.cm.Blues(np.linspace(0.4, 0.9, len(years)))[i])
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.02, 
                    f'{val:,.0f}', ha='center', va='bottom', fontsize=8)
    ax.set_ylabel('القيمة', fontsize=11, fontweight='bold')
    ax.set_title(title, fontsize=13, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
    ax.legend()
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    return _fig_to_bytesio(fig)


def _create_line_chart_pdf(data, x_col, y_col, title) -> BytesIO:
    """إنشاء مخطط خطي للـ PDF."""
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    x = data[x_col].astype(str).tolist()
    y = data[y_col].tolist()
    ax.plot(x, y, marker='o', linestyle='-', color='#1B3A5C', linewidth=2, markersize=8)
    ax.set_ylabel('القيمة', fontsize=11, fontweight='bold')
    ax.set_title(title, fontsize=13, fontweight='bold', pad=15)
    plt.xticks(rotation=45, ha='right', fontsize=9)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    return _fig_to_bytesio(fig)


def _create_area_chart_pdf(data, x_col, y_col, title) -> BytesIO:
    """إنشاء مخطط مساحي للـ PDF."""
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    x = data[x_col].astype(str).tolist()
    y = data[y_col].tolist()
    ax.fill_between(range(len(x)), y, color='#1B3A5C', alpha=0.4)
    ax.plot(range(len(x)), y, color='#1B3A5C', linewidth=2)
    ax.set_xticks(range(len(x)))
    ax.set_xticklabels(x, rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('القيمة', fontsize=11, fontweight='bold')
    ax.set_title(title, fontsize=13, fontweight='bold', pad=15)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    return _fig_to_bytesio(fig)


def _create_cash_flow_chart_pdf(data, title) -> BytesIO:
    """إنشاء مخطط تدفقات نقدية للـ PDF."""
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    years = data.columns[1:].tolist()
    labels = data.iloc[:, 0].tolist()
    x = np.arange(len(labels))
    width = 0.25
    cf_colors = ['#28A745', '#FFA726', '#DC3545']
    for i, year in enumerate(years):
        values = data[year].tolist()
        offset = width * i - (len(years)-1) * width / 2
        ax.bar(x + offset, values, width, label=str(year), color=cf_colors[i % len(cf_colors)])
    ax.axhline(0, color='black', linewidth=1)
    ax.set_ylabel('القيمة', fontsize=11, fontweight='bold')
    ax.set_title(title, fontsize=13, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
    ax.legend()
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    return _fig_to_bytesio(fig)


def _create_waterfall_chart_pdf(data, x_col, y_col, title) -> BytesIO:
    """إنشاء مخطط شلالي للـ PDF."""
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    categories = data[x_col].tolist()
    values = data[y_col].tolist()
    cumulative = 0
    cumulative_values = []
    for val in values:
        cumulative += val
        cumulative_values.append(cumulative)
    for i, (cat, val, cum) in enumerate(zip(categories, values, cumulative_values)):
        color = '#28A745' if val >= 0 else '#DC3545'
        bottom = cum - val if val >= 0 else cum
        ax.bar(cat, val, bottom=bottom, color=color, edgecolor='white', linewidth=0.5)
        ax.text(i, cum, f'{cum:,.0f}', ha='center', 
                va='bottom' if val >= 0 else 'top', fontsize=8, fontweight='bold')
    ax.set_ylabel('القيمة', fontsize=11, fontweight='bold')
    ax.set_title(title, fontsize=13, fontweight='bold', pad=15)
    plt.xticks(rotation=45, ha='right', fontsize=9)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    return _fig_to_bytesio(fig)


def _create_gauge_chart_pdf(value, title) -> BytesIO:
    """إنشاء مخطط مقياس (Gauge) للـ PDF."""
    fig, ax = plt.subplots(figsize=(6, 4), dpi=300)
    theta = np.linspace(0, np.pi, 100)
    r = 0.8
    x_arc = r * np.cos(theta)
    y_arc = r * np.sin(theta)
    ax.plot(x_arc, y_arc, color='#E0E4E8', linewidth=10, solid_capstyle='round')
    value_angle = (value / 100) * np.pi
    x_val = r * np.cos(value_angle)
    y_val = r * np.sin(value_angle)
    ax.plot([0, x_val], [0, y_val], color='#1B3A5C', linewidth=8, solid_capstyle='round')
    ax.plot(x_val, y_val, 'o', color='#1B3A5C', markersize=12)
    ax.text(0, -0.15, f'{value}/100', ha='center', va='center', 
            fontsize=20, fontweight='bold', color='#1B3A5C')
    ax.text(0, -0.45, title, ha='center', va='center', fontsize=12, color='#666666')
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-0.7, 1.1)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.tight_layout()
    return _fig_to_bytesio(fig)


# ============================================================
# تحويل Plotly figure إلى صورة
# ============================================================
def _plotly_to_image(fig, width=700, height=400) -> Optional[BytesIO]:
    """تحويل شكل Plotly إلى صورة PNG."""
    if fig is None or not HAS_PLOTLY:
        return None
    
    try:
        img_bytes = pio.to_image(fig, format='png', width=width, height=height, scale=2)
        return BytesIO(img_bytes)
    except Exception as e:
        print(f"⚠️ تعذر تحويل مخطط Plotly: {e}")
        return None


# ============================================================
# أنماط التقرير
# ============================================================
def _styles():
    """أنماط التقرير."""
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle('Title', parent=base['Title'], fontName=FONT_NAME, 
                                fontSize=22, leading=28, alignment=TA_CENTER, 
                                textColor=colors.HexColor("#1B3A5C"), spaceAfter=20),
        "heading": ParagraphStyle('Heading', parent=base['Heading2'], fontName=FONT_NAME, 
                                  fontSize=15, leading=20, alignment=TA_RIGHT, 
                                  textColor=colors.HexColor("#1B3A5C"), spaceAfter=12),
        "subheading": ParagraphStyle('Subheading', parent=base['Heading3'], fontName=FONT_NAME,
                                     fontSize=12, leading=16, alignment=TA_RIGHT,
                                     textColor=colors.HexColor("#2C5F8A"), spaceAfter=8),
        "normal": ParagraphStyle('Normal', parent=base['Normal'], fontName=FONT_NAME, 
                                 fontSize=10, leading=16, alignment=TA_RIGHT, 
                                 textColor=colors.black, spaceAfter=6),
        "small": ParagraphStyle('Small', parent=base['Normal'], fontName=FONT_NAME,
                               fontSize=8, leading=12, alignment=TA_CENTER,
                               textColor=colors.HexColor("#6C757D"), spaceAfter=4),
        "table_header": ParagraphStyle('TableHeader', fontName=FONT_NAME, fontSize=9, 
                                       leading=12, alignment=TA_CENTER, textColor=colors.white),
        "table_cell": ParagraphStyle('TableCell', fontName=FONT_NAME, fontSize=9,
                                     leading=12, alignment=TA_CENTER, textColor=colors.black),
    }


def _paragraph(text: str, style: ParagraphStyle) -> Paragraph:
    """إنشاء فقرة نصية."""
    return Paragraph(ar(text), style)


def _table_from_frame(frame: pd.DataFrame) -> Table:
    """إنشاء جدول من DataFrame."""
    if frame.empty:
        return Table([[ar("لا توجد بيانات")]], colWidths=[10*cm])
    
    data = [[ar(str(col)) for col in frame.columns]]
    data.extend([[ar(str(val)) for val in row] for row in frame.values.tolist()])
    
    table = Table(data, repeatRows=1, hAlign="CENTER")
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1B3A5C")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E4E8")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
    ]))
    return table


# ============================================================
# دالة إدراج صورة في التقرير - الإصدار الآمن
# ============================================================
def _add_image_to_story(story, img_buffer, width=16*cm, height=10*cm):
    """
    إضافة صورة إلى قصة التقرير بطريقة آمنة.
    
    Args:
        story: قائمة عناصر التقرير
        img_buffer: BytesIO يحتوي على الصورة
        width: عرض الصورة
        height: ارتفاع الصورة
    """
    if img_buffer is None:
        return
    
    # التأكد من أن img_buffer هو BytesIO
    if isinstance(img_buffer, bytes):
        img_buffer = BytesIO(img_buffer)
    
    if not hasattr(img_buffer, 'seek'):
        return
    
    try:
        img_buffer.seek(0)
        # استخدام ImageReader للتأكد من صحة الصورة
        reader = ImageReader(img_buffer)
        # إعادة التعيين بعد القراءة
        img_buffer.seek(0)
        img = Image(img_buffer, width=width, height=height)
        img.hAlign = "CENTER"
        story.append(img)
        story.append(Spacer(1, 0.3*cm))
    except Exception as e:
        print(f"⚠️ خطأ في إدراج الصورة: {e}")
        story.append(_paragraph(f"⚠️ تعذر إدراج الرسم البياني", _styles()["small"]))


def _render_chart_in_pdf(story, title, chart_func, *args):
    """دالة مساعدة لإدراج المخططات في التقرير."""
    story.append(Spacer(1, 0.3*cm))
    story.append(_paragraph(title, _styles()["heading"]))
    story.append(Spacer(1, 0.2*cm))
    
    try:
        img_buffer = chart_func(*args)
        _add_image_to_story(story, img_buffer)
    except Exception as e:
        print(f"⚠️ خطأ في إنشاء المخطط '{title}': {e}")
        story.append(_paragraph(f"⚠️ تعذر إنشاء المخطط: {str(e)[:50]}", _styles()["normal"]))


def _render_plotly_chart_in_pdf(story, title, fig, width=16*cm, height=10*cm):
    """إدراج مخطط Plotly في التقرير."""
    if fig is None:
        return
    
    story.append(Spacer(1, 0.3*cm))
    story.append(_paragraph(title, _styles()["heading"]))
    story.append(Spacer(1, 0.2*cm))
    
    img_buffer = _plotly_to_image(fig)
    if img_buffer:
        _add_image_to_story(story, img_buffer, width, height)
    else:
        story.append(_paragraph("⚠️ تعذر تحويل مخطط Plotly إلى صورة", _styles()["small"]))


# ============================================================
# الدالة الرئيسية للتصدير
# ============================================================
def generate_pdf_report(
    analysis_data: Dict,
    company_name: str = "",
    periods: List[str] = None,
    charts: Optional[Dict] = None,
) -> Optional[BytesIO]:
    """
    توليد تقرير PDF احترافي.
    
    Args:
        analysis_data: بيانات التحليل
        company_name: اسم الشركة
        periods: الفترات المالية
        charts: قاموس المخططات من Plotly
    
    Returns:
        BytesIO: محتوى ملف PDF أو None عند الخطأ
    """
    start = time.time()
    output = BytesIO()
    
    try:
        doc = SimpleDocTemplate(
            output,
            pagesize=landscape(A4),
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
            title=ar(f"تقرير مالي - {company_name}"),
            author=ar("العليان لتحليل القوائم المالية"),
        )
        styles = _styles()
        story = []
        
        # ====== عنوان التقرير ======
        story.append(Spacer(1, 0.8*cm))
        story.append(_paragraph("العليان لتحليل القوائم المالية", styles["title"]))
        story.append(Spacer(1, 0.3*cm))
        story.append(_paragraph("تقرير التحليل المالي الاحترافي", styles["heading"]))
        story.append(Spacer(1, 0.3*cm))
        if company_name:
            story.append(_paragraph(f"الشركة: {company_name}", styles["normal"]))
        if periods:
            story.append(_paragraph(f"الفترة: {' - '.join([str(p) for p in periods])}", styles["normal"]))
        story.append(Spacer(1, 0.5*cm))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E0E4E8")))
        
        story.append(PageBreak())
        
        # ====== الملخص التنفيذي ======
        story.append(_paragraph("📊 الملخص التنفيذي", styles["heading"]))
        story.append(Spacer(1, 0.3*cm))
        
        kpi_data = analysis_data.get("kpi_data", {})
        if kpi_data:
            df_kpi = pd.DataFrame(list(kpi_data.items()), columns=["المؤشر", "القيمة"])
            story.append(_table_from_frame(df_kpi))
            story.append(Spacer(1, 0.5*cm))
        
        # درجة الصحة المالية
        health = analysis_data.get("health_score", {})
        if health:
            score = health.get("total_score", 0)
            # محاولة استخدام Plotly gauge أولاً
            if charts and 'gauge' in charts:
                _render_plotly_chart_in_pdf(story, "درجة الصحة المالية", charts['gauge'], 12*cm, 8*cm)
            else:
                _render_chart_in_pdf(story, "درجة الصحة المالية", _create_gauge_chart_pdf, score, "درجة الصحة المالية")
        
        # Radar Chart
        if charts and 'radar' in charts:
            _render_plotly_chart_in_pdf(story, "تقييم الأداء حسب الفئة", charts['radar'], 14*cm, 10*cm)
        
        story.append(PageBreak())
        
        # ====== الميزانية العمومية ======
        story.append(_paragraph("📑 تحليل الميزانية العمومية", styles["heading"]))
        
        # Pie Chart
        if charts and 'pie' in charts:
            _render_plotly_chart_in_pdf(story, "هيكل الأصول", charts['pie'], 12*cm, 10*cm)
        
        # Stacked Bar
        if charts and 'stacked' in charts:
            _render_plotly_chart_in_pdf(story, "توزيع الأصول عبر السنوات", charts['stacked'], 16*cm, 10*cm)
        
        # Grouped Bar للمقارنة
        if charts and 'comparison' in charts:
            _render_plotly_chart_in_pdf(story, "مقارنة الأصول والخصوم", charts['comparison'], 16*cm, 10*cm)
        
        # إنشاء مخططات إضافية من البيانات
        mapped_data = analysis_data.get("mapped_data", {})
        if mapped_data:
            # مخطط شريطي للأصول
            asset_keys = ["cash", "receivables", "inventory", "fixed_assets"]
            asset_labels = ["النقدية", "الذمم المدينة", "المخزون", "الأصول الثابتة"]
            asset_values = [mapped_data.get(k, [0])[-1] if mapped_data.get(k) else 0 for k in asset_keys]
            
            if any(asset_values):
                asset_df = pd.DataFrame({"البند": asset_labels, "القيمة": asset_values})
                _render_chart_in_pdf(story, "هيكل الأصول (مخطط شريطي)", 
                                    _create_bar_chart_pdf, asset_df, "البند", "القيمة", "هيكل الأصول")
            
            # مخطط دائري
            if any(asset_values):
                pie_df = pd.DataFrame({"البند": asset_labels, "القيمة": asset_values})
                _render_chart_in_pdf(story, "توزيع الأصول (مخطط دائري)", 
                                    _create_pie_chart_pdf, pie_df, "البند", "القيمة", "توزيع الأصول")
        
        story.append(PageBreak())
        
        # ====== قائمة الدخل ======
        story.append(_paragraph("💰 تحليل قائمة الدخل", styles["heading"]))
        
        # Waterfall
        if charts and 'waterfall' in charts:
            _render_plotly_chart_in_pdf(story, "من الإيرادات إلى صافي الربح", charts['waterfall'], 16*cm, 10*cm)
        
        # Line Chart
        if charts and 'line' in charts:
            _render_plotly_chart_in_pdf(story, "اتجاه الإيرادات والأرباح", charts['line'], 16*cm, 10*cm)
        
        story.append(PageBreak())
        
        # ====== التدفقات النقدية ======
        story.append(_paragraph("💵 تحليل التدفقات النقدية", styles["heading"]))
        
        # Cash Flow Chart
        if charts and 'cashflow' in charts:
            _render_plotly_chart_in_pdf(story, "التدفقات النقدية", charts['cashflow'], 16*cm, 10*cm)
        
        story.append(PageBreak())
        
        # ====== النسب المالية ======
        story.append(_paragraph("📈 النسب المالية", styles["heading"]))
        
        ratios = analysis_data.get("financial_ratios", {})
        ratio_rows = []
        for category in ["liquidity", "profitability", "activity", "leverage"]:
            for key, data in ratios.get(category, {}).items():
                if isinstance(data, dict):
                    value = data.get("value")
                    if value is not None:
                        label = data.get("label", key)
                        if data.get("is_percentage"):
                            formatted = f"{value * 100:.2f}%"
                        else:
                            formatted = f"{value:.2f}"
                        ratio_rows.append([label, formatted])
        
        if ratio_rows:
            df_ratios = pd.DataFrame(ratio_rows, columns=["النسبة", "القيمة"])
            story.append(_table_from_frame(df_ratios))
        
        story.append(PageBreak())
        
        # ====== نقاط القوة والضعف ======
        story.append(_paragraph("تحليل شامل", styles["heading"]))
        
        strengths = analysis_data.get("strengths", [])
        if strengths:
            story.append(_paragraph("💪 نقاط القوة:", styles["subheading"]))
            for s in strengths:
                story.append(_paragraph(f"✓ {s}", styles["normal"]))
        
        story.append(Spacer(1, 0.4*cm))
        
        weaknesses = analysis_data.get("weaknesses", [])
        if weaknesses:
            story.append(_paragraph("⚠️ نقاط الضعف:", styles["subheading"]))
            for w in weaknesses:
                story.append(_paragraph(f"✗ {w}", styles["normal"]))
        
        story.append(Spacer(1, 0.4*cm))
        
        recommendations = analysis_data.get("recommendations", [])
        if recommendations:
            story.append(_paragraph("📋 التوصيات:", styles["subheading"]))
            for i, rec in enumerate(recommendations, 1):
                story.append(_paragraph(f"{i}. {rec}", styles["normal"]))
        
        # ====== بناء المستند ======
        doc.build(story)
        output.seek(0)
        
        elapsed = time.time() - start
        print(f"⏱️ [pdf_export] تم إنشاء التقرير في {elapsed:.2f} ثانية")
        return output
    
    except Exception as e:
        import traceback
        print(f"❌ خطأ في إنشاء التقرير: {e}")
        traceback.print_exc()
        return None


def get_pdf_filename(company_name: str, periods: List[str]) -> str:
    """توليد اسم ملف PDF."""
    date_str = datetime.now().strftime("%Y%m%d")
    period_str = "-".join([str(p) for p in (periods or [])])
    company = (company_name or "تقرير").replace(" ", "_")
    return f"{company}_{period_str}_تحليل_مالي_{date_str}.pdf"


def is_pdf_export_available() -> tuple:
    """التحقق من توفر مكتبات التصدير."""
    missing = []
    
    try:
        import matplotlib
        import numpy
    except ImportError:
        missing.append("matplotlib/numpy")
    
    try:
        import reportlab
    except ImportError:
        missing.append("reportlab")
    
    if not HAS_ARABIC:
        missing.append("arabic-reshaper / python-bidi")
    
    return len(missing) == 0, missing