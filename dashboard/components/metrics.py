"""
Metrics display components.
"""

import streamlit as st


def render_metric_row(metrics: dict) -> None:
    """
    Render a row of metric cards.

    Args:
        metrics: dict of label -> value
    """
    cols = st.columns(len(metrics))
    for col, (label, value) in zip(cols, metrics.items()):
        col.metric(label=label, value=value)


def render_density_badge(level: str) -> None:
    """Render a colored density level badge."""
    colors = {
        "LOW":       "#28a745",
        "MODERATE":  "#ffc107",
        "HIGH":      "#fd7e14",
        "CONGESTED": "#dc3545",
    }
    color = colors.get(level, "#6c757d")
    st.markdown(
        f"""
        <div style="
            background-color: {color};
            color: white;
            padding: 8px 16px;
            border-radius: 8px;
            text-align: center;
            font-size: 18px;
            font-weight: bold;
        ">{level}</div>
        """,
        unsafe_allow_html=True,
    )