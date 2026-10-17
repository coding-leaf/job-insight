"""Common API dependencies and query parameters."""


from fastapi import Query
from pydantic import BaseModel


class FilterParams(BaseModel):
    category: str | None = Query(
        None, description="Job category, e.g. 软件开发, or '未分类'"
    )
    province: str | None = Query(
        None, description="Province name, e.g. 广东省, or '未注明'"
    )
    education: str | None = Query(
        None, description="Education requirement, e.g. 本科及以上"
    )
    keyword: str | None = Query(
        None, description="Search keyword in title, company, description, or skills"
    )
    min_salary: int | None = Query(None, description="Minimum monthly salary filter")
    max_salary: int | None = Query(None, description="Maximum monthly salary filter")
    has_skills: bool | None = Query(
        None, description="Filter by presence of skills (true/false)"
    )
