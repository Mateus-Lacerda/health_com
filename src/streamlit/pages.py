"""Módulo para as páginas base da aplicação Streamlit"""
import os

import requests
import streamlit as st

from src.schemas.user import AcessLevel
from src.streamlit.agent import agent_chat
from src.streamlit.documents import view_documents

BASE_API_URL = os.getenv("BASE_API_URL", "http://localhost:5000")


# ------- Autenticação -------

def login_page():
    st.title("Login")
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    if st.button("Entrar", key="login_btn"):
        if username and password:
            response = requests.post(
                f"{BASE_API_URL}/api/v1/user/login",
                json={"user_name": username, "password": password}
            )
            if response.status_code == 200:
                data = response.json()
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["access_level"] = data.get("access_level")
                st.session_state["user_id"] = data.get("user_id")
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")
        else:
            st.warning("Por favor, preencha ambos os campos.")

# ------- Logout -------


def logout():
    for key in ["logged_in", "username", "access_level"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# ------- Páginas de Gerenciamento de Usuários -------


def add_user():
    st.subheader("Adicionar Usuário")
    name = st.text_input("Nome Completo")
    username = st.text_input("Nome de Usuário")
    password = st.text_input("Senha", type="password")
    level = st.selectbox("Nível de Acesso", [lvl.value for lvl in AcessLevel])
    if st.button("Enviar", key="add_user_btn"):
        if name and username and password:
            resp = requests.post(
                f"{BASE_API_URL}/api/v1/user",
                json={
                    "name": name,
                    "user_name": username,
                    "password": password,
                    "access_level": level
                }
            )
            if resp.status_code == 201:
                st.success("Usuário adicionado com sucesso.")
            else:
                st.error("Falha ao adicionar usuário.")
        else:
            st.warning("Preencha todos os campos.")


def list_users():
    """Função para listar usuários com paginação"""
    st.subheader("Listar Usuários")

    users_per_page = st.slider(
        "Selecione o número de usuários por página",
        min_value=1, max_value=20, value=5
    )
    page_number = st.sidebar.number_input("Página", min_value=1, value=1)
    offset = (page_number - 1) * users_per_page

    response = requests.get(
        f"{BASE_API_URL}/api/v1/user", params={"limit": users_per_page, "offset": offset}
    )

    if response.status_code == 200:
        users = response.json()
        if users:
            for user in users.get("users", []):
                st.write(
                    f"ID: {user["_id"]}, Nome: {
                        user['name']}, Usuário: {user['user_name']}, "
                    f"Nível de Acesso: {user['access_level']}, Criado em: {
                        user['created_at']}"
                )
        else:
            st.write("Nenhum usuário encontrado.")

        total_users = users.get("total", 0)
        total_pages = int(total_users) // users_per_page + \
            (1 if int(total_users) % users_per_page != 0 else 0)

        col1, col2 = st.columns([1, 1])
        with col1:
            if page_number > 1:
                if st.button("Página Anterior", key="prev_page_btn"):
                    page_number -= 1
        with col2:
            if page_number < total_pages:
                if st.button("Próxima Página", key="next_page_btn"):
                    page_number += 1

    else:
        st.error("Erro ao buscar usuários.")


def update_user():
    st.subheader("Atualizar Usuário")
    user_id = st.text_input("ID do Usuário")
    if user_id:
        get_resp = requests.get(f"{BASE_API_URL}/api/v1/user/{user_id}")
        if get_resp.status_code == 200:
            user = get_resp.json()
            name = st.text_input("Nome Completo", value=user["name"])
            username = st.text_input(
                "Nome de Usuário", value=user["user_name"])
            password = st.text_input("Senha", type="password")
            level = st.selectbox(
                "Nível de Acesso",
                [lvl.value for lvl in AcessLevel],
                index=[lvl.value for lvl in AcessLevel].index(
                    user["access_level"])
            )
            if st.button("Enviar Atualização", key="update_user_btn"):
                if name and username and password:
                    up_resp = requests.put(
                        f"{BASE_API_URL}/api/v1/user/{user_id}",
                        json={"name": name, "user_name": username,
                              "password": password, "access_level": level}
                    )
                    if up_resp.status_code == 200:
                        st.success("Usuário atualizado com sucesso.")
                    else:
                        st.error("Falha ao atualizar usuário.")
                else:
                    st.warning("Preencha todos os campos.")
        elif get_resp.status_code == 404:
            st.error("Usuário não encontrado.")
        else:
            st.error("Erro ao buscar usuário.")
    else:
        st.info("Informe um ID de usuário.")


def remove_user():
    st.subheader("Remover Usuário")
    user_id = st.text_input("ID do Usuário para remover")
    if st.button("Excluir Usuário", key="remove_user_btn"):
        if user_id:
            del_resp = requests.delete(f"{BASE_API_URL}/api/v1/user/{user_id}")
            if del_resp.status_code == 200:
                st.success("Usuário removido com sucesso.")
            else:
                st.error("Falha ao remover usuário.")
        else:
            st.warning("Informe um ID de usuário.")

# ------- Página de Envio de Arquivos -------


def upload_files():
    st.subheader("Enviar Arquivos PDF")
    files = st.file_uploader(
        "Selecione PDF(s)", type="pdf", accept_multiple_files=True)
    if files:
        for i, file in enumerate(files):
            level = st.selectbox(
                f"Nível de acesso para {file.name}",
                [lvl.value for lvl in AcessLevel],
                key=f"level_{i}"
            )
            category = st.selectbox(
                f"Categoria para {file.name}",
                ["Clínico", "Financeiro", "Administrativo"],
                key=f"cat_{i}"
            )
            user_id = st.session_state.get("user_id")
            if st.button(f"Enviar {file.name}", key=f"upload_btn_{i}"):
                resp = requests.post(
                    f"{BASE_API_URL}/api/v1/document/upload",
                    data={"access_level": level, "category": category, "user_id": user_id},
                    files={"file": (file.name, file.getvalue(), file.type)}
                )
                if resp.status_code == 200:
                    st.success(f"{file.name} enviado com sucesso.")
                else:
                    st.error(f"Falha ao enviar {file.name}, {resp.text}")

# ------- Página Principal com Navegação -------


def main_page():
    if not st.session_state.get("logged_in", False):
        login_page()
        return

    st.sidebar.title("Navegação")
    page = st.sidebar.radio("Ir para", [
                            "Início", "Gerenciamento de Usuários", "Chat com Agentes", "Enviar Arquivos", "Visualizar Documentos", "Sair"])

    if page == "Início":
        st.title("Bem-vindo ao HealthCom!")
        st.write(f"Logado como: {st.session_state['username']}")
        st.write(f"Nível de acesso: {st.session_state['access_level']}")
    elif page == "Gerenciamento de Usuários":
        if st.session_state.get("access_level") == AcessLevel.ADMIN.value:
            tabs = st.tabs(["Adicionar", "Listar", "Atualizar", "Remover"])
            with tabs[0]:
                add_user()
            with tabs[1]:
                list_users()
            with tabs[2]:
                update_user()
            with tabs[3]:
                remove_user()
        else:
            st.error("Acesso negado. Apenas administradores.")
    elif page == "Chat com Agentes":
        query = st.text_input("Digite sua pergunta:")
        if query:
            category = st.selectbox(
                "Filtrar por categoria",
                ["Clínico", "Financeiro", "Administrativo", "Todos"]
            )
            if st.button("Enviar", key="chat_send_btn"):
                agent_chat(st.session_state.get("access_level"),
                           category if category != "Todos" else None,
                           query)
    elif page == "Enviar Arquivos":
        upload_files()
    elif page == "Visualizar Documentos":
        view_documents()
    elif page == "Sair":
        logout()


if __name__ == "__main__":
    main_page()
