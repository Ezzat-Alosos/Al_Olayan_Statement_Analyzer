"""
محرك التحليل المالي - Analysis Engine
يجمع جميع خوارزميات وحسابات التحليل المالي
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from config import RATIO_THRESHOLDS, HEALTH_SCORE_WEIGHTS, HEALTH_SCORE_LABELS, COLUMN_MAPPING_DICTIONARY, FINANCIAL_ITEMS

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. Mapping (مطابقة الأعمدة)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def auto_suggest_mappings(df: pd.DataFrame) -> Dict[str, str]:
    """اقتراح مطابقات تلقائية."""
    suggestions = {}
    if df.empty:
        return suggestions
    first_col = df.columns[0]
    items_series = df[first_col].astype(str).str.strip().str.lower()
    for item_key, synonyms in COLUMN_MAPPING_DICTIONARY.items():
        for synonym in synonyms:
            synonym_lower = synonym.lower().strip()
            mask = items_series == synonym_lower
            if mask.any():
                suggestions[item_key] = synonym
                break
    return suggestions

def extract_mapped_data(df: pd.DataFrame, periods: List[str]) -> Dict[str, List[float]]:
    """استخراج البيانات المطابقة."""
    mapped_data = {}
    if df.empty:
        return mapped_data
    first_col = df.columns[0]
    items_series = df[first_col].astype(str).str.strip().str.lower()
    for item_key, synonyms in COLUMN_MAPPING_DICTIONARY.items():
        for synonym in synonyms:
            synonym_lower = synonym.lower().strip()
            mask = items_series == synonym_lower
            if mask.any():
                row_idx = mask.idxmax()
                row_data = df.iloc[row_idx]
                values = [float(row_data[p_col]) if pd.notna(row_data[p_col]) else 0.0 for p_col in periods if p_col in df.columns]
                if any(v != 0 for v in values):
                    mapped_data[item_key] = values
                break
    return mapped_data

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. Validators (التحقق من البيانات)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def get_item_label(key: str) -> str:
    labels = {
        "cash": "النقدية", "receivables": "الذمم المدينة", "inventory": "المخزون",
        "total_assets": "إجمالي الأصول", "total_liabilities": "إجمالي الخصوم",
        "total_equity": "حقوق الملكية", "revenue": "الإيرادات",
        "cost_of_sales": "تكلفة المبيعات", "gross_profit": "مجمل الربح",
        "operating_expenses": "المصاريف التشغيلية", "operating_income": "الربح التشغيلي",
        "net_income": "صافي الربح", "operating_cash_flow": "التدفقات التشغيلية",
        "investing_cash_flow": "التدفقات الاستثمارية", "financing_cash_flow": "التدفقات التمويلية",
    }
    return labels.get(key, key)

def get_unmapped_items(mapped_data: Dict[str, List[float]]) -> List[str]:
    all_items = set()
    for section in FINANCIAL_ITEMS.values():
        for key, value in section.items():
            if isinstance(value, dict) and "items" in value:
                all_items.update(value["items"].keys())
            elif isinstance(value, str):
                all_items.add(key)
    unmapped = all_items - set(mapped_data.keys())
    return [get_item_label(item) for item in unmapped]



def get_data_summary(mapped_data: Dict[str, List[float]], periods: List[str]) -> Dict:
    return {
        "num_periods": len(periods), "periods": periods,
        "num_items": len(mapped_data), "mapped_items": list(mapped_data.keys()),
        "unmapped_items": get_unmapped_items(mapped_data),
        "total_assets": mapped_data.get("total_assets", [0])[-1] if mapped_data.get("total_assets") else 0,
        "total_revenue": mapped_data.get("revenue", [0])[-1] if mapped_data.get("revenue") else 0,
    }

def validate_mapped_data(mapped_data: Dict[str, List[float]]) -> Tuple[bool, List[str], List[str]]:
    warnings, errors = [], []
    essential_items = ["total_assets", "revenue", "net_income"]
    for item in essential_items:
        if item not in mapped_data:
            warnings.append(f"⚠️ البند '{get_item_label(item)}' غير مطابق")
    positive_items = ["total_assets", "revenue", "total_equity"]
    for item in positive_items:
        if item in mapped_data:
            for i, val in enumerate(mapped_data[item]):
                if val < 0:
                    warnings.append(f"⚠️ قيمة سالبة في '{get_item_label(item)}' للفترة {i + 1}")
    if "total_assets" in mapped_data and "total_liabilities" in mapped_data and "total_equity" in mapped_data:
        for i in range(len(mapped_data["total_assets"])):
            assets = mapped_data["total_assets"][i]
            liabilities = mapped_data["total_liabilities"][i]
            equity = mapped_data["total_equity"][i]
            if assets > 0:
                diff = abs(assets - (liabilities + equity))
                if diff > assets * 0.01:
                    warnings.append(f"⚠️ الميزانية غير متوازنة في الفترة {i + 1}")
    if "revenue" in mapped_data and "cost_of_sales" in mapped_data and "gross_profit" in mapped_data:
        for i in range(len(mapped_data["revenue"])):
            rev, cos, gp = mapped_data["revenue"][i], mapped_data["cost_of_sales"][i], mapped_data["gross_profit"][i]
            if rev > 0:
                diff = abs(gp - (rev - cos))
                if diff > rev * 0.01:
                    warnings.append(f"⚠️ مجمل الربح غير متسق في الفترة {i + 1}")
    return len(errors) == 0, warnings, errors

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. Financial Ratios (النسب المالية)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def safe_divide(numerator: float, denominator: float) -> Optional[float]:
    if denominator == 0 or np.isnan(denominator) or np.isnan(numerator):
        return None
    return numerator / denominator

def calculate_all_ratios(mapped_data: Dict[str, List[float]], period_idx: int = -1) -> Dict:
    def get_val(key: str) -> float:
        values = mapped_data.get(key, [])
        return values[period_idx] if values and abs(period_idx) <= len(values) else 0.0

    cash, receivables, inventory = get_val("cash"), get_val("receivables"), get_val("inventory")
    prepaid, other_ca = get_val("prepaid"), get_val("other_current_assets")
    current_assets = cash + receivables + inventory + prepaid + other_ca
    total_assets = get_val("total_assets") or (current_assets + get_val("fixed_assets") + get_val("intangible_assets") + get_val("investments"))
    accounts_payable, short_term_loans, accrued = get_val("accounts_payable"), get_val("short_term_loans"), get_val("accrued_expenses")
    other_cl = get_val("other_current_liabilities")
    current_liabilities = accounts_payable + short_term_loans + accrued + other_cl
    long_term_loans, bonds, other_ncl = get_val("long_term_loans"), get_val("bonds"), get_val("other_non_current_liabilities")
    total_liabilities = get_val("total_liabilities") or (current_liabilities + long_term_loans + bonds + other_ncl)
    total_equity, revenue = get_val("total_equity"), get_val("revenue")
    cost_of_sales = get_val("cost_of_sales")
    gross_profit = get_val("gross_profit") or (revenue - cost_of_sales)
    operating_expenses, operating_income = get_val("operating_expenses"), get_val("operating_income") or (gross_profit - operating_expenses)
    interest_expense, net_income, shares = get_val("interest_expense"), get_val("net_income"), get_val("shares_outstanding")
    operating_cf, investing_cf, financing_cf = get_val("operating_cash_flow"), get_val("investing_cash_flow"), get_val("financing_cash_flow")

    liquidity = {
        "current_ratio": {"value": safe_divide(current_assets, current_liabilities), "label": "نسبة التداول", "formula": "الأصول المتداولة ÷ الخصوم المتداولة"},
        "quick_ratio": {"value": safe_divide(current_assets - inventory, current_liabilities), "label": "نسبة السيولة السريعة", "formula": "(الأصول المتداولة - المخزون) ÷ الخصوم المتداولة"},
        "cash_ratio": {"value": safe_divide(cash, current_liabilities), "label": "نسبة النقدية", "formula": "النقدية ÷ الخصوم المتداولة"},
        "working_capital": {"value": current_assets - current_liabilities, "label": "رأس المال العامل", "formula": "الأصول المتداولة - الخصوم المتداولة", "is_amount": True},
    }
    profitability = {
        "gross_margin": {"value": safe_divide(gross_profit, revenue), "label": "هامش الربح الإجمالي", "formula": "مجمل الربح ÷ الإيرادات", "is_percentage": True},
        "operating_margin": {"value": safe_divide(operating_income, revenue), "label": "هامش الربح التشغيلي", "formula": "الربح التشغيلي ÷ الإيرادات", "is_percentage": True},
        "net_margin": {"value": safe_divide(net_income, revenue), "label": "هامش صافي الربح", "formula": "صافي الربح ÷ الإيرادات", "is_percentage": True},
        "roa": {"value": safe_divide(net_income, total_assets), "label": "العائد على الأصول", "formula": "صافي الربح ÷ إجمالي الأصول", "is_percentage": True},
        "roe": {"value": safe_divide(net_income, total_equity), "label": "العائد على حقوق الملكية", "formula": "صافي الربح ÷ حقوق الملكية", "is_percentage": True},
        "eps": {"value": safe_divide(net_income, shares) if shares > 0 else None, "label": "ربحية السهم", "formula": "صافي الربح ÷ عدد الأسهم", "is_amount": True},
    }
    activity = {
        "inventory_turnover": {"value": safe_divide(cost_of_sales, inventory), "label": "معدل دوران المخزون", "formula": "تكلفة المبيعات ÷ المخزون"},
        "receivable_turnover": {"value": safe_divide(revenue, receivables), "label": "معدل دوران الذمم المدينة", "formula": "الإيرادات ÷ الذمم المدينة"},
        "asset_turnover": {"value": safe_divide(revenue, total_assets), "label": "معدل دوران الأصول", "formula": "الإيرادات ÷ إجمالي الأصول"},
        "avg_collection_period": {"value": safe_divide(365, safe_divide(revenue, receivables)) if receivables > 0 else None, "label": "متوسط فترة التحصيل (يوم)", "formula": "365 ÷ معدل دوران الذمم المدينة"},
        "days_inventory": {"value": safe_divide(365, safe_divide(cost_of_sales, inventory)) if inventory > 0 else None, "label": "أيام المخزون متوسط", "formula": "365 ÷ معدل دوران المخزون"},
    }
    leverage = {
        "debt_ratio": {"value": safe_divide(total_liabilities, total_assets), "label": "نسبة المديونية", "formula": "إجمالي الخصوم ÷ إجمالي الأصول", "is_percentage": True, "inverse": True},
        "debt_to_equity": {"value": safe_divide(total_liabilities, total_equity), "label": "الخصوم إلى حقوق الملكية", "formula": "إجمالي الخصوم ÷ حقوق الملكية", "inverse": True},
        "debt_to_assets": {"value": safe_divide(long_term_loans + short_term_loans, total_assets), "label": "الديون إلى الأصول", "formula": "(القروض قصيرة + طويلة الأجل) ÷ إجمالي الأصول", "is_percentage": True, "inverse": True},
        "interest_coverage": {"value": safe_divide(operating_income, interest_expense) if interest_expense > 0 else None, "label": "تغطية الفوائد", "formula": "الربح التشغيلي ÷ مصروف الفوائد"},
        "debt_service_coverage": {"value": safe_divide(operating_cf, short_term_loans + interest_expense) if (short_term_loans + interest_expense) > 0 else None, "label": "تغطية خدمة الدين", "formula": "التدفقات التشغيلية ÷ (أقساط + فوائد)"},
    }
    return {
        "liquidity": liquidity, "profitability": profitability, "activity": activity, "leverage": leverage,
        "cash_flow": {
            "operating_cf": {"value": operating_cf, "label": "صافي التدفقات التشغيلية", "is_amount": True},
            "investing_cf": {"value": investing_cf, "label": "صافي التدفقات الاستثمارية", "is_amount": True},
            "financing_cf": {"value": financing_cf, "label": "صافي التدفقات التمويلية", "is_amount": True},
            "net_cf": {"value": operating_cf + investing_cf + financing_cf, "label": "صافي التدفقات النقدية", "is_amount": True},
        },
        "raw_values": {
            "current_assets": current_assets, "current_liabilities": current_liabilities,
            "total_assets": total_assets, "total_liabilities": total_liabilities,
            "total_equity": total_equity, "revenue": revenue,
            "cost_of_sales": cost_of_sales, "gross_profit": gross_profit,
            "operating_income": operating_income, "net_income": net_income,
            "operating_cf": operating_cf, "investing_cf": investing_cf, "financing_cf": financing_cf,
        }
    }

def evaluate_ratio(ratio_key: str, value: Optional[float], inverse: bool = False) -> Dict:
    if value is None: return {"status": "غير متاح", "color": "#6C757D", "icon": "⚪"}
    thresholds = RATIO_THRESHOLDS.get(ratio_key)
    if not thresholds: return {"status": "محسوب", "color": "#6C757D", "icon": "⚪"}
    if inverse:
        if value <= thresholds["excellent"]: return {"status": "ممتاز", "color": "#28A745", "icon": "🟢"}
        elif value <= thresholds["good"]: return {"status": "جيد", "color": "#5CB85C", "icon": "🟢"}
        elif value <= thresholds["acceptable"]: return {"status": "مقبول", "color": "#FFA726", "icon": "🟡"}
        else: return {"status": "ضعيف", "color": "#DC3545", "icon": "🔴"}
    else:
        if value >= thresholds["excellent"]: return {"status": "ممتاز", "color": "#28A745", "icon": "🟢"}
        elif value >= thresholds["good"]: return {"status": "جيد", "color": "#5CB85C", "icon": "🟢"}
        elif value >= thresholds["acceptable"]: return {"status": "مقبول", "color": "#FFA726", "icon": "🟡"}
        else: return {"status": "ضعيف", "color": "#DC3545", "icon": "🔴"}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. Horizontal Analysis (التحليل الأفقي)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def calculate_growth_rate(previous: float, current: float) -> Optional[float]:
    if previous == 0: return 0.0 if current == 0 else None
    return ((current - previous) / abs(previous)) * 100

def calculate_horizontal_analysis(mapped_data: Dict[str, List[float]], periods: List[str]) -> Dict:
    if len(periods) < 2: return {}
    results = {}
    for item_key, values in mapped_data.items():
        if len(values) < 2: continue
        item_analysis = []
        for i in range(1, len(values)):
            current, previous = values[i], values[i - 1]
            change = current - previous
            growth_rate = calculate_growth_rate(previous, current)
            item_analysis.append({
                "period_from": periods[i - 1], "period_to": periods[i],
                "previous": previous, "current": current,
                "change": change, "growth_rate": growth_rate,
                "direction": "increase" if change > 0 else ("decrease" if change < 0 else "stable"),
            })
        results[item_key] = item_analysis
    return results

def _get_labels_h() -> Dict[str, str]:
    return {
        "cash": "النقدية", "receivables": "الذمم المدينة", "inventory": "المخزون",
        "fixed_assets": "الأصول الثابتة", "total_assets": "إجمالي الأصول",
        "accounts_payable": "الذمم الدائنة", "short_term_loans": "قروض قصيرة الأجل",
        "long_term_loans": "قروض طويلة الأجل", "total_liabilities": "إجمالي الخصوم",
        "share_capital": "رأس المال", "retained_earnings": "الأرباح المبقاة",
        "total_equity": "حقوق الملكية", "revenue": "الإيرادات",
        "cost_of_sales": "تكلفة المبيعات", "gross_profit": "مجمل الربح",
        "operating_expenses": "المصاريف التشغيلية", "operating_income": "الربح التشغيلي",
        "net_income": "صافي الربح", "operating_cash_flow": "التدفقات التشغيلية",
        "investing_cash_flow": "التدفقات الاستثمارية", "financing_cash_flow": "التدفقات التمويلية",
    }

def get_horizontal_summary(horizontal_data: Dict, mapped_data: Dict[str, List[float]]) -> Dict:
    if not horizontal_data: return {"top_increases": [], "top_decreases": []}
    changes, item_labels = [], _get_labels_h()
    for item_key, analyses in horizontal_data.items():
        if analyses:
            last = analyses[-1]
            if last["growth_rate"] is not None:
                changes.append({
                    "item": item_labels.get(item_key, item_key), "key": item_key,
                    "growth_rate": last["growth_rate"], "change": last["change"],
                    "direction": last["direction"],
                })
    sorted_changes = sorted(changes, key=lambda x: x["growth_rate"], reverse=True)
    return {
        "top_increases": [c for c in sorted_changes if c["growth_rate"] > 0][:5],
        "top_decreases": [c for c in sorted_changes if c["growth_rate"] < 0][-5:],
        "all_changes": sorted_changes,
    }

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. Vertical Analysis (التحليل الرأسي)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def calculate_vertical_analysis(mapped_data: Dict[str, List[float]], periods: List[str]) -> Dict:
    results = {"balance_sheet": {}, "income_statement": {}}
    total_assets_values = mapped_data.get("total_assets", [])
    if not total_assets_values: return results
    balance_items = ["cash", "receivables", "inventory", "prepaid", "other_current_assets", "fixed_assets", "intangible_assets", "investments", "accounts_payable", "short_term_loans", "accrued_expenses", "long_term_loans", "bonds", "share_capital", "retained_earnings", "reserves", "total_liabilities", "total_equity"]
    for item_key in balance_items:
        if item_key in mapped_data and total_assets_values:
            percentages = [round((val / total_assets_values[i]) * 100, 2) if i < len(total_assets_values) and total_assets_values[i] != 0 else 0.0 for i, val in enumerate(mapped_data[item_key])]
            results["balance_sheet"][item_key] = percentages
    revenue_values = mapped_data.get("revenue", [])
    if not revenue_values: return results
    income_items = ["cost_of_sales", "gross_profit", "operating_expenses", "operating_income", "interest_expense", "other_income", "income_before_tax", "tax_expense", "net_income"]
    for item_key in income_items:
        if item_key in mapped_data and revenue_values:
            percentages = [round((val / revenue_values[i]) * 100, 2) if i < len(revenue_values) and revenue_values[i] != 0 else 0.0 for i, val in enumerate(mapped_data[item_key])]
            results["income_statement"][item_key] = percentages
    return results

def _get_labels_v() -> Dict[str, str]:
    return {
        "cash": "النقدية", "receivables": "الذمم المدينة", "inventory": "المخزون",
        "prepaid": "مصروفات مدفوعة مقدماً", "other_current_assets": "أصول متداولة أخرى",
        "fixed_assets": "الأصول الثابتة", "intangible_assets": "الأصول غير الملموسة",
        "investments": "الاستثمارات", "accounts_payable": "الذمم الدائنة",
        "short_term_loans": "قروض قصيرة الأجل", "accrued_expenses": "مصروفات مستحقة",
        "long_term_loans": "قروض طويلة الأجل", "bonds": "سندات",
        "share_capital": "رأس المال", "retained_earnings": "الأرباح المبقاة",
        "reserves": "الاحتياطيات", "total_liabilities": "إجمالي الخصوم",
        "total_equity": "حقوق الملكية", "cost_of_sales": "تكلفة المبيعات",
        "gross_profit": "مجمل الربح", "operating_expenses": "المصاريف التشغيلية",
        "operating_income": "الربح التشغيلي", "interest_expense": "مصروف الفوائد",
        "other_income": "إيرادات أخرى", "income_before_tax": "الربح قبل الضريبة",
        "tax_expense": "مصروف الضريبة", "net_income": "صافي الربح",
    }

def get_vertical_summary(vertical_data: Dict, periods: List[str]) -> Dict:
    labels = _get_labels_v()
    summary = {"balance_sheet": [], "income_statement": []}
    for item_key, percentages in vertical_data.get("balance_sheet", {}).items():
        if percentages:
            summary["balance_sheet"].append({"item": labels.get(item_key, item_key), "key": item_key, "percentage": percentages[-1], "all_periods": percentages})
    for item_key, percentages in vertical_data.get("income_statement", {}).items():
        if percentages:
            summary["income_statement"].append({"item": labels.get(item_key, item_key), "key": item_key, "percentage": percentages[-1], "all_periods": percentages})
    summary["balance_sheet"].sort(key=lambda x: abs(x["percentage"]), reverse=True)
    summary["income_statement"].sort(key=lambda x: abs(x["percentage"]), reverse=True)
    return summary

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. Rule Engine (محرك القواعد)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def generate_comments(ratios: Dict, horizontal_data: Dict, mapped_data: Dict[str, List[float]]) -> Dict[str, List[str]]:
    comments = {"liquidity": [], "profitability": [], "activity": [], "leverage": [], "cash_flow": [], "general": []}
    cr = ratios.get("liquidity", {}).get("current_ratio", {}).get("value")
    if cr is not None:
        if cr >= 2.0: comments["liquidity"].append("نسبة التداول مرتفعة...")
        elif cr >= 1.5: comments["liquidity"].append("نسبة التداول في مستوى جيد...")
        elif cr >= 1.0: comments["liquidity"].append("نسبة التداول مقبولة...")
        else: comments["liquidity"].append("⚠️ نسبة التداول منخفضة...")
    nm = ratios.get("profitability", {}).get("net_margin", {}).get("value")
    if nm is not None:
        if nm >= 0.15: comments["profitability"].append("هامش صافي الربح ممتاز...")
        elif nm >= 0.08: comments["profitability"].append("هامش صافي الربح جيد...")
        elif nm >= 0.03: comments["profitability"].append("هامش صافي الربح مقبول...")
        elif nm < 0: comments["profitability"].append("⚠️ الشركة تحقق خسائر صافية...")
    dr = ratios.get("leverage", {}).get("debt_ratio", {}).get("value")
    if dr is not None:
        if dr <= 0.3: comments["leverage"].append("نسبة المديونية منخفضة...")
        elif dr <= 0.5: comments["leverage"].append("نسبة المديونية متوازنة...")
        else: comments["leverage"].append("⚠️ نسبة المديونية مرتفعة...")
    return comments

def identify_strengths_weaknesses(ratios: Dict, horizontal_data: Dict) -> tuple:
    strengths, weaknesses = [], []
    cr = ratios.get("liquidity", {}).get("current_ratio", {}).get("value")
    if cr is not None:
        if cr >= 1.5: strengths.append("سيولة جيدة...")
        elif cr < 1.0: weaknesses.append("ضعف السيولة...")
    nm = ratios.get("profitability", {}).get("net_margin", {}).get("value")
    if nm is not None:
        if nm >= 0.10: strengths.append("هامش ربحية مرتفع...")
        elif nm < 0.03: weaknesses.append("هامش ربحية منخفض...")
    dr = ratios.get("leverage", {}).get("debt_ratio", {}).get("value")
    if dr is not None:
        if dr <= 0.4: strengths.append("هيكل تمويلي متحفظ...")
        elif dr > 0.7: weaknesses.append("ارتفاع المديونية...")
    return strengths[:5], weaknesses[:5]

def generate_recommendations(ratios: Dict, strengths: List[str], weaknesses: List[str]) -> List[str]:
    recommendations = []
    cr = ratios.get("liquidity", {}).get("current_ratio", {}).get("value")
    if cr is not None and cr < 1.0: recommendations.append("تحسين إدارة رأس المال العامل...")
    nm = ratios.get("profitability", {}).get("net_margin", {}).get("value")
    if nm is not None and nm < 0.05: recommendations.append("مراجعة هيكل التكاليف...")
    dr = ratios.get("leverage", {}).get("debt_ratio", {}).get("value")
    if dr is not None and dr > 0.6: recommendations.append("إعادة هيكلة الديون...")
    if not recommendations: recommendations.append("الاستمرار في الأداء الحالي مع مراقبة المؤشرات المالية بشكل دوري")
    return recommendations[:6]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. Health Score (درجة الصحة المالية)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def calculate_health_score(ratios: Dict) -> Dict:
    def _score_ratio(value: float, excellent: float, good: float, acceptable: float, poor: float) -> float:
        if value >= excellent: return 95.0
        elif value >= good: return 80.0
        elif value >= acceptable: return 65.0
        elif value >= poor: return 45.0
        else: return 25.0
    def _score_ratio_inverse(value: float, excellent: float, good: float, acceptable: float, poor: float) -> float:
        if value <= excellent: return 95.0
        elif value <= good: return 80.0
        elif value <= acceptable: return 65.0
        elif value <= poor: return 45.0
        else: return 25.0
    def _get_classification(score: int) -> Dict:
        for (low, high), info in HEALTH_SCORE_LABELS.items():
            if low <= score <= high: return info
        return {"label": "غير محدد", "color": "#6C757D", "icon": "⚪"}

    category_scores = {}
    # Liquidity
    liquidity = ratios.get("liquidity", {})
    liquidity_scores = []
    cr = liquidity.get("current_ratio", {}).get("value")
    if cr is not None: liquidity_scores.append(_score_ratio(cr, 2.0, 1.5, 1.0, 0.5))
    category_scores["liquidity"] = {"score": sum(liquidity_scores) / len(liquidity_scores) if liquidity_scores else 50.0, "label": "السيولة", "weight": HEALTH_SCORE_WEIGHTS["liquidity"]}
    # Profitability
    profitability = ratios.get("profitability", {})
    profitability_scores = []
    nm = profitability.get("net_margin", {}).get("value")
    if nm is not None: profitability_scores.append(_score_ratio(nm, 0.15, 0.08, 0.03, 0.0))
    category_scores["profitability"] = {"score": sum(profitability_scores) / len(profitability_scores) if profitability_scores else 50.0, "label": "الربحية", "weight": HEALTH_SCORE_WEIGHTS["profitability"]}
    # Leverage
    leverage = ratios.get("leverage", {})
    leverage_scores = []
    dr = leverage.get("debt_ratio", {}).get("value")
    if dr is not None: leverage_scores.append(_score_ratio_inverse(dr, 0.3, 0.5, 0.7, 0.9))
    category_scores["leverage"] = {"score": sum(leverage_scores) / len(leverage_scores) if leverage_scores else 50.0, "label": "المديونية", "weight": HEALTH_SCORE_WEIGHTS["leverage"]}
    total_score = min(100, max(0, round(sum(cat["score"] * cat["weight"] for cat in category_scores.values()))))
    return {"total_score": total_score, "classification": _get_classification(total_score), "category_scores": category_scores}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 8. Summary (الملخص التنفيذي)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def generate_executive_summary(ratios: Dict, health_score: Dict, strengths: List[str], weaknesses: List[str], horizontal_data: Dict, mapped_data: Dict[str, List[float]], periods: List[str]) -> str:
    lines = []
    score = health_score.get("total_score", 0)
    classification = health_score.get("classification", {}).get("label", "غير محدد")
    lines.append(f"حصلت الشركة على درجة صحة مالية {score}/100 ({classification}).")
    revenue = mapped_data.get("revenue", [])
    if revenue: lines.append(f"بلغت الإيرادات {revenue[-1]:,.0f} ريال.")
    net_income = mapped_data.get("net_income", [])
    if net_income:
        if net_income[-1] > 0: lines.append(f"حققت الشركة صافي ربح بقيمة {net_income[-1]:,.0f} ريال.")
        else: lines.append(f"سجلت الشركة خسارة صافية بقيمة {abs(net_income[-1]):,.0f} ريال.")
    if len(periods) > 1 and horizontal_data:
        rev_growth = horizontal_data.get("revenue", [])
        if rev_growth:
            growth_rate = rev_growth[-1].get("growth_rate")
            if growth_rate is not None:
                if growth_rate > 0: lines.append(f"نمت الإيرادات بنسبة {growth_rate:.1f}% مقارنة بالفترة السابقة.")
                else: lines.append(f"انخفضت الإيرادات بنسبة {abs(growth_rate):.1f}% مقارنة بالفترة السابقة.")
    cr = ratios.get("liquidity", {}).get("current_ratio", {}).get("value")
    if cr is not None:
        if cr >= 1.5: lines.append("وضع السيولة مريح ويمكّن الشركة من الوفاء بالتزاماتها.")
        elif cr < 1.0: lines.append("وضع السيولة يحتاج إلى اهتمام لتجنب مخاطر السداد.")
    return " ".join(lines[:8])

def get_best_indicators(ratios: Dict) -> List[Dict]:
    indicators, all_ratios = [], {}
    for category in ["liquidity", "profitability", "activity"]:
        for key, data in ratios.get(category, {}).items():
            if data.get("value") is not None and not data.get("is_amount"):
                all_ratios[key] = data
    for key, data in all_ratios.items():
        evaluation = evaluate_ratio(key, data["value"], data.get("inverse", False))
        if evaluation["status"] in ["ممتاز", "جيد"]:
            indicators.append({"label": data["label"], "value": data["value"], "status": evaluation["status"], "color": evaluation["color"], "icon": evaluation["icon"]})
    return indicators[:5]

def get_worst_indicators(ratios: Dict) -> List[Dict]:
    indicators, all_ratios = [], {}
    for category in ["liquidity", "profitability", "activity", "leverage"]:
        for key, data in ratios.get(category, {}).items():
            if data.get("value") is not None and not data.get("is_amount"):
                all_ratios[key] = data
    for key, data in all_ratios.items():
        evaluation = evaluate_ratio(key, data["value"], data.get("inverse", False))
        if evaluation["status"] in ["ضعيف", "مقبول"]:
            indicators.append({"label": data["label"], "value": data["value"], "status": evaluation["status"], "color": evaluation["color"], "icon": evaluation["icon"]})
    return indicators[:5]