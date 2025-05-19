"""Módulo da aplicação Streamlit para a POC do projeto"""

import os

import requests
import streamlit as st

from src.streamlit.pages import main_page
from src.schemas.user import AcessLevel

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME") or "admin"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD") or "admin"
ADMIN_NAME = os.getenv("ADMIN_NAME") or "admin"
ADMIN_ACCESS_LEVEL = AcessLevel.ADMIN
BASE_API_URL = os.getenv("BASE_API_URL", "http://localhost:5000")

st.set_page_config(
    page_title="POC - Streamlit",
    page_icon=":guardsman:",
    layout="wide",
)

st.title("HealthCom - POC")
st.subheader("Aplicação de Prova de Conceito (POC) para o projeto HealthCom")


def create_admin_user():
    """
    Cria um usuário administrador no banco de dados, se não existir.
    """
    requests.post(
        f"{BASE_API_URL}/api/v1/user",
        json={
            "name": ADMIN_NAME,
            "user_name": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD,
            "access_level": ADMIN_ACCESS_LEVEL.value
        }
    )


if __name__ == "__main__":
    create_admin_user()
    main_page()
