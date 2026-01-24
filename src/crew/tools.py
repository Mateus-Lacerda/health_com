"""Módulo para as classes das ferramentas dos agentes."""

import os

import requests
from functools import partial
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

BASE_API_URL = os.getenv("BASE_API_URL", "http://localhost:5000")

# Dicionário para armazenar documentos encontrados na busca atual
search_results = {
    "documents": [],
    "names": []
}


def make_search(access_level: str, category: str, query: str) -> str:
    """Função para criar a busca na API interna."""
    global search_results
    
    response = requests.get(
        f"{BASE_API_URL}/api/v1/document/search",
        params={"query": query, "category": category,
                "access_level": access_level}
    )
    
    # Resetar resultados
    search_results = {
        "documents": [],
        "names": []
    }
    
    if response.status_code == 200:
        results = response.json().get("result", [])
        
        if not results:
            return "Nenhum documento encontrado para esta busca."
        
        result_text = f"Encontrados {len(results)} documento(s) relevante(s):\n\n"
        
        for idx, doc in enumerate(results, 1):
            doc_name = doc.get("filename", "Sem nome")
            content = doc.get("content", "")[:300]  # Primeiros 300 caracteres
            
            # Armazenar documento
            search_results["documents"].append(doc)
            search_results["names"].append(doc_name)
            
            result_text += f"Documento {idx}: {doc_name}\n"
            result_text += f"Categoria: {doc.get('category', 'N/A')}\n"
            result_text += f"Resumo: {content}...\n\n"
        
        return result_text
    else:
        return "Erro ao buscar informações na base de dados."


class SearchToolInput(BaseModel):
    """Esquema de entrada para o SearchTool."""
    query: str = Field(
        ..., description="""
        Termo de busca para consultar os documentos.
        O termo de busca é alguma palavra chave ou trecho que pode estar nos documentos alvo.
        """
    )


class SearchTool(BaseTool):
    """Ferramenta para buscar informações na API interna."""

    name: str = "search_tool"
    description: str = "Ferramenta para buscar informações nos documentos."
    args_schema: Type[BaseModel] = SearchToolInput

    def _run(self, query: str) -> str:  # type: ignore
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
