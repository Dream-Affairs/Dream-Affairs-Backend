"""Main module for the API."""
import uvicorn
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.responses.custom_responses import (
    CustomResponse,
    custom_http_exception_handler,
)
from app.core.config import settings
from app.database.connection import create_database

# ============ add imported routers here ============= #


# ==================================================== #

v1_router = APIRouter(prefix="/api/v1")

app = FastAPI(
    title="Dream Affairs API",
    description="Making your dreams come true one api call at a time",
    version="0.1.0",
    docs_url="/",
)

app.add_exception_handler(HTTPException, custom_http_exception_handler)

if settings.ENVIRONMENT == "development":
    create_database()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> CustomResponse:
    """Health check endpoint."""
    # add exception handling here
    return CustomResponse(status_code=200, message="Healthy", data={})


app.include_router(v1_router)


if __name__ == "__main__":
    uvicorn.run(app="main:app", port=8000, reload=True)
