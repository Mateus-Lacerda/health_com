"""Módulo para definição do Schema de usuário"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, SecretStr


class AcessLevel(Enum):
    L1 = 1
    L2 = 2
    M1 = 3
    M2 = 4
    H1 = 5
    H2 = 6
    ADMIN = 999

    @staticmethod
    def get_available_levels(level: str) -> list[str]:
        """
        Retorna os níveis de acesso disponíveis para o nível fornecido.

        Args:
            level (str): Nível de acesso atual.

        Returns:
            list[str]: Lista de níveis de acesso disponíveis.
        """
        levels = {
            "L1": ["L1", "L2", "M1", "M2", "H1", "H2"],
            "L2": ["L2", "M1", "M2", "H1", "H2"],
            "M1": ["M1", "M2", "H1", "H2"],
            "M2": ["M2", "H1", "H2"],
            "H1": ["H1", "H2"],
            "H2": ["H2"],
            "ADMIN": ["ADMIN"],
        }
        return levels.get(level, [])


class UserSchema(BaseModel):
    """Classe para definição do Schema de usuário"""

    id: Optional[str] = Field(
        None, description="ID do usuário", examples=["507f1f77bcf86cd799439011"]
    )
    name: str = Field(..., description="Nome da pessoa", examples=["João Doido"])
    user_name: str = Field(
        ..., description="Nome de usuário", examples=["Xx_joaodoido_xX"]
    )
    password: SecretStr = Field(
        ..., description="Senha do usuário", examples=["Senha123*"]
    )
    access_level: AcessLevel = Field(
        ...,
        description="Nível de acesso do usuário",
        examples=[1, 2, 3, 4, 5, 6, 999],
    )
    created_at: Optional[datetime] = Field(
        None,
        description="Data de criação do usuário",
        examples=["2023-10-01T12:00:00Z"],
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Data de atualização do usuário",
        examples=["2023-10-01T12:00:00Z"],
    )


class NewUserSchema(BaseModel):
    """Classe para definição do Schema de novo usuário"""

    name: str = Field(..., description="Nome da pessoa", examples=["João Doido"])
    user_name: str = Field(
        ..., description="Nome de usuário", examples=["Xx_joaodoido_xX"]
    )
    password: str = Field(..., description="Senha do usuário", examples=["Senha123*"])
    access_level: AcessLevel = Field(
        ...,
        description="Nível de acesso do usuário",
        examples=[1, 2, 3, 4, 5, 6, 999],
    )


    def as_dict(self) -> dict:
        """Retorna o modelo como um dicionário"""
        return {
            "name": self.name,
            "user_name": self.user_name,
            "password": self.password,
            "access_level": self.access_level.value,
        }


class UserUpdateSchema(BaseModel):
    """Classe para definição do Schema de atualização de usuário"""

    name: Optional[str] = Field(
        None, description="Nome da pessoa", examples=["João Doido"]
    )
    user_name: Optional[str] = Field(
        None, description="Nome de usuário", examples=["Xx_joaodoido_xX"]
    )
    password: Optional[SecretStr] = Field(
        None, description="Senha do usuário", examples=["Senha123*"]
    )
    access_level: Optional[AcessLevel] = Field(
        None,
        description="Nível de acesso do usuário",
        examples=[1, 2, 3, 4, 5, 6, 999],
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Data de atualização do usuário",
        examples=["2023-10-01T12:00:00Z"],
    )


class UserLoginSchema(BaseModel):
    """Classe para definição do Schema de login de usuário"""

    user_name: str = Field(
        ..., description="Nome de usuário", examples=["Xx_joaodoido_xX"]
    )
    password: SecretStr = Field(
        ..., description="Senha do usuário", examples=["Senha123*"]
    )
