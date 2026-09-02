"""
محرك تصدير CSV - CSV Export Engine
"""

import io
import csv
from datetime import datetime
from typing import Dict, List, Optional


def generate_csv_report(
    analysis_data: Dict,
    mapped_data: Dict[str, List[float]],
    periods: List[str],
) -> Optional[str]:
    """
    توليد تقرير CSV.

    Returns:
        str: محتوى ملف CSV
    """
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)

    # العناوين
    writer.writerow(["البند"] + periods + ["ملاحظات"])

    # البيانات
    item_labels = {
        "cash": "النقدية", "receivables": "الذمم المدينة",
        "inventory": "المخزون", "total_assets": "إجمالي الأصول",
        "total_liabilities": "إجمالي الخصوم", "total_equity": "حقوق الملكية",
        "revenue": "الإيرادات", "cost_of_sales": "تكلفة المبيعات",
        "gross_profit": "مجمل الربح", "operating_income": "الربح التشغيلي",
        "net_income": "صافي الربح",
        "operating_cash_flow": "التدفقات التشغيلية",
        "investing_cash_flow": "التدفقات الاستثمارية",
        "financing_cash_flow": "التدفقات التمويلية",
    }

    for key, values in mapped_data.items():
        label = item_labels.get(key, key)
        writer.writerow([label] + values + [""])

    # فاصل
    writer.writerow([])
    writer.writerow(["النسب المالية"])
    writer.writerow(["النسبة", "القيمة", "الحالة"])

    ratios = analysis_data.get("financial_ratios", {})
    for category in ["liquidity", "profitability", "activity", "leverage"]:
        for key, data in ratios.get(category, {}).items():
            value = data.get("value")
            if value is not None:
                if data.get("is_percentage"):
                    formatted = f"{value * 100:.2f}%"
                elif data.get("is_amount"):
                    formatted = f"{value:,.0f}"
                else:
                    formatted = f"{value:.2f}"
                writer.writerow([data.get("label", key), formatted, ""])

    # درجة الصحة المالية
    writer.writerow([])
    health = analysis_data.get("health_score", {})
    if health:
        writer.writerow(["درجة الصحة المالية", health.get("total_score", 0), health.get("classification", {}).get("label", "")])

    return output.getvalue()


def get_csv_filename(company_name: str, periods: List[str]) -> str:
    """توليد اسم ملف CSV."""
    date_str = datetime.now().strftime("%Y%m%d")
    period_str = "-".join(periods) if periods else ""
    company = company_name.replace(" ", "_") if company_name else "تقرير"
    return f"{company}_{period_str}_مؤشرات_مالية_{date_str}.csv"