from backend.app.api.routes import health
from backend.app.core.config import settings
from backend.app.core.logging import setup_logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

setup_logging(debug=settings.DEBUG)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="LexFlow - Internal Legal Operations Automation & Triage API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root health check and API v1 health router
app.include_router(health.router)
app.include_router(health.router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "docs": "/docs",
        "health": "/health",
    }
