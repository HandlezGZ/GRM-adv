from contextlib import asynccontextmanager

from backend.app.api.routes import classification, health, requests
from backend.app.core.config import settings
from backend.app.core.logging import setup_logging
from backend.app.db.session import init_db
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

setup_logging(debug=settings.DEBUG)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize tables
    init_db()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="LexFlow - Internal Legal Operations Automation & Triage API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root health check and API v1 routes
app.include_router(health.router)
app.include_router(health.router, prefix="/api/v1")
app.include_router(requests.router, prefix="/api/v1")
app.include_router(classification.router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "docs": "/docs",
        "health": "/health",
    }
