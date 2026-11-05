from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import dashboard, datasets, eval, prompts
from backend.app.core.config import settings
from backend.app.db.session import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database tables exist
    Base.metadata.create_all(bind=engine)
    try:
        from backend.app.db.session import SessionLocal
        from scripts.seed_golden_dataset import seed_database
        with SessionLocal() as db:
            seed_database(db)
    except Exception:
        pass
    yield


app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


api_router = APIRouter(prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
@api_router.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "lexeval-api",
        "version": "0.1.0",
    }


api_router.include_router(datasets.router)
api_router.include_router(prompts.router)
api_router.include_router(eval.router)
api_router.include_router(dashboard.router)

app.include_router(api_router)
