# pages/2_🎥_Content.py
import streamlit as st
from components.content_panel import render_content_page

def main():
    account = st.session_state.get("current_account", "AI_Girl_1")
    render_content_page(account)

if __name__ == "__main__":
    main()
