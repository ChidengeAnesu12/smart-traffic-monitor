"""
Sidebar component for the Streamlit dashboard.
"""

import streamlit as st


def render_sidebar() -> str:
    """Render sidebar and return selected page."""
    with st.sidebar:
        st.image(
            "https://img.icons8.com/color/96/traffic-jam.png",
            width=80
        )
        st.title("Traffic Monitor")
        st.markdown("---")

        page = st.radio(
            "Navigation",
            options=[
                "Live Processing",
                "Analytics",
                "Session History",
            ],
            index=0,
        )

        st.markdown("---")
        st.caption("Smart Traffic Monitor v1.0")
        st.caption("Powered by YOLOv8 + DeepSORT")

    return page