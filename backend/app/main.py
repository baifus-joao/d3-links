from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import get_settings
from backend.app.database.session import create_db_and_tables
from backend.app.routers.analytics import router as analytics_router
from backend.app.routers.health import router as health_router
from backend.app.routers.links import router as links_router
from backend.app.routers.redirect import router as redirect_router

settings = get_settings()
frontend_dir = Path(__file__).resolve().parents[2] / "frontend"


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
    description="Encurtador de links inteligente com analytics por unidade e campanha.",
)

app.include_router(health_router)
app.include_router(analytics_router)
app.include_router(links_router)

if frontend_dir.exists():
    app.mount("/dashboard", StaticFiles(directory=frontend_dir, html=True), name="dashboard")


@app.get("/")
def root():
    if frontend_dir.exists():
        return RedirectResponse(url="/dashboard/", status_code=307)
    return JSONResponse(
        {
            "name": settings.app_name,
            "environment": settings.app_env,
            "dashboard_url": f"{settings.base_url.rstrip('/')}/dashboard/",
            "docs_url": f"{settings.base_url.rstrip('/')}/docs",
            "api_info_url": f"{settings.base_url.rstrip('/')}/api-info",
        }
    )


@app.get("/api-info")
def api_info() -> JSONResponse:
    return JSONResponse(
        {
            "name": settings.app_name,
            "environment": settings.app_env,
            "dashboard_url": f"{settings.base_url.rstrip('/')}/dashboard/",
            "docs_url": f"{settings.base_url.rstrip('/')}/docs",
            "api_info_url": f"{settings.base_url.rstrip('/')}/api-info",
        }
    )


app.include_router(redirect_router)
