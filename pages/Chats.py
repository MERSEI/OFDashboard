# pages/1_💬_Chats.py
import streamlit as st
from components.chat_layout import render_chats_page

def main():
    account = st.session_state.get("current_account", "AI_Girl_1")
    render_chats_page(account)

if __name__ == "__main__":
    main()
