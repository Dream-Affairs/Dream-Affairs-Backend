"""Main module for the API."""
import sentry_sdk
import uvicorn
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.responses.custom_responses import (
    CustomException,
    CustomResponse,
    custom_http_exception_handler,
)
from app.api.routers import account_routers, meal_router
from app.core.config import settings

# ============ Sentry Initialization ============= #


sentry_sdk.init(
    settings.PRD_SENTRY_DSN,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    environment=settings.ENVIRONMENT,
)

# ================================================ #

v1_router = APIRouter(prefix="/api/v1")

app = FastAPI(
    title="Dream Affairs API",
    description="Making your dreams come true one api call at a time",
    version="0.1.0",
    docs_url="/",
)

app.add_exception_handler(HTTPException, custom_http_exception_handler)


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
    raise CustomException(status_code=400, message="Healthy", data={})


app.include_router(v1_router)
app.include_router(account_routers.router)
app.include_router(meal_router.app)


if __name__ == "__main__":
    uvicorn.run(app="main:app", port=8000, reload=True)
