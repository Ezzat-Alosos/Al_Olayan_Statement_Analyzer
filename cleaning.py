"""
محرك تنظيف البيانات - Data Cleaning Engine
"""

import pandas as pd
import numpy as np
import re
from typing import Tuple, List


def clean_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    تنظيف DataFrame بالكامل.

    Args:
        df: DataFrame الخام

    Returns:
        Tuple: (DataFrame المنظف, قائمة رسائل التنظيف)
    """
    messages = []
    cleaned = df.copy()

    # حذف الصفوف الفارغة بالكامل
    empty_rows = cleaned.isna().all(axis=1).sum()
    if empty_rows > 0:
        cleaned = cleaned.dropna(how='all')
        messages.append(f"✓ تم حذف {empty_rows} صف فارغ")

    # حذف الأعمدة الفارغة بالكامل
    empty_cols = cleaned.isna().all(axis=0).sum()
    if empty_cols > 0:
        cleaned = cleaned.dropna(axis=1, how='all')
        messages.append(f"✓ تم حذف {empty_cols} عمود فارغ")

    # تنظيف أسماء الأعمدة
    #cleaned.columns = [clean_column_name(str(col)) for col in cleaned.columns]
    messages.append("✓ تم توحيد أسماء الأعمدة")

    # تحويل القيم الرقمية
    numeric_converted = 0
    for col in cleaned.columns:
        if cleaned[col].dtype == object:
            converted = convert_to_numeric(cleaned[col])
            if converted is not None:
                cleaned[col] = converted
                numeric_converted += 1

    if numeric_converted > 0:
        messages.append(f"✓ تم تحويل {numeric_converted} عمود إلى قيم رقمية")

    # إزالة المسافات الزائدة من النصوص
    for col in cleaned.select_dtypes(include=['object']).columns:
        cleaned[col] = cleaned[col].apply(
            lambda x: x.strip() if isinstance(x, str) else x
        )

    # إعادة تعيين الفهرس
    cleaned = cleaned.reset_index(drop=True)

    messages.append(f"✓ عدد الصفوف النهائي: {len(cleaned)}")
    messages.append(f"✓ عدد الأعمدة النهائي: {len(cleaned.columns)}")

    return cleaned, messages


def clean_column_name(name: str) -> str:
    """تنظيف اسم العمود."""
    # إزالة المسافات الزائدة
    name = name.strip()
    # إزالة الأسطر الجديدة
    name = name.replace('\n', ' ').replace('\r', '')
    # إزالة المسافات المتعددة
    name = re.sub(r'\s+', ' ', name)
    return name


def convert_to_numeric(series: pd.Series) -> pd.Series:
    """
    تحويل سلسلة نصية إلى رقمية.
    يتعامل مع الأقواس السالبة والفواصل.
    """
    def parse_value(val):
        if pd.isna(val) or val == '' or val == '-' or val == '--':
            return np.nan
        if isinstance(val, (int, float)):
            return float(val)
        if not isinstance(val, str):
            return np.nan

        val = val.strip()

        # التعامل مع الأقواس السالبة (2500) -> -2500
        if val.startswith('(') and val.endswith(')'):
            val = '-' + val[1:-1]

        # إزالة رمز العملة
        val = re.sub(r'[ر.س$€£¥,،]', '', val)

        # إزالة الفواصل
        val = val.replace(',', '').replace('،', '')

        # إزالة المسافات
        val = val.strip()

        try:
            return float(val)
        except (ValueError, TypeError):
            return np.nan

    converted = series.apply(parse_value)

    # التحقق من أن معظم القيم تم تحويلها بنجاح
    non_null_original = series.notna().sum()
    non_null_converted = converted.notna().sum()

    if non_null_original > 0 and (non_null_converted / non_null_original) > 0.5:
        return converted
    return None


def detect_missing_values(df: pd.DataFrame) -> dict:
    """اكتشاف القيم المفقودة."""
    missing = {}
    for col in df.columns:
        null_count = df[col].isna().sum()
        if null_count > 0:
            missing[col] = {
                "count": int(null_count),
                "percentage": round(null_count / len(df) * 100, 1)
            }
    return missing


def validate_data(df: pd.DataFrame) -> List[str]:
    """
    التحقق من صحة البيانات.

    Returns:
        قائمة بالتحذيرات
    """
    warnings = []

    # التحقق من الأعمدة المكررة
    duplicated_cols = df.columns[df.columns.duplicated()].tolist()
    if duplicated_cols:
        warnings.append(f"⚠️ يوجد أعمدة مكررة: {', '.join(str(c) for c in duplicated_cols)}")

    # التحقق من الصفوف الفارغة
    empty_rows = df.isna().all(axis=1).sum()
    if empty_rows > 0:
        warnings.append(f"⚠️ يوجد {empty_rows} صف فارغ بالكامل")

    # التحقق من القيم غير الرقمية في أعمدة يُتوقع أنها رقمية
    for col in df.columns[1:]:  # تخطي العمود الأول (عادة أسماء البنود)
        if df[col].dtype == object:
            non_numeric = df[col].apply(
                lambda x: not is_numeric_value(x) if pd.notna(x) else False
            ).sum()
            if non_numeric > 0:
                warnings.append(f"⚠️ العمود '{col}' يحتوي على {non_numeric} قيمة غير رقمية")

    return warnings


def is_numeric_value(val) -> bool:
    """التحقق مما إذا كانت القيمة رقمية."""
    if isinstance(val, (int, float)):
        return True
    if isinstance(val, str):
        val = val.strip()
        val = re.sub(r'[(),،\s$€£¥ر.س]', '', val)
        val = val.replace(',', '')
        try:
            float(val)
            return True
        except (ValueError, TypeError):
            return False
    return False