"""Módulo para as funções de criação de tasks."""

from crewai import Task

from src.crew.agents import (
    create_researcher_agent,
    create_conversational_agent,
    create_expert_agent,
)


def create_researcher_task(access_level: str, category: str) -> Task:
    """
    Função para criar a task do agente pesquisador.
    """
    return Task(
        agent=create_researcher_agent(access_level, category),
        description="Montar queries para serem feitas no Elastic, "
        "da melhor forma possível, para simplificar a "
        "necessidade da pessoa escrever muito para que tenha "
        "bons resultados. Esta é a pergunta feita: {query}",
        expected_output="Query para ser feita no ElasticSearch.",
    )


def create_conversational_task() -> Task:
    """
    Função para criar a task do agente conversacional.
    """
    return Task(
        agent=create_conversational_agent(),
        description="Ler os trechos dos documentos encontrados e "
        "apresentar de forma expositiva. IMPORTANTE: Ao final de cada "
        "trecho citado, você deve colocar uma tag especial [FONTE: nome_do_documento] "
        "para indicar de qual documento aquele trecho foi extraído. "
        "Esta é a pergunta feita: {query}",
        expected_output="Texto explicativo com os trechos dos "
        "documentos encontrados, com indicação de fonte para cada trecho.",
    )


def create_expert_task() -> Task:
    """
    Função para criar a task do agente perito.
    """
    return Task(
        agent=create_expert_agent(),
        description="Responder dúvidas específicas e dar "
        "direcionamentos mais aplicados, se preocupando "
        "sempre em recomendar que a pessoa fale com um "
        "especialista na área. Esta é a pergunta feita: {query}",
        expected_output="Resposta específica para a dúvida "
        "apresentada, com recomendações de conversar com um "
        "quando necessário.",
    )
