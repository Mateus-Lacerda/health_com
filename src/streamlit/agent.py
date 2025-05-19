"""Módulo para a página de chat com os agents"""

import re
import sys

import streamlit as st

from src.crew.crew import create_crew


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
            output_placeholder.markdown(result)

        status.update(label="✅ Review Ready!",
                      state="complete", expanded=False)

    # st.subheader("Here is your Trip Plan", anchor=False, divider="rainbow")
    st.subheader("Here is your Review", anchor=False, divider="rainbow")
    st.markdown(result)
