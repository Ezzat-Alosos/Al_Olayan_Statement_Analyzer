"""
العليان لتحليل القوائم المالية
Al Olayan Financial Statement Analyzer
الملف الرئيسي للتطبيق (نسخة سريعة - بدون معالج)
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List

# إعداد الصفحة
st.set_page_config(
    page_title="العليان لتحليل القوائم المالية",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# الاستيرادات المحلية
from config import COLORS, DEMO_DATA
from charts import create_gauge_chart, create_radar_chart, create_pie_chart, create_waterfall_chart, create_line_chart, create_area_chart, create_cash_flow_chart, create_grouped_bar_chart, create_stacked_bar_chart
from cleaning import clean_dataframe

# استيراد الملفات المدمجة (التي تحتوي على كل شيء آخر)
from analysis_engine import *
from ui_engine import *


# استيراد محرك التصدير PDF
from pdf_export import generate_pdf_report, get_pdf_filename, is_pdf_export_available

# استيراد محرك التصدير Excel
from excel_export import generate_excel_report, get_excel_filename

# استيراد محرك التصدير CSV
from csv_export import generate_csv_report, get_csv_filename



# تهيئة الجلسة
init_session_state()

# تطبيق CSS
st.markdown(get_main_css(), unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# الهيدر
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
render_header()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# شريط الأدوات
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
toolbar_cols = st.columns(7)

with toolbar_cols[0]:
    reset_btn = st.button("🔄 إعادة تعيين", use_container_width=True)
with toolbar_cols[2]:
    about_btn = st.button("ℹ️ حول البرنامج", use_container_width=True)

# معالجة أزرار شريط الأدوات
if reset_btn:
    reset_state()
    st.rerun()
if about_btn:
    set_state("show_about", not get_state("show_about"))
    st.rerun()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# التعريفات والوظائف المساعدة
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _render_quick_upload_screen():
    """عرض شاشة رفع الملف المباشرة (بدون معالج)"""
    st.markdown("### 📤 رفع القوائم المالية للتحليل الفوري")
    
    uploaded_file = st.file_uploader(
        "اختر ملف Excel (يجب أن يكون العمود الأول للبنود، والأعمدة التالية للسنوات):",
        type=["xlsx", "xls"],
        help="ملف الإكسل يجب أن يكون بتنسيق: البند | 2024 | 2025 ... (يتم التحليل تلقائياً)"
    )

    if uploaded_file is not None:
        # قراءة الملف مباشرة
        try:
            # قراءة الملف مع التأكد من أن الصف الأول هو العناوين
            df = pd.read_excel(uploaded_file, header=0)

            # تحويل جميع أسماء الأعمدة إلى نصوص لضمان ظهورها بشكل صحيح
            df.columns = df.columns.astype(str).str.strip()

            # تنظيف البيانات
            df, messages = clean_dataframe(df)
            
            # عرض معاينة للبيانات
            st.markdown("#### 📊 معاينة البيانات المرفوعة")
            st.dataframe(df, use_container_width=True, hide_index=True)

            # نفترض أن الأعمدة من العمود الثاني هي السنوات
            periods = df.columns[1:].tolist()
            set_state("periods", periods)

            # الكشف التلقائي عن المطابقات
            st.markdown("#### 🔍 جاري مطابقة البنود تلقائياً...")
            
            # استخراج البيانات المطابقة مباشرة من DataFrame
            mapped_data = {}
            first_col = df.columns[0]  # عمود "البند"
            
            # قاموس لترجمة المفاتيح الإنجليزية إلى أسماء عربية
            item_labels = {
                "cash": "النقدية",
                "receivables": "الذمم المدينة",
                "inventory": "المخزون",
                "total_assets": "إجمالي الأصول",
                "total_liabilities": "إجمالي الخصوم",
                "total_equity": "حقوق الملكية",
                "revenue": "الإيرادات",
                "cost_of_sales": "تكلفة المبيعات",
                "gross_profit": "مجمل الربح",
                "operating_expenses": "المصاريف التشغيلية",
                "operating_income": "الربح التشغيلي",
                "net_income": "صافي الربح",
                "operating_cash_flow": "التدفقات التشغيلية",
                "investing_cash_flow": "التدفقات الاستثمارية",
                "financing_cash_flow": "التدفقات التمويلية",
                "net_cash_flow": "صافي التدفقات النقدية",
                "short_term_loans": "قروض قصيرة الأجل",
                "long_term_loans": "قروض طويلة الأجل",
                "interest_expense": "مصروف الفوائد",
                "fixed_assets": "الأصول الثابتة",
                "share_capital": "رأس المال",
                "retained_earnings": "الأرباح المبقاة",
                "prepaid": "مصروفات مدفوعة مقدماً",
                "shares_outstanding": "عدد الأسهم",
                "tax_expense": "مصروف الضريبة",
                "accounts_payable": "الذمم الدائنة",
                "accrued_expenses": "مصروفات مستحقة",
                "other_current_assets": "أصول متداولة أخرى",
                "other_non_current_assets": "أصول غير متداولة أخرى",
                "investments": "الاستثمارات",
                "bonds": "سندات",
                "other_equity": "بنود أخرى في حقوق الملكية",
                "reserves": "الاحتياطيات",
                "income_before_tax": "الربح قبل الضريبة",
                "other_income": "إيرادات أخرى",
                "operating_income": "الربح التشغيلي",
            }

            # البحث عن كل بند مالي في الجدول
            for item_key in item_labels.keys():
                item_label = item_labels.get(item_key)
                
                if item_label:
                    mask = df[first_col].astype(str).str.strip() == item_label
                    if mask.any():
                        row = df[mask].iloc[0]
                        values = []
                        for p_col in periods:
                            if p_col in df.columns:
                                try:
                                    val = float(row[p_col]) if pd.notna(row[p_col]) else 0.0
                                except (ValueError, TypeError):
                                    val = 0.0
                                values.append(val)
                            else:
                                values.append(0.0)
                        
                        if any(v != 0 for v in values):
                            mapped_data[item_key] = values

            # التحقق من وجود بيانات
            if not mapped_data:
                st.error("❌ لم يتم التعرف على البنود المالية في الملف. تأكد من أن العمود الأول يحتوي على أسماء البنود (مثل: النقدية، الإيرادات) وأن الأعمدة التالية هي القيم المالية.")
                return

            set_state("mapped_data", mapped_data)

            # زر التحليل المباشر
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 تحليل القوائم المالية", type="primary", use_container_width=True):
                    set_state("app_state", "analysis")
                    _run_analysis(mapped_data, periods)
                    st.rerun()

        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء قراءة الملف: {str(e)}")


def _run_analysis(mapped_data: Dict, periods: List[str]):
    """تشغيل التحليل المالي الكامل."""
    with st.spinner("⏳ جارٍ التحليل وحساب النسب..."):
        # حساب النسب المالية
        ratios = calculate_all_ratios(mapped_data, period_idx=-1)

        # التحليل الأفقي
        horizontal = calculate_horizontal_analysis(mapped_data, periods)
        h_summary = get_horizontal_summary(horizontal, mapped_data)

        # التحليل الرأسي
        vertical = calculate_vertical_analysis(mapped_data, periods)
        v_summary = get_vertical_summary(vertical, periods)

        # التعليقات الذكية
        comments = generate_comments(ratios, horizontal, mapped_data)

        # نقاط القوة والضعف
        strengths, weaknesses = identify_strengths_weaknesses(ratios, horizontal)

        # التوصيات
        recommendations = generate_recommendations(ratios, strengths, weaknesses)

        # درجة الصحة المالية
        health = calculate_health_score(ratios)

        # الملخص التنفيذي
        summary_text = generate_executive_summary(
            ratios, health, strengths, weaknesses, horizontal, mapped_data, periods
        )

        # بطاقات KPI
        raw = ratios.get("raw_values", {})
        kpi_data = {
            "إجمالي الأصول": raw.get("total_assets", 0),
            "إجمالي الخصوم": raw.get("total_liabilities", 0),
            "حقوق الملكية": raw.get("total_equity", 0),
            "الإيرادات": raw.get("revenue", 0),
            "تكلفة المبيعات": raw.get("cost_of_sales", 0),
            "مجمل الربح": raw.get("gross_profit", 0),
            "الربح التشغيلي": raw.get("operating_income", 0),
            "صافي الربح": raw.get("net_income", 0),
            "التدفقات التشغيلية": raw.get("operating_cf", 0),
            "التدفقات الاستثمارية": raw.get("investing_cf", 0),
            "التدفقات التمويلية": raw.get("financing_cf", 0),
        }

        # حفظ النتائج
        store_analysis_results({
            "financial_ratios": ratios,
            "horizontal_analysis": horizontal,
            "horizontal_summary": h_summary,
            "vertical_analysis": vertical,
            "vertical_summary": v_summary,
            "rule_comments": comments,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "health_score": health,
            "summary_text": summary_text,
            "kpi_data": kpi_data,
        })


def _render_analysis_results():
    """عرض نتائج التحليل."""
    
    # أزرار التصدير
    st.markdown("---")
    export_cols = st.columns(4)
    with export_cols[0]:
        if st.button("📄 تصدير PDF", use_container_width=True):
            _handle_pdf_export()
    with export_cols[1]:
        if st.button("📊 تصدير Excel", use_container_width=True):
            _handle_excel_export()
    with export_cols[2]:
        if st.button("📁 تصدير CSV", use_container_width=True):
            _handle_csv_export()
    with export_cols[3]:
        if st.button("🔄 تحليل ملف جديد", use_container_width=True):
            reset_state()
            st.rerun()

    st.markdown("---")

    # التبويبات
    tabs = st.tabs([
        "📊 لوحة المعلومات",
        "📑 الميزانية العمومية",
        "💰 قائمة الدخل",
        "💵 التدفقات النقدية",
        "📈 المؤشرات المالية",
        "📉 الاتجاهات",
        "📄 التقرير النهائي",
    ])

    with tabs[0]:
        _render_dashboard()
    with tabs[1]:
        _render_balance_sheet()
    with tabs[2]:
        _render_income_statement()
    with tabs[3]:
        _render_cash_flow()
    with tabs[4]:
        _render_financial_indicators()
    with tabs[5]:
        _render_trends()
    with tabs[6]:
        _render_final_report()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# دوال التصدير
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _handle_pdf_export():
    available, missing = is_pdf_export_available()
    if not available:
        st.error(f"❌ مكتبات مطلوبة غير متوفرة: {', '.join(missing)}")
        return

    analysis_data = {
        "kpi_data": get_state("kpi_data", {}),
        "financial_ratios": get_state("financial_ratios", {}),
        "horizontal_analysis": get_state("horizontal_analysis", {}),
        "health_score": get_state("health_score", {}),
        "strengths": get_state("strengths", []),
        "weaknesses": get_state("weaknesses", []),
        "recommendations": get_state("recommendations", []),
        "summary_text": get_state("summary_text", ""),
    }

    # تجميع الرسوم البيانية التي تم إنشاؤها في الواجهة
    charts = {}
    mapped_data = get_state("mapped_data", {})
    periods = get_state("periods", [])
    health = get_state("health_score", {})
    
    # 1. Gauge Chart
    if get_state("kpi_data"):
        charts['gauge'] = create_gauge_chart(health.get("total_score", 0), "درجة الصحة المالية")
    
    # 2. Radar Chart
    if health.get("category_scores"):
        cat_scores = health.get("category_scores", {})
        categories = [v["label"] for v in cat_scores.values()]
        scores = [v["score"] for v in cat_scores.values()]
        charts['radar'] = create_radar_chart(categories, scores)
    
    # 3. Pie Chart (الأصول)
    if mapped_data:
        asset_items = ["cash", "receivables", "inventory", "fixed_assets", "intangible_assets", "investments"]
        asset_labels = ["النقدية", "الذمم المدينة", "المخزون", "الأصول الثابتة", "الأصول غير الملموسة", "الاستثمارات"]
        asset_values = [mapped_data.get(k, [0])[-1] for k in asset_items]
        asset_values = [v for v in asset_values if v > 0]
        asset_labels_filtered = [l for l, v in zip(asset_labels, [mapped_data.get(k, [0])[-1] for k in asset_items]) if v > 0]
        if asset_values:
            charts['pie'] = create_pie_chart(asset_labels_filtered, asset_values, "توزيع الأصول")
    
    # 4. Waterfall Chart (قائمة الدخل)
    if mapped_data.get("revenue") and mapped_data.get("net_income"):
        revenue = mapped_data.get("revenue", [0])[-1]
        cos = mapped_data.get("cost_of_sales", [0])[-1]
        opex = mapped_data.get("operating_expenses", [0])[-1]
        interest = mapped_data.get("interest_expense", [0])[-1]
        tax = mapped_data.get("tax_expense", [0])[-1]
        net = mapped_data.get("net_income", [0])[-1]
        if revenue > 0:
            waterfall_cats = ["الإيرادات", "تكلفة المبيعات", "المصاريف التشغيلية", "الفوائد", "الضرائب", "صافي الربح"]
            waterfall_vals = [revenue, -cos, -opex, -interest, -tax, net]
            charts['waterfall'] = create_waterfall_chart(waterfall_cats, waterfall_vals, "من الإيرادات إلى صافي الربح")
    
    # 5. Line Chart (اتجاه الإيرادات والأرباح)
    if len(periods) > 1:
        trend_series = {}
        for key, label in [("revenue", "الإيرادات"), ("gross_profit", "مجمل الربح"), ("net_income", "صافي الربح")]:
            if key in mapped_data:
                trend_series[label] = mapped_data[key]
        if trend_series:
            charts['line'] = create_line_chart(periods, trend_series, "اتجاه الأداء المالي")
    
    # 6. Area Chart (اتجاه الأصول والخصوم)
    if len(periods) > 1:
        bs_series = {}
        for key, label in [("total_assets", "الأصول"), ("total_liabilities", "الخصوم"), ("total_equity", "حقوق الملكية")]:
            if key in mapped_data:
                bs_series[label] = mapped_data[key]
        if bs_series:
            charts['area'] = create_area_chart(periods, bs_series, "اتجاه المركز المالي")
    
    # 7. Cash Flow Chart
    operating = mapped_data.get("operating_cash_flow", [])
    investing = mapped_data.get("investing_cash_flow", [])
    financing = mapped_data.get("financing_cash_flow", [])
    if operating or investing or financing:
        charts['cashflow'] = create_cash_flow_chart(
            periods,
            operating if operating else [0] * len(periods),
            investing if investing else [0] * len(periods),
            financing if financing else [0] * len(periods),
        )

    pdf_bytes = generate_pdf_report(
        analysis_data,
        get_state("company_name", ""),
        get_state("periods", []),
        charts  # <--- تم إرجاع تمرير المخططات
    )

    if pdf_bytes:
        filename = get_pdf_filename(get_state("company_name", ""), get_state("periods", []))
        st.download_button(
            "⬇️ تحميل PDF",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf",
        )
        st.success("✅ تم إنشاء التقرير بنجاح")
    else:
        st.error("❌ حدث خطأ أثناء إنشاء التقرير")


def _handle_excel_export():
    """معالجة تصدير Excel مع الرسوم البيانية"""
    analysis_data = {
        "kpi_data": get_state("kpi_data", {}),
        "financial_ratios": get_state("financial_ratios", {}),
        "horizontal_analysis": get_state("horizontal_analysis", {}),
        "health_score": get_state("health_score", {}),  # إضافة
        "strengths": get_state("strengths", []),  # إضافة
        "weaknesses": get_state("weaknesses", []),  # إضافة
        "recommendations": get_state("recommendations", []),  # إضافة
    }

    excel_bytes = generate_excel_report(
        analysis_data,
        get_state("mapped_data", {}),
        get_state("periods", []),
        get_state("company_name", ""),
    )

    if excel_bytes:
        filename = get_excel_filename(get_state("company_name", ""), get_state("periods", []))
        st.download_button(
            "⬇️ تحميل Excel",
            data=excel_bytes,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        st.success("✅ تم إنشاء ملف Excel بنجاح")
    else:
        st.error("❌ حدث خطأ أثناء إنشاء الملف")



def _handle_csv_export():
    analysis_data = {
        "financial_ratios": get_state("financial_ratios", {}),
        "health_score": get_state("health_score", {}),
    }

    csv_content = generate_csv_report(
        analysis_data,
        get_state("mapped_data", {}),
        get_state("periods", []),
    )

    if csv_content:
        filename = get_csv_filename(get_state("company_name", ""), get_state("periods", []))
        st.download_button(
            "⬇️ تحميل CSV",
            data=csv_content.encode('utf-8-sig'),
            file_name=filename,
            mime="text/csv",
        )
        st.success("✅ تم إنشاء ملف CSV بنجاح")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# دوال العرض الفرعية
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _render_dashboard():
    st.markdown("### 📊 لوحة المعلومات - الملخص التنفيذي")
    health = get_state("health_score", {})
    if health:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            render_health_score(
                health.get("total_score", 0),
                health.get("classification", {}).get("label", ""),
                health.get("classification", {}).get("color", "#6C757D"),
            )
            fig = create_gauge_chart(health.get("total_score", 0), "درجة الصحة المالية")
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    kpi_data = get_state("kpi_data", {})
    mapped_data = get_state("mapped_data", {})
    periods = get_state("periods", [])

    if kpi_data:
        st.markdown("#### المؤشرات الرئيسية")
        kpi_items = list(kpi_data.items())
        for row_start in range(0, len(kpi_items), 4):
            cols = st.columns(4)
            for i, col in enumerate(cols):
                idx = row_start + i
                if idx < len(kpi_items):
                    label, value = kpi_items[idx]
                    with col:
                        change_text = None
                        change_type = "neutral"
                        if len(periods) > 1:
                            key_map = {
                                "إجمالي الأصول": "total_assets",
                                "الإيرادات": "revenue",
                                "صافي الربح": "net_income",
                                "حقوق الملكية": "total_equity",
                            }
                            data_key = key_map.get(label)
                            if data_key and data_key in mapped_data and len(mapped_data[data_key]) > 1:
                                prev = mapped_data[data_key][-2]
                                curr = mapped_data[data_key][-1]
                                if prev != 0:
                                    growth = ((curr - prev) / abs(prev)) * 100
                                    change_text = f"{growth:.1f}%"
                                    change_type = "positive" if growth > 0 else "negative"
                        render_kpi_card(
                            label,
                            f"{value:,.0f}" if isinstance(value, (int, float)) else str(value),
                            change_text,
                            change_type,
                        )

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### ✅ أفضل المؤشرات")
        ratios = get_state("financial_ratios", {})
        best = get_best_indicators(ratios)
        for ind in best:
            st.markdown(f"{ind['icon']} **{ind['label']}**: {ind['value']:.2f} ({ind['status']})")
    with col2:
        st.markdown("#### ⚠️ مؤشرات تحتاج متابعة")
        worst = get_worst_indicators(ratios)
        for ind in worst:
            st.markdown(f"{ind['icon']} **{ind['label']}**: {ind['value']:.2f} ({ind['status']})")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 💪 نقاط القوة")
        for s in get_state("strengths", []):
            render_strength_item(s)
    with col2:
        st.markdown("#### ⚡ نقاط الضعف")
        for w in get_state("weaknesses", []):
            render_weakness_item(w)

    st.markdown("---")
    st.markdown("#### 📝 الملخص المالي")
    render_analysis_comment(get_state("summary_text", ""))

    if health:
        cat_scores = health.get("category_scores", {})
        if cat_scores:
            categories = [v["label"] for v in cat_scores.values()]
            scores = [v["score"] for v in cat_scores.values()]
            fig = create_radar_chart(categories, scores)
            st.plotly_chart(fig, use_container_width=True)


def _render_balance_sheet():
    st.markdown("### 📑 تحليل الميزانية العمومية")
    mapped_data = get_state("mapped_data", {})
    periods = get_state("periods", [])
    if not mapped_data:
        st.info("لا توجد بيانات للعرض")
        return
    
    # ━━━ 1. جدول الميزانية العمومية ━━━
    bs_items = {
        "cash": "النقدية", "receivables": "الذمم المدينة",
        "inventory": "المخزون", "prepaid": "مصروفات مدفوعة مقدماً",
        "fixed_assets": "الأصول الثابتة", "intangible_assets": "الأصول غير الملموسة",
        "investments": "الاستثمارات", "total_assets": "إجمالي الأصول",
        "accounts_payable": "الذمم الدائنة", "short_term_loans": "قروض قصيرة الأجل",
        "long_term_loans": "قروض طويلة الأجل", "total_liabilities": "إجمالي الخصوم",
        "share_capital": "رأس المال", "retained_earnings": "الأرباح المبقاة",
        "reserves": "الاحتياطيات", "total_equity": "حقوق الملكية",
    }
    table_data = []
    for key, label in bs_items.items():
        if key in mapped_data:
            row = {"البند": label}
            for i, p in enumerate(periods):
                if i < len(mapped_data[key]):
                    row[p] = f"{mapped_data[key][i]:,.0f}"
            table_data.append(row)
    if table_data:
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")



        # تعريف المتغيرات للحسابات (حتى لو لم نستخدم الرسم المكدس)
    cash_vals = mapped_data.get("cash", [0]*len(periods))
    rec_vals = mapped_data.get("receivables", [0]*len(periods))
    inv_vals = mapped_data.get("inventory", [0]*len(periods))
    fixed_vals = mapped_data.get("fixed_assets", [0]*len(periods))




    
    # ━━━ 2. هيكل الأصول (دائري) ━━━
    st.markdown("#### هيكل الأصول")
    asset_items = ["cash", "receivables", "inventory", "fixed_assets", "intangible_assets", "investments"]
    asset_labels = ["النقدية", "الذمم المدينة", "المخزون", "الأصول الثابتة", "الأصول غير الملموسة", "الاستثمارات"]
    asset_values = [mapped_data.get(k, [0])[-1] for k in asset_items]
    asset_values = [v for v in asset_values if v > 0]
    asset_labels_filtered = [l for l, v in zip(asset_labels, [mapped_data.get(k, [0])[-1] for k in asset_items]) if v > 0]
    if asset_values:
        fig = create_pie_chart(asset_labels_filtered, asset_values, "توزيع الأصول")
        st.plotly_chart(fig, use_container_width=True)




#======================================================

    # ━━━ 3. هيكل الأصول المكدس (Stacked Bar) ━━━
    #st.markdown("#### هيكل الأصول المكدس (تحليل السنوات)")
    
    # تجهيز البيانات لعرضها كأعمدة مكدسة
    #stacked_data = {}
    
    # التأكد من أن لدينا بيانات لكل بند
    #cash_vals = mapped_data.get("cash", [0]*len(periods))
    #rec_vals = mapped_data.get("receivables", [0]*len(periods))
    #inv_vals = mapped_data.get("inventory", [0]*len(periods))
    #fixed_vals = mapped_data.get("fixed_assets", [0]*len(periods))
    
    # إضافة البيانات إلى القاموس (كل نوع من الأصول سيكون لوناً مختلفاً في المكدس)
    #stacked_data["النقدية"] = cash_vals
    #stacked_data["الذمم المدينة"] = rec_vals
    #stacked_data["المخزون"] = inv_vals
    #stacked_data["الأصول الثابتة"] = fixed_vals
    
    # استدعاء دالة الرسم
    #if any(stacked_data.values()):
        #fig = create_stacked_bar_chart(
           # categories=periods,
          #  series=stacked_data,
         #   title="توزيع الأصول حسب النوع (مكدس)"
        #)
        #st.plotly_chart(fig, use_container_width=True)



#========================================================




    # ━━━ 4. مقارنة الأصول والخصوم (Grouped Bar) ━━━
    st.markdown("#### مقارنة الأصول والخصوم")
    if len(periods) >= 1:
        comparison_series = {}
        
        # حساب إجمالي الأصول والخصوم إذا لم تكن موجودة مباشرة
        total_assets_vals = mapped_data.get("total_assets")
        if not total_assets_vals:
            total_assets_vals = [sum(vals) for vals in zip(cash_vals, rec_vals, inv_vals, fixed_vals)]
        
        total_liabilities_vals = mapped_data.get("total_liabilities")
        if not total_liabilities_vals:
            # افترض أن الخصوم تساوي مجموع الخصوم المتداولة وغير المتداولة إذا كانت البيانات متاحة
            short_term = mapped_data.get("short_term_loans", [0]*len(periods))
            long_term = mapped_data.get("long_term_loans", [0]*len(periods))
            total_liabilities_vals = [s + l for s, l in zip(short_term, long_term)]
        
        if total_assets_vals and total_liabilities_vals:
            comparison_series["إجمالي الأصول"] = total_assets_vals
            comparison_series["إجمالي الخصوم"] = total_liabilities_vals
            
            # رسم المخطط المقارن
            fig = create_grouped_bar_chart(
                categories=periods,
                series=comparison_series,
                title="مقارنة إجمالي الأصول والخصوم عبر السنوات"
            )
            st.plotly_chart(fig, use_container_width=True)


def _render_income_statement():
    st.markdown("### 💰 تحليل قائمة الدخل")
    mapped_data = get_state("mapped_data", {})
    periods = get_state("periods", [])
    if not mapped_data:
        st.info("لا توجد بيانات للعرض")
        return
    is_items = {
        "revenue": "الإيرادات", "cost_of_sales": "تكلفة المبيعات",
        "gross_profit": "مجمل الربح", "operating_expenses": "المصاريف التشغيلية",
        "operating_income": "الربح التشغيلي", "interest_expense": "مصروف الفوائد",
        "income_before_tax": "الربح قبل الضريبة", "tax_expense": "مصروف الضريبة",
        "net_income": "صافي الربح",
    }
    table_data = []
    for key, label in is_items.items():
        if key in mapped_data:
            row = {"البند": label}
            for i, p in enumerate(periods):
                if i < len(mapped_data[key]):
                    row[p] = f"{mapped_data[key][i]:,.0f}"
            table_data.append(row)
    if table_data:
        st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("#### التحليل الشلالي لقائمة الدخل")
    revenue = mapped_data.get("revenue", [0])[-1]
    cos = mapped_data.get("cost_of_sales", [0])[-1]
    opex = mapped_data.get("operating_expenses", [0])[-1]
    interest = mapped_data.get("interest_expense", [0])[-1]
    tax = mapped_data.get("tax_expense", [0])[-1]
    net = mapped_data.get("net_income", [0])[-1]

    if revenue > 0:
        waterfall_cats = ["الإيرادات", "تكلفة المبيعات", "المصاريف التشغيلية", "الفوائد", "الضرائب", "صافي الربح"]
        waterfall_vals = [revenue, -cos, -opex, -interest, -tax, net]
        fig = create_waterfall_chart(waterfall_cats, waterfall_vals, "من الإيرادات إلى صافي الربح")
        st.plotly_chart(fig, use_container_width=True)

    if len(periods) > 1:
        st.markdown("#### مقارنة الإيرادات والأرباح")
        series = {}
        for key, label in [("revenue", "الإيرادات"), ("gross_profit", "مجمل الربح"), ("net_income", "صافي الربح")]:
            if key in mapped_data:
                series[label] = mapped_data[key]
        if series:
            fig = create_grouped_bar_chart(periods, series, "مقارنة الأداء المالي")
            st.plotly_chart(fig, use_container_width=True)


def _render_cash_flow():
    st.markdown("### 💵 تحليل التدفقات النقدية")
    mapped_data = get_state("mapped_data", {})
    periods = get_state("periods", [])
    if not mapped_data:
        st.info("لا توجد بيانات للعرض")
        return
    cf_items = {
        "operating_cash_flow": "صافي التدفقات التشغيلية",
        "investing_cash_flow": "صافي التدفقات الاستثمارية",
        "financing_cash_flow": "صافي التدفقات التمويلية",
    }
    table_data = []
    for key, label in cf_items.items():
        if key in mapped_data:
            row = {"البند": label}
            for i, p in enumerate(periods):
                if i < len(mapped_data[key]):
                    row[p] = f"{mapped_data[key][i]:,.0f}"
            table_data.append(row)
    if table_data:
        st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

    st.markdown("---")
    operating = mapped_data.get("operating_cash_flow", [])
    investing = mapped_data.get("investing_cash_flow", [])
    financing = mapped_data.get("financing_cash_flow", [])

    if operating or investing or financing:
        fig = create_cash_flow_chart(
            periods,
            operating if operating else [0] * len(periods),
            investing if investing else [0] * len(periods),
            financing if financing else [0] * len(periods),
        )
        st.plotly_chart(fig, use_container_width=True)


def _render_financial_indicators():
    st.markdown("### 📈 المؤشرات المالية")
    ratios = get_state("financial_ratios", {})
    if not ratios:
        st.info("لا توجد بيانات للعرض")
        return
    sub_tabs = st.tabs(["السيولة", "الربحية", "النشاط", "المديونية"])
    with sub_tabs[0]:
        st.markdown("#### 💧 نسب السيولة")
        liquidity = ratios.get("liquidity", {})
        for key, data in liquidity.items():
            value = data.get("value")
            if value is not None:
                evaluation = evaluate_ratio(key, value)
                render_ratio_card(
                    data["label"], value, evaluation["status"], evaluation["color"],
                    data.get("formula", ""), data.get("is_percentage", False), data.get("is_amount", False)
                )
    with sub_tabs[1]:
        st.markdown("#### 💰 نسب الربحية")
        profitability = ratios.get("profitability", {})
        for key, data in profitability.items():
            value = data.get("value")
            if value is not None:
                evaluation = evaluate_ratio(key, value)
                render_ratio_card(
                    data["label"], value, evaluation["status"], evaluation["color"],
                    data.get("formula", ""), data.get("is_percentage", False), data.get("is_amount", False)
                )
    with sub_tabs[2]:
        st.markdown("#### 🔄 نسب النشاط")
        activity = ratios.get("activity", {})
        for key, data in activity.items():
            value = data.get("value")
            if value is not None:
                evaluation = evaluate_ratio(key, value)
                render_ratio_card(
                    data["label"], value, evaluation["status"], evaluation["color"],
                    data.get("formula", ""), data.get("is_percentage", False), data.get("is_amount", False)
                )
    with sub_tabs[3]:
        st.markdown("#### 🏦 نسب المديونية")
        leverage = ratios.get("leverage", {})
        for key, data in leverage.items():
            value = data.get("value")
            if value is not None:
                evaluation = evaluate_ratio(key, value, data.get("inverse", False))
                render_ratio_card(
                    data["label"], value, evaluation["status"], evaluation["color"],
                    data.get("formula", ""), data.get("is_percentage", False), data.get("is_amount", False)
                )


def _render_trends():
    st.markdown("### 📉 تحليل الاتجاهات")
    mapped_data = get_state("mapped_data", {})
    periods = get_state("periods", [])
    if len(periods) < 2:
        st.info("يتطلب تحليل الاتجاهات بيانات لأكثر من فترة واحدة")
        return
    
    st.markdown("#### اتجاه الإيرادات والأرباح")
    trend_series = {}
    for key, label in [("revenue", "الإيرادات"), ("gross_profit", "مجمل الربح"), ("net_income", "صافي الربح")]:
        if key in mapped_data:
            trend_series[label] = mapped_data[key]
    if trend_series:
        fig = create_line_chart(periods, trend_series, "اتجاه الأداء المالي")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### اتجاه الأصول والخصوم")
    bs_series = {}
    for key, label in [("total_assets", "الأصول"), ("total_liabilities", "الخصوم"), ("total_equity", "حقوق الملكية")]:
        if key in mapped_data:
            bs_series[label] = mapped_data[key]
    if bs_series:
        fig = create_area_chart(periods, bs_series, "اتجاه المركز المالي")
        st.plotly_chart(fig, use_container_width=True)


def _render_final_report():
    st.markdown("### 📄 التقرير النهائي")
    st.markdown("#### الملخص التنفيذي")
    st.markdown(get_state("summary_text", ""))
    st.markdown("---")
    st.markdown("#### 📋 التوصيات")
    recommendations = get_state("recommendations", [])
    for i, rec in enumerate(recommendations, 1):
        st.markdown(f"{i}. {rec}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# المحتوى الرئيسي (النسخة السريعة)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# التحقق مما إذا كان المستخدم يريد استخدام البيانات التجريبية
if get_state("use_demo", False):
    # تحميل البيانات التجريبية
    mapped_data = {}
    for section in ["balance_sheet", "income_statement", "cash_flow"]:
        for key, values in DEMO_DATA[section].items():
            mapped_data[key] = values
    
    set_state("mapped_data", mapped_data)
    set_state("periods", DEMO_DATA["periods"])
    set_state("analysis_complete", True)
    set_state("app_state", "analysis")
    _run_analysis(mapped_data, DEMO_DATA["periods"])
    set_state("use_demo", False)  # إعادة التعيين

# إذا كان التحليل مكتملاً، اعرض النتائج
elif is_analysis_complete():
    _render_analysis_results()

# إذا لم يكن هناك بيانات، اعرض شاشة رفع الملف المباشرة
else:
    _render_quick_upload_screen()