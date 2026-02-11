# pages/3_Analytics.py  или 3_📊_Analytics.py
import streamlit as st
from components.analytics_panel import render_analytics_page

def main():
    account = st.session_state.get("current_account", "AI_Girl_1")
    render_analytics_page(account)

if __name__ == "__main__":
    main()
