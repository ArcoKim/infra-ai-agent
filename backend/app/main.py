from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import logger
from app.core.clients import SharedClients
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.APP_NAME}...")
    await SharedClients.startup()
    logger.info("Shared HTTP clients initialized")
    yield
    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}...")
    await SharedClients.shutdown()
    logger.info("Shared HTTP clients closed")


app = FastAPI(
    title=settings.APP_NAME,
    description="반도체 Infra AI Agent - 센서 데이터 분석 및 시각화",
    version="1.0.0",
    lifespan=lifespan,
    redirect_slashes=False,
)

# CORS middleware
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://frontend:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
