"""Main module for the API."""
import sentry_sdk
import uvicorn
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.responses.custom_responses import (
    CustomResponse,
    custom_http_exception_handler,
)
from app.api.routers.account_routers import router as account_routers
from app.api.routers.email_router import email_router as email_routers
from app.api.routers.invite_router import router as invite_routers
from app.api.routers.meal_router import meal_router as meal_routers
from app.api.routers.role_router import router as role_routers
from app.core.config import settings

# ============ add imported routers here ============= #


# ==================================================== #


# ============ Sentry Initialization ============= #


sentry_sdk.init(
    settings.PRD_SENTRY_DSN,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    environment=settings.ENVIRONMENT,
)

# ================================================ #

v1_router = APIRouter(prefix="/api/v1")


v1_router.include_router(
    account_routers,
)
v1_router.include_router(
    email_routers,
)
v1_router.include_router(
    role_routers,
)
v1_router.include_router(
    invite_routers,
)

v1_router.include_router(meal_routers)

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
    return CustomResponse(
        status_code=200,
        detail="Healthy",
    )


app.include_router(v1_router)


if __name__ == "__main__":
    uvicorn.run(app="main:app", port=8000, reload=True)
