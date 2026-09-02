"""
محرك الرسوم البيانية - Charts Engine
يستخدم Plotly لإنشاء رسوم بيانية تفاعلية
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Optional
from config import COLORS, CHART_COLORS, INDICATOR_COLORS


def get_chart_layout(title: str = "", height: int = 400) -> Dict:
    """إعدادات التخطيط الأساسية."""
    return {
        "title": {"text": title, "x": 0.5, "font": {"size": 16, "family": "Cairo"}},
        "font": {"family": "Cairo", "size": 12},
        "height": height,
        "margin": {"t": 50, "b": 50, "l": 50, "r": 50},
        "paper_bgcolor": "white",
        "plot_bgcolor": "#FAFBFC",
        "xaxis": {"gridcolor": "#E8E8E8"},
        "yaxis": {"gridcolor": "#E8E8E8"},
    }


def create_kpi_comparison_chart(
    labels: List[str],
    current_values: List[float],
    previous_values: List[float],
    title: str = "مقارنة المؤشرات الرئيسية"
) -> go.Figure:
    """رسم بياني لمقارنة KPI بين فترتين."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="الفترة السابقة",
        x=labels,
        y=previous_values,
        marker_color=CHART_COLORS[3],
        opacity=0.7,
    ))

    fig.add_trace(go.Bar(
        name="الفترة الحالية",
        x=labels,
        y=current_values,
        marker_color=CHART_COLORS[0],
    ))

    layout = get_chart_layout(title)
    layout["barmode"] = "group"
    fig.update_layout(**layout)

    return fig


def create_waterfall_chart(
    categories: List[str],
    values: List[float],
    title: str = "تحليل شلالي"
) -> go.Figure:
    """رسم بياني شلالي."""
    measures = ["relative"] * (len(values) - 1) + ["total"]

    fig = go.Figure(go.Waterfall(
        name="",
        orientation="v",
        measure=measures,
        x=categories,
        y=values,
        connector={"line": {"color": COLORS["border"]}},
        increasing={"marker": {"color": INDICATOR_COLORS["positive"]}},
        decreasing={"marker": {"color": INDICATOR_COLORS["negative"]}},
        totals={"marker": {"color": COLORS["primary"]}},
    ))

    fig.update_layout(**get_chart_layout(title))
    return fig


def create_pie_chart(
    labels: List[str],
    values: List[float],
    title: str = "",
    hole: float = 0.4
) -> go.Figure:
    """رسم بياني دائري/حلقي."""
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=hole,
        marker={"colors": CHART_COLORS},
        textinfo="label+percent",
        textfont={"family": "Cairo", "size": 11},
    ))

    fig.update_layout(**get_chart_layout(title, height=380))
    return fig


def create_line_chart(
    periods: List[str],
    series: Dict[str, List[float]],
    title: str = ""
) -> go.Figure:
    """رسم بياني خطي."""
    fig = go.Figure()

    for i, (name, values) in enumerate(series.items()):
        fig.add_trace(go.Scatter(
            x=periods,
            y=values,
            mode="lines+markers",
            name=name,
            line={"color": CHART_COLORS[i % len(CHART_COLORS)], "width": 2},
            marker={"size": 8},
        ))

    fig.update_layout(**get_chart_layout(title))
    return fig


def create_area_chart(
    periods: List[str],
    series: Dict[str, List[float]],
    title: str = ""
) -> go.Figure:
    """رسم بياني مساحي."""
    fig = go.Figure()

    for i, (name, values) in enumerate(series.items()):
        fig.add_trace(go.Scatter(
            x=periods,
            y=values,
            mode="lines",
            name=name,
            fill="tonexty" if i > 0 else "tozeroy",
            line={"color": CHART_COLORS[i % len(CHART_COLORS)]},
        ))

    fig.update_layout(**get_chart_layout(title))
    return fig


def create_bar_chart(
    categories: List[str],
    values: List[float],
    title: str = "",
    horizontal: bool = False,
    colors: Optional[List[str]] = None
) -> go.Figure:
    """رسم بياني أعمدة."""
    if colors is None:
        colors = [COLORS["primary"]] * len(values)

    if horizontal:
        fig = go.Figure(go.Bar(
            y=categories,
            x=values,
            orientation="h",
            marker_color=colors,
        ))
    else:
        fig = go.Figure(go.Bar(
            x=categories,
            y=values,
            marker_color=colors,
        ))

    fig.update_layout(**get_chart_layout(title))
    return fig


def create_stacked_bar_chart(
    categories: List[str],
    series: Dict[str, List[float]],
    title: str = ""
) -> go.Figure:
    """رسم بياني أعمدة مكدسة."""
    fig = go.Figure()

    for i, (name, values) in enumerate(series.items()):
        fig.add_trace(go.Bar(
            name=name,
            x=categories,
            y=values,
            marker_color=CHART_COLORS[i % len(CHART_COLORS)],
        ))

    layout = get_chart_layout(title)
    layout["barmode"] = "stack"
    fig.update_layout(**layout)
    return fig


def create_radar_chart(
    categories: List[str],
    values: List[float],
    title: str = "تقييم الأداء المالي"
) -> go.Figure:
    """رسم بياني رادار."""
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor=f"rgba(27, 58, 92, 0.2)",
        line={"color": COLORS["primary"], "width": 2},
        marker={"size": 6},
    ))

    fig.update_layout(
        polar={
            "radialaxis": {"visible": True, "range": [0, 100]},
            "angularaxis": {"tickfont": {"family": "Cairo"}},
        },
        **get_chart_layout(title, height=450),
    )

    return fig


def create_gauge_chart(
    value: float,
    title: str = "",
    max_value: float = 100
) -> go.Figure:
    """رسم بياني مقياس."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"family": "Cairo", "size": 14}},
        number={"font": {"family": "Cairo", "size": 28}},
        gauge={
            "axis": {"range": [0, max_value]},
            "bar": {"color": COLORS["primary"]},
            "steps": [
                {"range": [0, 40], "color": "#FFEBEE"},
                {"range": [40, 60], "color": "#FFF3E0"},
                {"range": [60, 80], "color": "#E8F5E9"},
                {"range": [80, 100], "color": "#C8E6C9"},
            ],
            "threshold": {
                "line": {"color": INDICATOR_COLORS["positive"], "width": 3},
                "thickness": 0.8,
                "value": value,
            },
        },
    ))

    fig.update_layout(height=300, margin={"t": 40, "b": 20, "l": 30, "r": 30})
    return fig


def create_treemap_chart(
    labels: List[str],
    values: List[float],
    parents: List[str],
    title: str = ""
) -> go.Figure:
    """رسم بياني شجري."""
    fig = go.Figure(go.Treemap(
        labels=labels,
        values=values,
        parents=parents,
        marker={"colors": CHART_COLORS[:len(labels)]},
        textfont={"family": "Cairo"},
    ))

    fig.update_layout(**get_chart_layout(title, height=450))
    return fig


def create_funnel_chart(
    stages: List[str],
    values: List[float],
    title: str = ""
) -> go.Figure:
    """رسم بياني قمعي."""
    fig = go.Figure(go.Funnel(
        y=stages,
        x=values,
        marker={"color": CHART_COLORS[:len(stages)]},
        textfont={"family": "Cairo"},
    ))

    fig.update_layout(**get_chart_layout(title))
    return fig


def create_scatter_chart(
    x_values: List[float],
    y_values: List[float],
    labels: List[str],
    title: str = "",
    x_title: str = "",
    y_title: str = ""
) -> go.Figure:
    """رسم بياني نقطي."""
    fig = go.Figure(go.Scatter(
        x=x_values,
        y=y_values,
        mode="markers+text",
        text=labels,
        textposition="top center",
        marker={"size": 12, "color": COLORS["primary"]},
        textfont={"family": "Cairo", "size": 10},
    ))

    layout = get_chart_layout(title)
    layout["xaxis"]["title"] = x_title
    layout["yaxis"]["title"] = y_title
    fig.update_layout(**layout)
    return fig


def create_grouped_bar_chart(
    categories: List[str],
    series: Dict[str, List[float]],
    title: str = ""
) -> go.Figure:
    """رسم بياني أعمدة مجمعة."""
    fig = go.Figure()

    for i, (name, values) in enumerate(series.items()):
        fig.add_trace(go.Bar(
            name=name,
            x=categories,
            y=values,
            marker_color=CHART_COLORS[i % len(CHART_COLORS)],
        ))

    layout = get_chart_layout(title)
    layout["barmode"] = "group"
    fig.update_layout(**layout)
    return fig


def create_cash_flow_chart(
    periods: List[str],
    operating: List[float],
    investing: List[float],
    financing: List[float],
    title: str = "التدفقات النقدية"
) -> go.Figure:
    """رسم بياني خاص بالتدفقات النقدية."""
    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="تشغيلية",
        x=periods,
        y=operating,
        marker_color=INDICATOR_COLORS["positive"],
    ))

    fig.add_trace(go.Bar(
        name="استثمارية",
        x=periods,
        y=investing,
        marker_color=INDICATOR_COLORS["warning"],
    ))

    fig.add_trace(go.Bar(
        name="تمويلية",
        x=periods,
        y=financing,
        marker_color=INDICATOR_COLORS["negative"],
    ))

    layout = get_chart_layout(title)
    layout["barmode"] = "group"
    fig.update_layout(**layout)
    return fig