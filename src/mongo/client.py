"""Módulo de para o client do MongoDB e GridFS"""

import os

from gridfs import GridFS
from pymongo import MongoClient
from pymongo.database import Database

MONGO_URI = os.getenv("MONGO_URI") or "mongodb://localhost:27017"
DB_NAME = os.getenv("DB_NAME") or "healthcom"


class MongoDBClient:
    """
    Classe para gerenciar a conexão com o MongoDB e GridFS.

    Atributos:
        _client: Instância do cliente MongoDB.
        db: Banco de dados padrão.
        fs: Instância do GridFS.
    """
    _instance = None
    _initialized = False

    def __init__(self):
        """
        Inicializa a conexão com o MongoDB e GridFS.
        """
        if self._initialized:
            return
        self._client: MongoClient = MongoClient(MONGO_URI)
        self.db: Database = self._client[DB_NAME]
        self.fs: GridFS = GridFS(self.db)
        self._initialized = True

    def __new__(cls) -> "MongoDBClient":
        """
        Garante que apenas uma instância do cliente MongoDB seja criada.
        """
        if cls._instance is None:
            cls._instance = super(MongoDBClient, cls).__new__(cls)
        return cls._instance
