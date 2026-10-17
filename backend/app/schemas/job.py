
from pydantic import BaseModel, Field


class ProvenanceItem(BaseModel):
    origin: str
    evidence: str


class SkillItem(BaseModel):
    skill_name: str
    provenance: list[ProvenanceItem] = Field(default_factory=list)


class JobItem(BaseModel):
    id: str
    source_ids: list[str] = Field(default_factory=list)
    source_url: str | None = None
    published_at: str | None = None
    title: str
    company: str
    company_type: str | None = None
    company_size: str | None = None
    work_location: str | None = None
    province: str | None = None
    city: str | None = None
    salary_display: str | None = None
    salary_min_monthly: int | None = None
    salary_max_monthly: int | None = None
    salary_eligible_for_midpoint: bool = False
    salary_midpoint: float | None = None
    salary_stat_excluded: bool = False
    salary_exclude_reason: str | None = None
    education_requirement: str | None = None
    education_min_code: int | None = None
    experience_requirement: str | None = None
    experience_min_years: float | None = None
    experience_status: str | None = None
    major_requirement: str | None = None
    description: str | None = None
    recruitment_headcount: int | None = None
    skills: list[SkillItem] = Field(default_factory=list)
    job_category: str | None = None
    category_source: str | None = None


class MetaOptionsData(BaseModel):
    categories: list[str]
    provinces: list[str]
    education_levels: list[str]


class CategoryProportion(BaseModel):
    category: str
    count: int
    ratio: float


class OverviewData(BaseModel):
    total_jobs: int
    eligible_salary_jobs: int
    tagged_skills_jobs: int
    duplicate_groups: int
    overall_salary_median: float | None = None
    skill_coverage_ratio: float | None = None
    category_breakdown: list[CategoryProportion] = Field(default_factory=list)


class CategorySalaryStat(BaseModel):
    category: str
    sample_count: int
    eligible_count: int
    median: float | None = None
    p25: float | None = None
    p75: float | None = None
    is_low_sample: bool = False
    rank: int | None = None


class RegionSalaryStat(BaseModel):
    province: str
    sample_count: int
    eligible_count: int
    median: float | None = None
    p25: float | None = None
    p75: float | None = None
    is_low_sample: bool = False
    rank: int | None = None


class SkillStatItem(BaseModel):
    skill_name: str
    count: int
    ratio_annotated: float | None = None
    ratio_total: float | None = None


class SkillsTopData(BaseModel):
    total_jobs: int
    tagged_skills_jobs: int
    coverage_ratio: float | None = None
    skills: list[SkillStatItem] = Field(default_factory=list)


class JobListData(BaseModel):
    items: list[JobItem]
    total: int
    page: int
    page_size: int
    total_pages: int
