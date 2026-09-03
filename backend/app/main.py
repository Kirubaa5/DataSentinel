from fastapi import FastAPI

from app.api.analysis import router as analysis_router
from app.api.datasets import router as datasets_router
from app.api.findings import router as findings_router
from app.api.repairs import router as repairs_router
from app.core.logging import configure_logging

configure_logging()
app = FastAPI(title="DataSentinel", version="1.0.0")


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok", "service": "datasentinel"}


app.include_router(datasets_router, prefix="/api")
app.include_router(analysis_router, prefix="/api")
app.include_router(findings_router, prefix="/api")
app.include_router(repairs_router, prefix="/api")