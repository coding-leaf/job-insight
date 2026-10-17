"""API v1 router aggregator."""

from fastapi import APIRouter

from app.api.v1.endpoints import jobs, meta, overview, stats

api_router = APIRouter()

api_router.include_router(meta.router, prefix="/meta", tags=["Meta"])
api_router.include_router(overview.router, prefix="/overview", tags=["Overview"])
api_router.include_router(stats.router, prefix="/stats", tags=["Stats"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
