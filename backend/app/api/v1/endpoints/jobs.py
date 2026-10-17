from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import FilterParams
from app.db.repository import JobRepository, get_repository
from app.schemas.job import JobItem, JobListData
from app.schemas.response import ResponseModel, success_response

router = APIRouter()


@router.get("", response_model=ResponseModel[JobListData])
async def list_jobs(
    filters: Annotated[FilterParams, Depends()],
    repo: Annotated[JobRepository, Depends(get_repository)],
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
    sort_by: Annotated[
        str,
        Query(
            pattern="^(id|published_at|salary_min_monthly|salary_max_monthly|salary_midpoint)$",
            description="Field to sort by",
        ),
    ] = "id",
    sort_order: Annotated[
        str, Query(pattern="^(asc|desc)$", description="Sort order")
    ] = "asc",
) -> ResponseModel[JobListData]:
    """Search and paginate job postings with multi-dimensional filtering."""
    data = await repo.get_jobs(
        page=page,
        page_size=page_size,
        category=filters.category,
        province=filters.province,
        education=filters.education,
        keyword=filters.keyword,
        min_salary=filters.min_salary,
        max_salary=filters.max_salary,
        has_skills=filters.has_skills,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return success_response(data=data)


@router.get("/{job_id}", response_model=ResponseModel[JobItem])
async def get_job_detail(
    job_id: str,
    repo: Annotated[JobRepository, Depends(get_repository)],
) -> ResponseModel[JobItem]:
    """Retrieve detailed information for a single job posting by ID."""
    job = await repo.get_job_by_id(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id '{job_id}' not found",
        )
    return success_response(data=JobItem.model_validate(job))
