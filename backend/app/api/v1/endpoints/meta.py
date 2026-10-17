from typing import Annotated

from fastapi import APIRouter, Depends

from app.db.repository import JobRepository, get_repository
from app.schemas.job import MetaOptionsData
from app.schemas.response import ResponseModel, success_response

router = APIRouter()


@router.get("/options", response_model=ResponseModel[MetaOptionsData])
async def get_options(
    repo: Annotated[JobRepository, Depends(get_repository)],
) -> ResponseModel[MetaOptionsData]:
    """Return filter options for category, province, and education."""
    options = await repo.get_meta_options()
    return success_response(data=options)
