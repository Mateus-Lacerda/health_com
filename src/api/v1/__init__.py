"""Base module for the API v1."""

from fastapi import APIRouter

from src.api.v1.document import document_router
from src.api.v1.user import user_router

__all__ = ["router"]

router = APIRouter(
    prefix="/api/v1",
    tags=["API v1"]
)

router.include_router(
    user_router,
    prefix="/user",
    tags=["User"],
)
router.include_router(
    document_router,
    prefix="/document",
    tags=["Document"],
)
