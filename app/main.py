from fastapi import FastAPI

from app.routers import health

app = FastAPI(
    title="Blog Platform API",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)


app.include_router(health.router, prefix="/api/v1")
