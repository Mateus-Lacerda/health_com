"""Module that starts and runs the API."""

import os

from fastapi import FastAPI
from uvicorn import run

from src.api.v1 import router
from src.api.health import health_router


def create_app():
    """Create the FastAPI app."""

    app = FastAPI()
    app.include_router(router)
    app.include_router(health_router)
    return app


app = create_app()

if __name__ == "__main__":
    # Get the host and port from environment variables or use default values
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))
    reload = os.getenv("RELOAD", "False").lower() == "true"

    run(
        "src.api.run:app",
        host=host,
        port=port,
        reload=reload,
        reload_dirs=["src.api"],
        log_level="info",
    )
