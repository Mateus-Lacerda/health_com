"""Módulo de conexão com o Elasticsearch."""

import os
import logging
from elasticsearch import Elasticsearch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ES_HOST = os.getenv("ES_HOST", "localhost")
ES_PORT = int(os.getenv("ES_PORT", '9200'))
ELASTIC_USER = os.getenv("ELASTIC_USER", "elastic")
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD", "changeme")


class ElasticsearchConnection:
    """Classe responsável por realizar a conexão com o Elasticsearch."""
    _instance = None
    _initialized = False

    def __init__(self) -> None:
        """
        Inicializa a conexão com o Elasticsearch.
        """
        if self._initialized:
            return
        self.es = Elasticsearch(
            hosts=[f"http://{ES_HOST}:{ES_PORT}"],
            basic_auth=(ELASTIC_USER, ELASTIC_PASSWORD),
            verify_certs=False,
            max_retries=30,
            retry_on_timeout=True,
            request_timeout=30,
            ssl_show_warn=False,
        )
        self._create_doc_index()
        self._initialized = True

    def __new__(cls) -> "ElasticsearchConnection":
        """
        Garante que apenas uma instância do cliente Elasticsearch seja criada.
        """
        if cls._instance is None:
            cls._instance = super(ElasticsearchConnection, cls).__new__(cls)
        return cls._instance

    def _create_doc_index(self) -> None:
        index_name = "healthcom_docs"
        if self.es.indices.exists(index=index_name):
            return

        self.es.indices.create(
            index=index_name,
            body={
                "mappings": {
                    "properties": {
                        "filename": {"type": "text"},
                        "content": {"type": "text"},
                        "category": {"type": "keyword"},
                        "access_level": {"type": "integer"},
                        "uploaded_by": {"type": "keyword"},
                        "data_upload": {"type": "date"},
                    }
                }
            }
        )
