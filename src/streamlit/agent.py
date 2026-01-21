"""Módulo para a página de chat com os agents"""

import re
import sys
import requests

import streamlit as st

from src.crew.crew import create_crew

BASE_API_URL = st.session_state.get("BASE_API_URL", "http://localhost:5000")


class StreamToExpander:
    def __init__(self, expander):
        self.expander = expander
        self.buffer = []
        self.colors = ['red', 'green', 'blue', 'orange', 'purple', 'pink']
        self.color_index = 0  # Initialize color index

    def write(self, data):
        # Filter out ANSI escape codes using a regular expression
        cleaned_data = re.sub(r'\x1B\[[0-9;]*[mK]', '', data)

        # Check if the data contains 'task' information
        task_match_object = re.search(
            r'\"task\"\s*:\s*\"(.*?)\"', cleaned_data, re.IGNORECASE)
        task_match_input = re.search(
            r'task\s*:\s*([^\n]*)', cleaned_data, re.IGNORECASE)
        task_value = None
        if task_match_object:
            task_value = task_match_object.group(1)
        elif task_match_input:
            task_value = task_match_input.group(1).strip()

        if task_value:
            st.toast(":robot_face: " + task_value)

        # Check if the text contains the specified phrase and apply color
        if "Entering new CrewAgentExecutor chain" in cleaned_data:
            # Apply different color and switch color index
            # Increment color index and wrap around if necessary
            self.color_index = (self.color_index + 1) % len(self.colors)

            cleaned_data = cleaned_data.replace("Entering new CrewAgentExecutor chain", f":{
                                                self.colors[self.color_index]}[Entering new CrewAgentExecutor chain]")

        if "Gerente de Projetos Sênior e Consultor de Saúde" in cleaned_data:
            cleaned_data = cleaned_data.replace(
                "Gerente de Projetos Sênior e Consultor de Saúde", f":{self.colors[self.color_index]}[Gerente de Projetos Sênior e Consultor de Saúde]")
        if "Pesquisador Acadêmico PhD" in cleaned_data:
            cleaned_data = cleaned_data.replace(
                "Pesquisador Acadêmico PhD", f":{self.colors[self.color_index]}[Pesquisador Acadêmico PhD]")
        if "Brigadeiro Médico da Aeronáutica" in cleaned_data:
            cleaned_data = cleaned_data.replace(
                "Brigadeiro Médico da Aeronáutica", f":{self.colors[self.color_index]}[Brigadeiro Médico da Aeronáutica]")
        if "Apresentador de Televisão Aposentado" in cleaned_data:
            cleaned_data = cleaned_data.replace(
                "Apresentador de Televisão Aposentado", f":{self.colors[self.color_index]}[Apresentador de Televisão Aposentado]")
        if "Finished chain." in cleaned_data:
            cleaned_data = cleaned_data.replace(
                "Finished chain.", f":{self.colors[self.color_index]}[Finished chain.]")

        self.buffer.append(cleaned_data)
        if "\n" in data:
            self.expander.markdown(''.join(self.buffer),
                                   unsafe_allow_html=True)
            self.buffer = []

    def flush(self):
        # Flush any remaining data in the buffer
        if self.buffer:
            self.expander.markdown(''.join(self.buffer),
                                   unsafe_allow_html=True)
            self.buffer = []


def extract_and_display_documents(response_text):
    """
    Extrai os documentos citados na resposta e exibe um indicador visual.
    Procura por tags [FONTE: nome_do_documento]
    """
    import os
    
    # Converter CrewOutput para string se necessário
    if not isinstance(response_text, str):
        response_text = str(response_text)
    
    # Extrair todas as referências de fontes
    fonte_pattern = r'\[FONTE:\s*([^\]]+)\]'
    fontes = re.findall(fonte_pattern, response_text, re.IGNORECASE)
    
    if not fontes:
        return
    
    # Remover duplicatas mantendo ordem
    fontes_unicas = []
    seen = set()
    for fonte in fontes:
        fonte_limpa = fonte.strip()
        if fonte_limpa not in seen:
            fontes_unicas.append(fonte_limpa)
            seen.add(fonte_limpa)
    
    st.subheader("📚 Documentos Utilizados", divider="orange")
    
    # Buscar detalhes dos documentos
    BASE_API_URL = os.getenv("BASE_API_URL", "http://localhost:5000")
    
    try:
        # Buscar lista de todos os documentos
        access_level = st.session_state.get("access_level", 0)
        response = requests.get(
            f"{BASE_API_URL}/api/v1/document/list",
            params={"access_level": access_level}
        )
        
        if response.status_code == 200:
            todos_docs = response.json().get("documents", [])
            
            # Criar mapa nome -> documento
            docs_map = {doc.get("filename", ""): doc for doc in todos_docs}
            
            # Exibir documentos encontrados
            cols = st.columns(min(3, len(fontes_unicas)))
            
            for idx, fonte in enumerate(fontes_unicas):
                col = cols[idx % len(cols)]
                
                if fonte in docs_map:
                    doc = docs_map[fonte]
                    with col:
                        with st.container(border=True):
                            st.markdown(f"**📄 {doc.get('filename', fonte)}**")
                            st.caption(f"Categoria: {doc.get('category', 'N/A')}")
                            st.caption(f"Enviado por: {doc.get('uploaded_by', 'N/A')}")
                            
                            # Botão para visualizar
                            if st.button(f"👁️ Ver", key=f"view_doc_{doc.get('id')}"):
                                st.session_state.selected_doc = doc.get("id")
                                st.session_state.view_mode = "markdown"
                else:
                    with col:
                        with st.container(border=True):
                            st.markdown(f"**📄 {fonte}**")
                            st.caption("Documento não encontrado no sistema")
    except Exception as e:
        st.warning(f"Erro ao exibir documentos: {str(e)}")


def agent_chat(access_level, category, query):
    """Função para o chat com os agents"""
    st.subheader("Chat com os Agents")

    with st.status("🤖 **Os agentes estão trabalhando...**", state="running", expanded=True) as status:
        with st.container(height=500, border=False):
            sys.stdout = StreamToExpander(st)
            health_com_crew = create_crew(
                access_level=access_level,
                category=category
            )
            output_placeholder = st.empty()
            result = health_com_crew.kickoff(
                inputs={"query": query}
            )
            # Converter CrewOutput para string
            result_str = str(result)
            output_placeholder.markdown(result_str)

        status.update(label="✅ **Os agentes terminaram!**",
                      state="complete", expanded=False)

    st.subheader("Aqui está sua resposta", anchor=False, divider="rainbow")
    st.markdown(result_str)
    
    # Extrair e exibir documentos usados
    extract_and_display_documents(result_str)
