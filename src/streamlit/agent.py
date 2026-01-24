"Módulo para a página de chat com os agents"

import logging
import re
import sys
import requests
import os

import streamlit as st

from src.crew.crew import create_crew

BASE_API_URL = os.getenv("BASE_API_URL", "http://localhost:5000")

# Inicializar session state
if "found_documents" not in st.session_state:
    st.session_state.found_documents = []


class StreamToExpander:
    def __init__(self, expander):
        self.expander = expander
        self.colors = ['red', 'green', 'blue', 'orange', 'purple', 'pink']
        self.color_index = 0
        self.line_buffer = ""
        self.full_log = ""

    def write(self, data):
        self.line_buffer += data

        if "\n" in self.line_buffer:
            lines = self.line_buffer.split('\n')
            # The last element is the partial line (or empty string if ends with \n)
            self.line_buffer = lines.pop()

            for line in lines:
                self.process_line(line)

            # Update the UI with the full log accumulated so far
            self.expander.markdown(self.full_log, unsafe_allow_html=True)

    def process_line(self, line):
        # 1. Clean ANSI
        cleaned_line = re.sub(r'\x1B\[[0-9;]*[mK]', '', line)

        # 2. Detect Tasks (Toast)
        task_match = re.search(r'"task"\s*:\s*"(.*?)"', cleaned_line, re.IGNORECASE)
        task_match_input = re.search(r'task\s*:\s*([^\n]*)', cleaned_line, re.IGNORECASE)
        if task_match:
            st.toast(":robot_face: " + task_match.group(1))
        elif task_match_input:
            st.toast(":robot_face: " + task_match_input.group(1).strip())

        # 3. Detect Tool Calls (Toast + Highlight)
        if "Action:" in cleaned_line:
            match = re.search(r'Action\s*:\s*(.*)', cleaned_line, re.IGNORECASE)
            if match:
                tool = match.group(1).strip()
                st.toast(f":hammer_and_wrench: Tool: {tool}")
                cleaned_line = cleaned_line.replace(match.group(0), f":orange[**Action:** {tool}]")

        if "Action Input:" in cleaned_line:
            match = re.search(r'Action Input\s*:\s*(.*)', cleaned_line, re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                cleaned_line = cleaned_line.replace(match.group(0), f":orange[**Action Input:** {val}]")

        # 4. Coloring Agent Names and Phrases
        if "Entering new CrewAgentExecutor chain" in cleaned_line:
            self.color_index = (self.color_index + 1) % len(self.colors)
            cleaned_line = cleaned_line.replace(
                "Entering new CrewAgentExecutor chain",
                f":{self.colors[self.color_index]}[Entering new CrewAgentExecutor chain]"
            )

        agents = [
            "Gerente de Projetos Sênior e Consultor de Saúde",
            "Pesquisador Acadêmico PhD",
            "Brigadeiro Médico da Aeronáutica",
            "Apresentador de Televisão Aposentado"
        ]
        for agent in agents:
            if agent in cleaned_line:
                cleaned_line = cleaned_line.replace(
                    agent,
                    f":{self.colors[self.color_index]}[{agent}]"
                )

        if "Finished chain." in cleaned_line:
            cleaned_line = cleaned_line.replace(
                "Finished chain.",
                f":{self.colors[self.color_index]}[Finished chain.]"
            )

        # Append to full log with double space for markdown line break
        self.full_log += cleaned_line + "  \n"

    def flush(self):
        if self.line_buffer:
            self.process_line(self.line_buffer)
            self.line_buffer = ""
            self.expander.markdown(self.full_log, unsafe_allow_html=True)


class StreamToLogger(logging.Handler):
    """
    Custom logging handler that sends logs to the StreamToExpander.
    """
    def __init__(self, stream_expander):
        super().__init__()
        self.stream_expander = stream_expander

    def emit(self, record):
        try:
            msg = self.format(record)
            self.stream_expander.write(msg + "\n")
        except Exception:
            self.handleError(record)


def extract_and_display_documents(response_text, search_docs):
    """
    Extrai os documentos citados na resposta e exibe um indicador visual.
    Utiliza os documentos encontrados na busca.
    """
    # Converter CrewOutput para string se necessário
    if not isinstance(response_text, str):
        response_text = str(response_text)
    
    # Se houver documentos da busca, usá-los
    if not search_docs:
        st.info("Nenhum documento foi consultado nesta busca.")
        return
    
    st.subheader("Documentos Utilizados", divider="orange")
    
    try:
        # Buscar lista de todos os documentos
        access_level = st.session_state.get("access_level", 0)
        response = requests.get(
            f"{BASE_API_URL}/api/v1/document/list",
            params={"access_level": access_level},
            timeout=10
        )
        
        if response.status_code == 200:
            todos_docs = response.json().get("documents", [])
            
            # Exibir documentos encontrados na busca
            cols = st.columns(min(3, len(search_docs)))
            
            for idx, doc in enumerate(search_docs):
                col = cols[idx % len(cols)]
                doc_id = str(doc.get("id", ""))
                
                with col:
                    with st.container(border=True):
                        st.markdown(f"**{doc.get('filename', 'Sem nome')}**")
                        st.caption(f"Categoria: {doc.get('category', 'N/A')}")
                        st.caption(f"Enviado por: {doc.get('uploaded_by', 'N/A')}")
                        
                        if st.button("Ver", key=f"view_doc_{doc_id}"):
                            st.session_state.selected_doc = doc_id
                            st.session_state.view_mode = "markdown"
                            st.rerun()
    except requests.RequestException as e:
        st.warning(f"Erro ao exibir documentos: {str(e)}")


def agent_chat(access_level, category, query):
    """Função para o chat com os agents com interface visual detalhada"""
    st.subheader("Orquestração de Agentes")
    
    # Timeline visual
    timeline_col1, timeline_col2, timeline_col3, timeline_col4 = st.columns(4)
    
    with timeline_col1:
        manager_container = st.empty()
    with timeline_col2:
        researcher_container = st.empty()
    with timeline_col3:
        conversational_container = st.empty()
    with timeline_col4:
        expert_container = st.empty()
    
    # Containers para logs detalhados
    logs_expander = st.expander("Logs de Execução", expanded=False)
    
    # Seção de detalhes dos documentos encontrados
    documents_expander = st.expander("Documentos Encontrados", expanded=False)
    
    # Atualizar timeline inicial
    with manager_container.container(border=True):
        st.markdown("### Gerente\n**Status:** Iniciando...")
    
    with researcher_container.container(border=True):
        st.markdown("### Pesquisador\n**Status:** Aguardando...")
    
    with conversational_container.container(border=True):
        st.markdown("### Apresentador\n**Status:** Aguardando...")
    
    with expert_container.container(border=True):
        st.markdown("### Perito\n**Status:** Aguardando...")
    
    # Executar crew
    with st.status("Agentes em execução...", state="running", expanded=True) as status_box:
        # Logs
        with logs_expander:
            logs_container = st.empty()
        
        # Setup Capture
        stream_expander = StreamToExpander(logs_container)
        
        # 1. Capture stdout
        old_stdout = sys.stdout
        sys.stdout = stream_expander
        
        # 2. Capture logging
        logger = logging.getLogger()
        old_level = logger.getEffectiveLevel()
        logger.setLevel(logging.INFO)
        
        log_handler = StreamToLogger(stream_expander)
        formatter = logging.Formatter('%(message)s')
        log_handler.setFormatter(formatter)
        logger.addHandler(log_handler)
        
        try:
            # Atualizar timeline - Gerente
            with manager_container.container(border=True):
                st.markdown("### Gerente\n**Status:** Coordenando agentes...")
            
            # Atualizar timeline - Pesquisador
            with researcher_container.container(border=True):
                st.markdown("### Pesquisador\n**Status:** Buscando documentos...")
            
            health_com_crew = create_crew(
                access_level=access_level,
                category=category
            )
            
            result = health_com_crew.kickoff(
                inputs={"query": query}
            )
            
            # Atualizar timeline - Conversational
            with conversational_container.container(border=True):
                st.markdown("### Apresentador\n**Status:** Estruturando resposta...")
            
            # Atualizar timeline - Expert
            with expert_container.container(border=True):
                st.markdown("### Perito\n**Status:** Validando e recomendando...")
            
            # Resultado
            result_str = str(result)
        finally:
            sys.stdout.flush()
            sys.stdout = old_stdout
            
            # Remove handler and restore level
            logger.removeHandler(log_handler)
            logger.setLevel(old_level)
        
        status_box.update(label="Agentes finalizados!", state="complete", expanded=False)
    
    # Timeline final
    with manager_container.container(border=True):
        st.markdown("### Gerente\n**Status:** Coordenação completa")
    
    with researcher_container.container(border=True):
        st.markdown("### Pesquisador\n**Status:** Busca concluída")
    
    with conversational_container.container(border=True):
        st.markdown("### Apresentador\n**Status:** Resposta estruturada")
    
    with expert_container.container(border=True):
        st.markdown("### Perito\n**Status:** Validação completa")
    
    # Sincronizar documentos encontrados da busca
    found_docs_list = []
    try:
        from src.crew.tools import search_results as sr
        if sr and sr.get("documents"):
            found_docs_list = sr["documents"]
            st.session_state.found_documents = found_docs_list
    except (ImportError, AttributeError) as e:
        st.warning(f"Não foi possível recuperar documentos da busca: {str(e)}")
    
    # Mostrar documentos encontrados
    with documents_expander:
        if found_docs_list:
            st.success(f"**{len(found_docs_list)} documentos encontrados:**")
            for idx, doc in enumerate(found_docs_list, 1):
                filename = doc.get("filename", "Sem nome")
                st.write(f"{idx}. {filename}")
        else:
            st.info("Nenhum documento foi consultado nesta busca.")
    
    # Resposta Final
    st.subheader("Resposta Final", divider="rainbow")
    st.markdown(result_str)
    
    # Seção de documentos utilizados
    st.divider()
    extract_and_display_documents(result_str, found_docs_list)