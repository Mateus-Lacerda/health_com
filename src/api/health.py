"""Module for the health route."""

from fastapi import APIRouter

health_router = APIRouter()


@health_router.get("/health")
async def health_check():
    """Health check endpoint.

    Returns:
        dict: A dictionary with the status of the service.
    """
    return {"status": "healthy"}
