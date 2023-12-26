"""Main module for the API."""

import sentry_sdk
import uvicorn
from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.responses.custom_responses import (
    CustomResponse,
    custom_http_exception_handler,
)
from app.api.routers.account_routers import router as account_router
from app.api.routers.checklist_router import router as checklist_router
from app.api.routers.dashboard_router import router as dashboard_router
from app.api.routers.email_router import router as email_router
from app.api.routers.file_router import router as file_router
from app.api.routers.gift_payment_router import router as payment_router
from app.api.routers.gift_router import router as gift_router
from app.api.routers.meal_router import router as meal_router
from app.api.routers.organization_router import router as organization_router
from app.api.routers.role_router import router as role_router
from app.api.routers.sso_router import router as sso_router
from app.core.config import settings
from app.database.connection import get_db_unyield
from app.services.permission_services import ORG_ADMIN_PERMISSION
from app.services.roles_services import create_default_roles

# from app.api.models.plan_models import Plan
from description import TEXT

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
    account_router,
)
v1_router.include_router(
    sso_router,
)
v1_router.include_router(
    email_router,
)
v1_router.include_router(
    role_router,
)
v1_router.include_router(
    organization_router,
)
v1_router.include_router(
    dashboard_router,
)
v1_router.include_router(
    meal_router,
)
v1_router.include_router(
    gift_router,
)
v1_router.include_router(
    file_router,
)
v1_router.include_router(
    checklist_router,
)
v1_router.include_router(
    payment_router,
)


app = FastAPI(
    title="Dream Affairs API",
    description=TEXT,
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


@v1_router.get("/health")
def health() -> CustomResponse:
    """Health check endpoint."""
    # add exception handling here
    return CustomResponse(
        status_code=200,
        message="Healthy",
    )


app.include_router(v1_router)


@app.on_event("startup")
async def startup_event():
    """Create default roles on startup."""

    if settings.ENVIRONMENT == "production":
        db = get_db_unyield()
        ORG_ADMIN_PERMISSION.create_permissions(db)
        create_default_roles(db)
        # Plan.create_default_plans(db)


if __name__ == "__main__":
    uvicorn.run(app="main:app", port=8000, reload=True)
