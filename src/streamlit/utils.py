"""Utilidades para o app Streamlit"""

import streamlit as st


def check_login():
    """Verifica se o usuário está logado"""
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.session_state["logged_in"]:
        return True
    else:
        return False
