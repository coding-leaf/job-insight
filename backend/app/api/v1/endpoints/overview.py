from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import FilterParams
from app.db.repository import JobRepository, get_repository
from app.schemas.job import OverviewData
from app.schemas.response import ResponseModel, success_response

router = APIRouter()


@router.get("", response_model=ResponseModel[OverviewData])
async def get_overview(
    filters: Annotated[FilterParams, Depends()],
    repo: Annotated[JobRepository, Depends(get_repository)],
) -> ResponseModel[OverviewData]:
    """Return KPI overview statistics including total jobs, salary median, and coverage ratio."""
    data = await repo.get_overview(
        category=filters.category,
        province=filters.province,
        education=filters.education,
    )
    return success_response(data=data)
