"""
Smart Traffic Monitor — Streamlit Dashboard
Main entry point. Run with: streamlit run dashboard/app.py
"""

import sys
import streamlit as st
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))
sys.path.append(str(Path(__file__).resolve().parent))

from components.sidebar import render_sidebar
from pages.live_processing import render_live_processing
from pages.analytics_page import render_analytics
from pages.history_page import render_history

# Page config
st.set_page_config(
    page_title="Smart Traffic Monitor",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 1rem;}
    </style>
""", unsafe_allow_html=True)


def main():
    page = render_sidebar()

    if page == "Live Processing":
        render_live_processing()
    elif page == "Analytics":
        render_analytics()
    elif page == "Session History":
        render_history()


if __name__ == "__main__":
    main()