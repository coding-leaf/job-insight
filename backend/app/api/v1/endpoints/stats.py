from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import FilterParams
from app.db.repository import JobRepository, get_repository
from app.schemas.job import (
    CategorySalaryStat,
    RegionSalaryStat,
    SkillsTopData,
)
from app.schemas.response import ResponseModel, success_response

router = APIRouter()


@router.get(
    "/salary-by-category", response_model=ResponseModel[list[CategorySalaryStat]]
)
async def get_salary_by_category(
    filters: Annotated[FilterParams, Depends()],
    repo: Annotated[JobRepository, Depends(get_repository)],
) -> ResponseModel[list[CategorySalaryStat]]:
    """Return salary ranking and distribution by category (sample size threshold N < 5)."""
    data = await repo.get_salary_by_category(
        category=filters.category,
        province=filters.province,
        education=filters.education,
    )
    return success_response(data=data)


@router.get("/salary-by-region", response_model=ResponseModel[list[RegionSalaryStat]])
async def get_salary_by_region(
    filters: Annotated[FilterParams, Depends()],
    repo: Annotated[JobRepository, Depends(get_repository)],
) -> ResponseModel[list[RegionSalaryStat]]:
    """Return salary ranking and distribution by province/region."""
    data = await repo.get_salary_by_region(
        category=filters.category,
        province=filters.province,
        education=filters.education,
    )
    return success_response(data=data)


@router.get("/skills-top", response_model=ResponseModel[SkillsTopData])
async def get_skills_top(
    filters: Annotated[FilterParams, Depends()],
    repo: Annotated[JobRepository, Depends(get_repository)],
    limit: Annotated[int, Query(ge=1, le=100, description="Top N skills")] = 20,
) -> ResponseModel[SkillsTopData]:
    """Return top skills with annotated ratio and total ratio."""
    data = await repo.get_skills_top(
        limit=limit,
        category=filters.category,
        province=filters.province,
        education=filters.education,
    )
    return success_response(data=data)
