"""
محرك تحميل البيانات - Data Loader
يدعم Excel (.xlsx, .xls) و CSV
"""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Optional, Tuple, List
import io


def load_file(uploaded_file) -> Tuple[Optional[pd.ExcelFile], Optional[pd.DataFrame], str]:
    """
    تحميل الملف المرفوع.

    Args:
        uploaded_file: الملف المرفوع من Streamlit

    Returns:
        Tuple: (ExcelFile أو None, DataFrame أو None, نوع الملف)
    """
    file_name = uploaded_file.name.lower()

    if file_name.endswith(('.xlsx', '.xls')):
        try:
            excel_file = pd.ExcelFile(uploaded_file)
            return excel_file, None, "excel"
        except Exception as e:
            st.error(f"❌ خطأ في قراءة ملف Excel: {str(e)}")
            return None, None, ""

    elif file_name.endswith('.csv'):
        try:
            # محاولة قراءة CSV بترميزات مختلفة
            content = uploaded_file.read()
            for encoding in ['utf-8', 'utf-8-sig', 'cp1256', 'latin1']:
                try:
                    df = pd.read_csv(io.BytesIO(content), encoding=encoding)
                    return None, df, "csv"
                except UnicodeDecodeError:
                    continue
            st.error("❌ لم يتم التعرف على ترميز الملف")
            return None, None, ""
        except Exception as e:
            st.error(f"❌ خطأ في قراءة ملف CSV: {str(e)}")
            return None, None, ""

    else:
        st.error("❌ نوع الملف غير مدعوم. يرجى رفع ملف Excel أو CSV.")
        return None, None, ""


def get_sheet_names(excel_file: pd.ExcelFile) -> List[str]:
    """الحصول على أسماء أوراق العمل."""
    return excel_file.sheet_names


def read_sheet(excel_file: pd.ExcelFile, sheet_name: str, header: Optional[int] = None) -> pd.DataFrame:
    """
    قراءة ورقة عمل محددة.

    Args:
        excel_file: ملف Excel
        sheet_name: اسم الورقة
        header: رقم صف العناوين (None لقراءة بدون عناوين)

    Returns:
        DataFrame
    """
    try:
        df = pd.read_excel(excel_file, sheet_name=sheet_name, header=header)
        return df
    except Exception as e:
        st.error(f"❌ خطأ في قراءة الورقة '{sheet_name}': {str(e)}")
        return pd.DataFrame()


def get_preview(df: pd.DataFrame, rows: int = 30) -> pd.DataFrame:
    """الحصول على معاينة للبيانات."""
    return df.head(rows)


def set_header_row(df: pd.DataFrame, header_row: int) -> pd.DataFrame:
    """
    تعيين صف العناوين وإعادة بناء DataFrame.

    Args:
        df: DataFrame الأصلي
        header_row: رقم الصف المراد استخدامه كعنوان

    Returns:
        DataFrame جديد مع العناوين الصحيحة
    """
    try:
        new_header = df.iloc[header_row]
        new_df = df.iloc[header_row + 1:].copy()
        new_df.columns = new_header.values
        new_df = new_df.reset_index(drop=True)
        return new_df
    except Exception as e:
        st.error(f"❌ خطأ في تعيين صف العناوين: {str(e)}")
        return df