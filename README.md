# العليان لتحليل القوائم المالية
## Al Olayan Financial Statement Analyzer

منصة ذكاء أعمال متكاملة لتحليل القوائم المالية واتخاذ القرار.

---

## المميزات

- ✅ استيراد ذكي للقوائم المالية (Excel, CSV)
- ✅ معالج استيراد بأربع خطوات
- ✅ تنظيف تلقائي للبيانات
- ✅ مطابقة ذكية للأعمدة مع قاموس عربي/إنجليزي
- ✅ حساب أكثر من 20 نسبة مالية
- ✅ التحليل الأفقي والرأسي
- ✅ تعليقات وتوصيات ذكية (Rule-Based)
- ✅ درجة الصحة المالية (من 100)
- ✅ رسوم بيانية تفاعلية (Plotly)
- ✅ تصدير PDF احترافي
- ✅ تصدير Excel متعدد الأوراق
- ✅ تصدير CSV
- ✅ دعم كامل للعربية (RTL)
- ✅ بيانات تجريبية مدمجة

---

## التثبيت

```bash
pip install -r requirements.txt
```

## التشغيل

```bash
streamlit run app.py
```

---

## هيكل المشروع

```
app/
├── app.py                  # الملف الرئيسي
├── config.py               # التكوين والإعدادات
├── styles.py               # أنماط CSS
├── components.py           # مكونات الواجهة
├── session_manager.py      # إدارة الجلسة
├── data_loader.py          # تحميل الملفات
├── cleaning.py             # تنظيف البيانات
├── mapping.py              # مطابقة الأعمدة
├── validators.py           # التحقق من البيانات
├── financial_ratios.py     # النسب المالية
├── horizontal_analysis.py  # التحليل الأفقي
├── vertical_analysis.py    # التحليل الرأسي
├── rule_engine.py          # محرك القواعد الذكي
├── health_score.py         # درجة الصحة المالية
├── charts.py               # الرسوم البيانية
├── summary.py              # الملخص التنفيذي
├── pdf_export.py           # تصدير PDF
├── excel_export.py         # تصدير Excel
├── csv_export.py           # تصدير CSV
├── requirements.txt        # المتطلبات
└── README.md               # التوثيق
```

---

## النسب المالية المحسوبة

### نسب السيولة
- نسبة التداول (Current Ratio)
- نسبة السيولة السريعة (Quick Ratio)
- نسبة النقدية (Cash Ratio)
- رأس المال العامل (Working Capital)

### نسب الربحية
- هامش الربح الإجمالي (Gross Margin)
- هامش الربح التشغيلي (Operating Margin)
- هامش صافي الربح (Net Margin)
- العائد على الأصول (ROA)
- العائد على حقوق الملكية (ROE)
- ربحية السهم (EPS)

### نسب النشاط
- معدل دوران المخزون (Inventory Turnover)
- معدل دوران الذمم المدينة (Receivable Turnover)
- معدل دوران الأصول (Asset Turnover)
- متوسط فترة التحصيل (Average Collection Period)
- أيام المخزون (Days Inventory Outstanding)

### نسب المديونية
- نسبة المديونية (Debt Ratio)
- الخصوم إلى حقوق الملكية (Debt to Equity)
- الديون إلى الأصول (Debt to Assets)
- تغطية الفوائد (Interest Coverage)
- تغطية خدمة الدين (Debt Service Coverage)

---

## المتطلبات

- Python 3.9+
- Streamlit 1.28+
- Pandas 2.0+
- Plotly 5.15+
- OpenPyXL 3.1+
- ReportLab 4.0+
- arabic-reshaper 3.0+
- python-bidi 0.4+