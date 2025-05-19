"""
Módulo para a classe de inicitalização da Crew de agentes.
"""

from crewai import Crew, Process

from src.crew.agents import (
    create_manager_agent,
    create_researcher_agent,
    create_conversational_agent,
    create_expert_agent,
)
from src.crew.tasks import (
    create_researcher_task,
    create_conversational_task,
    create_expert_task,
)


class HealthComCrew:
    """
    Classe para a inicialização da Crew de agentes.

    Agentes:
    - Gerente de projetos sênior e consultor de saúde:
        Backstory:
            Este agente trabalhou como consultor de saúde
            durante 20 anos, e acabou entrando na área de
            tecnologia, onde se tornou um gerente de projetos
            sênior. Ele trabalha principalmente com projetos
            relacionados à saúde, e tem um conhecimento profundo
            sobre o setor de saúde e tecnologia.
        Função:
            O gerente é o agente responsável por gerenciar
            a Crew e garantir que todos os agentes estejam
            trabalhando cada um em sua tarefa específica.

    - Pesquisador acadêmico Phd:
        Backstory:
            Este agente é um pesquisador acadêmico com PhD
            em saúde pública. Ele tem uma vasta experiência
            em pesquisa e análise de dados, e é especialista
            em encontrar informações relevantes para projetos
            de saúde.
        Função:
            O pesquisador é o agente responsável por montar queries
            para serem feitas no Elastic, da melhor forma possível,
            para simplificar a necessidade da pessoa escrever muito para
            que tenha bons resultados.

    - Apresentador de televisão aposentado:
        Backstory:
            Este agente é um apresentador de televisão aposentado
            que decidiu trabalhar em hospitais como forma de caridade.
            Ele tem uma vasta experiência em comunicação e é capaz
            de explicar conceitos complexos de forma simples e clara.
        Função:
            O conversacional é o agente que lê os trechos dos
            documentos encontrados e apresenta de forma expositiva.

    - Brigadeiro médico da Aeronáutica:
        Backstory:
            Este agente é um brigadeiro médico da Aeronáutica
            que tem uma vasta experiência em medicina e saúde
            pública. Ele é versado em questões de saúde, mas
            brilha mesmo na parte burocrática de segurança
            pública. Tendo feito um curso de LGPD nas últimas
            férias, ele sabe o que sabe, e sabe quando deve
            recomendar que a pessoa procure alguém com mais
            experiência real na área.
            (Ele entende mesmo é de papelada e hinos militares).
        Função:
            O perito é o agente que responde dúvidas específicas
            e pode dar direcionamentos mais aplicados,
            se preocupando sempre em recomendar que a pessoa
            fale com um especialista na área
    """

    def __init__(self, access_level: str, category: str) -> None:
        """
        Inicializa a Crew de agentes.
        """
        self.crew = Crew(
            tasks=[
                create_researcher_task(access_level, category),
                create_conversational_task(),
                create_expert_task(),
            ],
            agents=[
                create_researcher_agent(access_level, category),
                create_conversational_agent(),
                create_expert_agent(),
            ],
            manager_agent=create_manager_agent(),
            verbose=True,
            process=Process.hierarchical
        )


def create_crew(access_level: str, category: str) -> Crew:
    """
    Função para criar a Crew de agentes.
    """
    return HealthComCrew(access_level, category).crew
