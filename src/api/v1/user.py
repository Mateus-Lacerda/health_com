"""Módulo para cadastro e busca de usuários"""

from datetime import datetime

from bson.objectid import ObjectId
from fastapi import HTTPException, Response
from fastapi.routing import APIRouter

from src.mongo.client import MongoDBClient
from src.schemas.user import (
    NewUserSchema,
    UserSchema,
    UserUpdateSchema,
    UserLoginSchema
)

user_router = APIRouter()

mongo_client = MongoDBClient()


@user_router.post("/")
async def add_user(user: NewUserSchema):
    """
    Adiciona um novo usuário ao banco de dados.

    Args:
        user (UserSchema): Dados do usuário a ser adicionado.

    Raises:
        HTTPException: Se o usuário já existir ou se ocorrer um erro ao adicionar o usuário.
    """
    db = mongo_client.db
    user_collection = db["users"]

    if user_collection.find_one({"user_name": user.user_name}):
        raise HTTPException(status_code=400, detail="Usuário já existe")

    try:
        user.access_level = user.access_level.value
        user_dict = user.dict()
        user_dict["created_at"] = datetime.utcnow()
        result = user_collection.insert_one(user_dict)
        return {"id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao adicionar usuário: {str(e)}")


@user_router.get("/{user_id}")
async def get_user(user_id: str) -> UserSchema:
    """
    Obtém os dados de um usuário pelo ID.

    Args:
        user_id (str): ID do usuário a ser buscado.

    Raises:
        HTTPException: Se o usuário não for encontrado ou se ocorrer um erro ao buscar o usuário.
    """
    db = mongo_client.db
    user_collection = db["users"]

    try:
        user = user_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(
                status_code=404, detail="Usuário não encontrado")
        return user
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao buscar usuário: {str(e)}")


@user_router.put("/{user_id}")
async def update_user(user_id: str, user_update: UserUpdateSchema):
    """
    Atualiza os dados de um usuário pelo ID.

    Args:
        user_id (str): ID do usuário a ser atualizado.
        user_update (UserUpdateSchema): Dados atualizados do usuário.

    Raises:
        HTTPException: Se o usuário não for encontrado ou se ocorrer um erro ao atualizar o usuário.
    """
    db = mongo_client.db
    user_collection = db["users"]

    try:
        user_update_dict = user_update.dict(exclude_unset=True)
        user_update_dict["updated_at"] = datetime.utcnow()
        result = user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": user_update_dict},
        )
        if result.matched_count == 0:
            raise HTTPException(
                status_code=404, detail="Usuário não encontrado")
        return {"message": "Usuário atualizado com sucesso"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao atualizar usuário: {str(e)}")


@user_router.delete("/{user_id}")
async def delete_user(user_id: str):
    """
    Deleta um usuário pelo ID.

    Args:
        user_id (str): ID do usuário a ser deletado.

    Raises:
        HTTPException: Se o usuário não for encontrado ou se
            ocorrer um erro ao deletar o usuário.
    """
    db = mongo_client.db
    user_collection = db["users"]

    try:
        result = user_collection.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=404, detail="Usuário não encontrado")
        return {"message": "Usuário deletado com sucesso"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao deletar usuário: {str(e)}")


@user_router.get("/")
async def get_users(limit: int = 10, offset: int = 0) -> dict:
    """
    Obtém uma lista de usuários.

    Args:
        limit (int): Número máximo de usuários a serem retornados.
        offset (int): Número de usuários a serem pulados.

    Raises:
        HTTPException: Se ocorrer um erro ao buscar os usuários.
    """
    db = mongo_client.db
    user_collection = db["users"]

    try:
        users = list(user_collection.find().skip(offset).limit(limit))
        for user in users:
            user["_id"] = str(user["_id"])
        total_users = user_collection.count_documents({})
        return {
            "total": total_users,
            "users": users
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao buscar usuários: {str(e)}")


@user_router.post("/login")
async def login(user_login: UserLoginSchema):
    """
    Realiza o login de um usuário.

    Args:
        user_login (UserLoginSchema): Dados de login do usuário.

    Raises:
        HTTPException: Se o usuário não for encontrado
            ou se ocorrer um erro ao realizar o login.
    """
    db = mongo_client.db
    user_collection = db["users"]

    try:
        user = user_collection.find_one(
            {"user_name": user_login.user_name,
                "password": user_login.password.get_secret_value()}
        )
        if not user:
            raise HTTPException(
                status_code=401, detail="Usuário ou senha inválidos")
        user_access_level = user.get("access_level")
        user_id = str(user["_id"])
        return {
            "message": "Login bem-sucedido",
            "access_level": user_access_level,
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao realizar login: {str(e)}")
