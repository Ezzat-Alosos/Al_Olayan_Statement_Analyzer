"""
تكوين برنامج العليان لتحليل القوائم المالية
Al Olayan Financial Statement Analyzer - Configuration
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# هوية البرنامج
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
APP_NAME = "العليان لتحليل القوائم المالية"
APP_SUBTITLE = "منصة ذكاء أعمال لتحليل القوائم المالية واتخاذ القرار"
APP_VERSION = "1.0.0"
APP_AUTHOR = "العليان"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# الألوان
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COLORS = {
    "primary": "#1B3A5C",       # أزرق داكن
    "secondary": "#2C5F8A",     # أزرق متوسط
    "background": "#FFFFFF",    # أبيض
    "surface": "#F8F9FA",       # رمادي فاتح جداً
    "border": "#E0E4E8",        # رمادي حدود
    "text_primary": "#1B3A5C",  # نص أساسي
    "text_secondary": "#5A6B7B", # نص ثانوي
    "light_gray": "#F0F2F5",    # رمادي فاتح
}

# ألوان المؤشرات
INDICATOR_COLORS = {
    "positive": "#28A745",   # أخضر
    "warning": "#FFA726",    # برتقالي
    "negative": "#DC3545",   # أحمر
    "neutral": "#6C757D",    # رمادي
}

# ألوان الرسوم البيانية
CHART_COLORS = [
    "#1B3A5C", "#2C5F8A", "#4A90D9", "#7AB8F5",
    "#28A745", "#FFA726", "#DC3545", "#6C757D",
    "#17A2B8", "#6F42C1", "#E83E8C", "#FD7E14",
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# الخطوط
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FONT_FAMILY = "Cairo"
FONT_URL = "https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700;800&display=swap"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# أنواع الملفات المدعومة
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SUPPORTED_FILE_TYPES = {
    "excel": [".xlsx", ".xls"],
    "csv": [".csv"],
}

ALLOWED_EXTENSIONS = [".xlsx", ".xls", ".csv"]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# حدود تقييم النسب المالية
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RATIO_THRESHOLDS = {
    "current_ratio": {"excellent": 2.0, "good": 1.5, "acceptable": 1.0, "poor": 0.5},
    "quick_ratio": {"excellent": 1.5, "good": 1.0, "acceptable": 0.7, "poor": 0.3},
    "cash_ratio": {"excellent": 0.5, "good": 0.3, "acceptable": 0.2, "poor": 0.1},
    "gross_margin": {"excellent": 0.40, "good": 0.25, "acceptable": 0.15, "poor": 0.05},
    "operating_margin": {"excellent": 0.20, "good": 0.10, "acceptable": 0.05, "poor": 0.0},
    "net_margin": {"excellent": 0.15, "good": 0.08, "acceptable": 0.03, "poor": 0.0},
    "roa": {"excellent": 0.10, "good": 0.05, "acceptable": 0.02, "poor": 0.0},
    "roe": {"excellent": 0.20, "good": 0.12, "acceptable": 0.05, "poor": 0.0},
    "debt_ratio": {"excellent": 0.3, "good": 0.5, "acceptable": 0.7, "poor": 0.9},
    "debt_to_equity": {"excellent": 0.5, "good": 1.0, "acceptable": 2.0, "poor": 3.0},
    "inventory_turnover": {"excellent": 8.0, "good": 5.0, "acceptable": 3.0, "poor": 1.0},
    "receivable_turnover": {"excellent": 12.0, "good": 8.0, "acceptable": 5.0, "poor": 2.0},
    "asset_turnover": {"excellent": 2.0, "good": 1.0, "acceptable": 0.5, "poor": 0.2},
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# أوزان درجة الصحة المالية
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HEALTH_SCORE_WEIGHTS = {
    "liquidity": 0.25,
    "profitability": 0.25,
    "activity": 0.15,
    "leverage": 0.20,
    "cash_flow": 0.15,
}

HEALTH_SCORE_LABELS = {
    (90, 100): {"label": "ممتاز", "color": "#28A745", "icon": "🟢"},
    (80, 89): {"label": "جيد جداً", "color": "#5CB85C", "icon": "🟢"},
    (70, 79): {"label": "جيد", "color": "#FFA726", "icon": "🟡"},
    (60, 69): {"label": "مقبول", "color": "#FF8C00", "icon": "🟠"},
    (0, 59): {"label": "يحتاج إلى متابعة", "color": "#DC3545", "icon": "🔴"},
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# بنود القوائم المالية
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FINANCIAL_ITEMS = {
    "balance_sheet": {
        "current_assets": {
            "label": "الأصول المتداولة",
            "items": {
                "cash": "النقدية وما يعادلها",
                "receivables": "الذمم المدينة",
                "inventory": "المخزون",
                "prepaid": "مصروفات مدفوعة مقدماً",
                "other_current_assets": "أصول متداولة أخرى",
            }
        },
        "non_current_assets": {
            "label": "الأصول غير المتداولة",
            "items": {
                "fixed_assets": "الأصول الثابتة",
                "intangible_assets": "الأصول غير الملموسة",
                "investments": "الاستثمارات طويلة الأجل",
                "other_non_current_assets": "أصول غير متداولة أخرى",
            }
        },
        "total_assets": "إجمالي الأصول",
        "current_liabilities": {
            "label": "الخصوم المتداولة",
            "items": {
                "accounts_payable": "الذمم الدائنة",
                "short_term_loans": "قروض قصيرة الأجل",
                "accrued_expenses": "مصروفات مستحقة",
                "other_current_liabilities": "خصوم متداولة أخرى",
            }
        },
        "non_current_liabilities": {
            "label": "الخصوم غير المتداولة",
            "items": {
                "long_term_loans": "قروض طويلة الأجل",
                "bonds": "سندات",
                "other_non_current_liabilities": "خصوم غير متداولة أخرى",
            }
        },
        "total_liabilities": "إجمالي الخصوم",
        "equity": {
            "label": "حقوق الملكية",
            "items": {
                "share_capital": "رأس المال",
                "retained_earnings": "الأرباح المبقاة",
                "reserves": "الاحتياطيات",
                "other_equity": "بنود أخرى في حقوق الملكية",
            }
        },
        "total_equity": "إجمالي حقوق الملكية",
    },
    "income_statement": {
        "revenue": "الإيرادات",
        "cost_of_sales": "تكلفة المبيعات",
        "gross_profit": "مجمل الربح",
        "operating_expenses": "المصاريف التشغيلية",
        "operating_income": "الربح التشغيلي",
        "interest_expense": "مصروف الفوائد",
        "other_income": "إيرادات أخرى",
        "income_before_tax": "الربح قبل الضريبة",
        "tax_expense": "مصروف الضريبة",
        "net_income": "صافي الربح",
        "shares_outstanding": "عدد الأسهم",
    },
    "cash_flow": {
        "operating_cash_flow": "صافي التدفقات التشغيلية",
        "investing_cash_flow": "صافي التدفقات الاستثمارية",
        "financing_cash_flow": "صافي التدفقات التمويلية",
        "net_cash_flow": "صافي التدفقات النقدية",
    }
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# قاموس مطابقة الأعمدة
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COLUMN_MAPPING_DICTIONARY = {
    "cash": [
        "cash", "cash & cash equivalents", "cash and cash equivalents",
        "cash balance", "bank balance", "النقدية", "الصندوق", "البنوك",
        "النقد وما يعادله", "نقدية", "النقد", "الأرصدة النقدية",
    ],
    "receivables": [
        "receivables", "accounts receivable", "trade receivables",
        "الذمم المدينة", "المدينون", "حسابات القبض", "ذمم مدينة",
    ],
    "inventory": [
        "inventory", "inventories", "stock", "المخزون", "البضاعة",
        "مخزون", "بضاعة",
    ],
    "total_assets": [
        "total assets", "إجمالي الأصول", "مجموع الأصول", "اجمالي الاصول",
    ],
    "accounts_payable": [
        "accounts payable", "trade payables", "الذمم الدائنة",
        "الدائنون", "حسابات الدفع",
    ],
    "total_liabilities": [
        "total liabilities", "إجمالي الخصوم", "مجموع الخصوم",
        "اجمالي الالتزامات", "إجمالي الالتزامات",
    ],
    "total_equity": [
        "total equity", "shareholders equity", "stockholders equity",
        "حقوق الملكية", "إجمالي حقوق الملكية", "حقوق المساهمين",
    ],
    "revenue": [
        "revenue", "sales", "net sales", "total revenue", "net revenue",
        "الإيرادات", "المبيعات", "صافي المبيعات", "ايرادات",
    ],
    "cost_of_sales": [
        "cost of sales", "cost of goods sold", "cogs", "cost of revenue",
        "تكلفة المبيعات", "تكلفة البضاعة المباعة", "تكلفة الإيرادات",
    ],
    "gross_profit": [
        "gross profit", "gross margin", "مجمل الربح", "إجمالي الربح",
        "الربح الإجمالي",
    ],
    "operating_expenses": [
        "operating expenses", "opex", "المصاريف التشغيلية",
        "مصروفات تشغيلية", "المصروفات التشغيلية",
    ],
    "operating_income": [
        "operating income", "operating profit", "الربح التشغيلي",
        "الدخل التشغيلي", "ربح العمليات",
    ],
    "net_income": [
        "net income", "net profit", "net earnings", "صافي الربح",
        "صافي الدخل", "الربح الصافي",
    ],
    "operating_cash_flow": [
        "operating cash flow", "cash from operations",
        "التدفقات التشغيلية", "صافي التدفقات التشغيلية",
        "التدفقات النقدية من الأنشطة التشغيلية",
    ],
    "investing_cash_flow": [
        "investing cash flow", "cash from investing",
        "التدفقات الاستثمارية", "صافي التدفقات الاستثمارية",
        "التدفقات النقدية من الأنشطة الاستثمارية",
    ],
    "financing_cash_flow": [
        "financing cash flow", "cash from financing",
        "التدفقات التمويلية", "صافي التدفقات التمويلية",
        "التدفقات النقدية من الأنشطة التمويلية",
    ],
    "short_term_loans": [
        "short term loans", "short term debt", "current portion of long term debt",
        "قروض قصيرة الأجل", "ديون قصيرة الأجل",
    ],
    "long_term_loans": [
        "long term loans", "long term debt", "non current borrowings",
        "قروض طويلة الأجل", "ديون طويلة الأجل",
    ],
    "interest_expense": [
        "interest expense", "finance costs", "مصروف الفوائد",
        "تكاليف التمويل", "مصاريف الفوائد",
    ],
    "fixed_assets": [
        "fixed assets", "property plant and equipment", "ppe",
        "الأصول الثابتة", "الممتلكات والمعدات",
    ],
    "share_capital": [
        "share capital", "paid in capital", "common stock",
        "رأس المال", "رأس المال المدفوع",
    ],
    "retained_earnings": [
        "retained earnings", "accumulated profits",
        "الأرباح المبقاة", "الأرباح المحتجزة",
    ],
    "prepaid": [
        "prepaid expenses", "prepayments",
        "مصروفات مدفوعة مقدماً", "مدفوعات مقدمة",
    ],
    "shares_outstanding": [
        "shares outstanding", "number of shares", "عدد الأسهم",
        "الأسهم القائمة",
    ],
    "tax_expense": [
        "tax expense", "income tax", "مصروف الضريبة", "ضريبة الدخل",
    ],
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# إعدادات التصدير
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXPORT_SETTINGS = {
    "pdf": {
        "page_size": "A4",
        "margin": 50,
        "font_size_title": 18,
        "font_size_heading": 14,
        "font_size_body": 10,
        "font_size_small": 8,
    },
    "excel": {
        "header_color": "1B3A5C",
        "header_font_color": "FFFFFF",
        "alt_row_color": "F0F2F5",
        "border_color": "E0E4E8",
    },
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# بيانات تجريبية
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DEMO_DATA = {
    "company_name": "شركة النموذج التجارية",
    "periods": ["2022", "2023"],
    "balance_sheet": {
        "cash": [5000000, 6200000],
        "receivables": [3500000, 4100000],
        "inventory": [4200000, 3800000],
        "prepaid": [500000, 600000],
        "other_current_assets": [300000, 350000],
        "fixed_assets": [15000000, 16500000],
        "intangible_assets": [2000000, 1800000],
        "investments": [3000000, 3500000],
        "other_non_current_assets": [500000, 450000],
        "total_assets": [34000000, 37300000],
        "accounts_payable": [2800000, 3200000],
        "short_term_loans": [2000000, 1500000],
        "accrued_expenses": [1200000, 1400000],
        "other_current_liabilities": [500000, 600000],
        "long_term_loans": [8000000, 7000000],
        "bonds": [0, 0],
        "other_non_current_liabilities": [500000, 600000],
        "total_liabilities": [15000000, 14300000],
        "share_capital": [10000000, 10000000],
        "retained_earnings": [7000000, 10500000],
        "reserves": [2000000, 2500000],
        "other_equity": [0, 0],
        "total_equity": [19000000, 23000000],
    },
    "income_statement": {
        "revenue": [25000000, 30000000],
        "cost_of_sales": [15000000, 17500000],
        "gross_profit": [10000000, 12500000],
        "operating_expenses": [5000000, 5500000],
        "operating_income": [5000000, 7000000],
        "interest_expense": [800000, 700000],
        "other_income": [200000, 300000],
        "income_before_tax": [4400000, 6600000],
        "tax_expense": [660000, 990000],
        "net_income": [3740000, 5610000],
        "shares_outstanding": [10000000, 10000000],
    },
    "cash_flow": {
        "operating_cash_flow": [4500000, 6800000],
        "investing_cash_flow": [-2000000, -2500000],
        "financing_cash_flow": [-1500000, -2000000],
        "net_cash_flow": [1000000, 2300000],
    }
}