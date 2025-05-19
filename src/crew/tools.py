"""Módulo para as classes das ferramentas dos agentes."""

import os

import requests
from functools import partial
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

BASE_API_URL = os.getenv("BASE_API_URL", "http://localhost:5000")


def make_search(access_level: str, category: str, query: str) -> dict:
    """Função para criar a busca na API interna."""
    response = requests.get(
        f"{BASE_API_URL}/api/v1/document/search",
        params={"query": query, "category": category,
                "access_level": access_level}
    )
    if response.status_code == 200:
        return response.json().get("result", [])
    else:
        return {"error": "Erro ao buscar informações."}


class SearchToolInput(BaseModel):
    """Esquema de entrada para o SearchTool."""
    query: str = Field(
        ..., description="Termo de busca para consultar os documentos."
    )


class SearchTool(BaseTool):
    """Ferramenta para buscar informações na API interna."""

    name: str = "search_tool"
    description: str = "Ferramenta para buscar informações nos documentos."
    args_schema: Type[BaseModel] = SearchToolInput

    def _run(self, query: str) -> list[dict]:
        """Método para executar a busca na API interna."""
        pass


def search_tool(access_level: str, category: str) -> SearchTool:
    """Função para criar a ferramenta de busca."""
    tool = SearchTool()
    search = partial(
        make_search, access_level=access_level, category=category
    )
    tool._run = search

    return tool
