"""Automated test suite specifically verifying native MongoDB aggregation pipelines."""

from collections.abc import AsyncGenerator

import pytest
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import PyMongoError

from app.core.config import settings
from app.db.repository import _build_mongo_filter, repository


@pytest.fixture
async def mongo_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Provide a direct Motor database connection; skip tests if MongoDB is unreachable."""
    client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=1500)
    try:
        await client.admin.command("ping")
    except (PyMongoError, OSError):
        pytest.skip("MongoDB is not available at " + settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    yield db
    client.close()


def test_build_mongo_filter():
    """Verify conversion of parameters to MongoDB query dictionaries."""
    # 1. Normal category and province
    q1 = _build_mongo_filter(category="软件开发", province="北京市")
    assert q1 == {"job_category": "软件开发", "province": "北京市"}

    # 2. Unclassified category and unnoted province
    q2 = _build_mongo_filter(category="未分类", province="未注明")
    assert q2 == {"job_category": None, "province": None}

    # 3. Skills flag
    q3_true = _build_mongo_filter(has_skills=True)
    assert q3_true == {"skills.0": {"$exists": True}}
    q3_false = _build_mongo_filter(has_skills=False)
    assert q3_false == {"skills.0": {"$exists": False}}

    # 4. Salary overlap interval
    q4 = _build_mongo_filter(min_salary=10000, max_salary=20000)
    assert q4 == {
        "salary_eligible_for_midpoint": True,
        "salary_max_monthly": {"$gte": 10000},
        "salary_min_monthly": {"$lte": 20000},
    }

    # 5. Keyword search regex
    q5 = _build_mongo_filter(keyword="Python")
    assert "$or" in q5
    assert len(q5["$or"]) == 4


async def test_mongo_overview_pipeline(mongo_db: AsyncIOMotorDatabase):
    """Verify _mongo_get_overview facet pipeline baseline output."""
    overview = await repository._mongo_get_overview(mongo_db, match_filter={})

    assert overview.total_jobs == 2251
    assert overview.eligible_salary_jobs == 2194
    assert overview.tagged_skills_jobs == 833
    assert overview.duplicate_groups == 305
    assert overview.overall_salary_median == 12000.0
    assert pytest.approx(overview.skill_coverage_ratio, 0.001) == 0.3701

    breakdown = overview.category_breakdown
    assert len(breakdown) >= 11
    total_in_breakdown = sum(b.count for b in breakdown)
    assert total_in_breakdown == 2251

    # Filtered overview via facet
    filt = _build_mongo_filter(category="软件开发")
    dev_overview = await repository._aggregate_overview(mongo_db, match_filter=filt)
    assert dev_overview.total_jobs == 580
    assert dev_overview.eligible_salary_jobs == 574
    assert dev_overview.overall_salary_median == 12500.0


async def test_mongo_salary_by_category_pipeline(mongo_db: AsyncIOMotorDatabase):
    """Verify _mongo_get_salary_by_category aggregation and low sample flagging."""
    categories = await repository._mongo_get_salary_by_category(mongo_db, match_filter={})
    cat_map = {c.category: c for c in categories}

    # Algorithm & AI
    ai_stat = cat_map["算法与人工智能"]
    assert ai_stat.sample_count == 453
    assert ai_stat.eligible_count == 419
    assert ai_stat.median == 17500.0
    assert ai_stat.p25 == 12000.0
    assert ai_stat.p75 == 27500.0
    assert ai_stat.is_low_sample is False
    assert ai_stat.rank == 1

    # Software development
    dev_stat = cat_map["软件开发"]
    assert dev_stat.sample_count == 580
    assert dev_stat.eligible_count == 574
    assert dev_stat.median == 12500.0
    assert dev_stat.p25 == 9000.0
    assert dev_stat.p75 == 15500.0
    assert dev_stat.is_low_sample is False

    # Low sample threshold: '项目与产品' (N=4 < 5)
    prod_stat = cat_map["项目与产品"]
    assert prod_stat.sample_count == 4
    assert prod_stat.eligible_count == 4
    assert prod_stat.is_low_sample is True
    assert prod_stat.rank is None

    # Unclassified: excluded from rank
    unclass_stat = cat_map["未分类"]
    assert unclass_stat.sample_count == 403
    assert unclass_stat.eligible_count == 395
    assert unclass_stat.rank is None


async def test_mongo_salary_by_region_pipeline(mongo_db: AsyncIOMotorDatabase):
    """Verify _mongo_get_salary_by_region regional aggregation pipeline."""
    provinces = await repository._mongo_get_salary_by_region(mongo_db, match_filter={})
    assert len(provinces) >= 20

    prov_map = {p.province: p for p in provinces}
    assert "北京市" in prov_map
    assert "上海市" in prov_map
    assert "广东省" in prov_map

    bj = prov_map["北京市"]
    assert bj.sample_count > 0
    assert bj.median is not None
    assert bj.rank is not None


async def test_mongo_skills_top_pipeline(mongo_db: AsyncIOMotorDatabase):
    """Verify _mongo_get_skills_top unwind and dual denominators."""
    data = await repository._mongo_get_skills_top(mongo_db, match_filter={}, limit=20)

    assert data.total_jobs == 2251
    assert data.tagged_skills_jobs == 833
    assert pytest.approx(data.coverage_ratio, 0.001) == 0.3701
    assert len(data.skills) == 20

    top1 = data.skills[0]
    assert top1.skill_name == "Python"
    assert top1.count == 307
    assert pytest.approx(top1.ratio_annotated, 0.0001) == round(307 / 833, 4)
    assert pytest.approx(top1.ratio_total, 0.0001) == round(307 / 2251, 4)

    top2 = data.skills[1]
    assert top2.skill_name == "C++"
    assert top2.count == 234

    top3 = data.skills[2]
    assert top3.skill_name == "Linux"
    assert top3.count == 214


async def test_mongo_jobs_query_and_pagination(mongo_db: AsyncIOMotorDatabase):
    """Verify _mongo_get_jobs cursor pagination and filtering."""
    q_all = _build_mongo_filter()
    jobs_page1 = await repository._mongo_get_jobs(
        mongo_db, query=q_all, page=1, page_size=10, sort_by="id", sort_order="asc"
    )
    assert jobs_page1.total == 2251
    assert len(jobs_page1.items) == 10
    assert jobs_page1.total_pages == 226

    # Category filter
    q_cat = _build_mongo_filter(category="算法与人工智能")
    jobs_cat = await repository._query_jobs(mongo_db, query=q_cat, page=1, page_size=20)
    assert jobs_cat.total == 453

    # has_skills filter
    q_skills = _build_mongo_filter(has_skills=True)
    jobs_skills = await repository._mongo_get_jobs(mongo_db, query=q_skills, page=1, page_size=20)
    assert jobs_skills.total == 833


async def test_mongo_get_job_by_id(mongo_db: AsyncIOMotorDatabase):
    """Verify _mongo_get_job_by_id with primary id and source_ids."""
    first_job = await mongo_db.jobs.find_one({}, {"_id": 0, "id": 1, "source_ids": 1})
    assert first_job is not None
    job_id = first_job["id"]

    doc = await repository._mongo_get_job_by_id(mongo_db, job_id)
    assert doc is not None
    assert doc["id"] == job_id

    # Test source_id lookup if available
    source_ids = first_job.get("source_ids", [])
    if source_ids:
        doc_by_src = await repository._mongo_get_job_by_id(mongo_db, source_ids[0])
        assert doc_by_src is not None
        assert doc_by_src["id"] == job_id

    # Non-existent
    assert await repository._mongo_get_job_by_id(mongo_db, "non_existent_id_99999") is None


async def test_mongo_empty_filter_results(mongo_db: AsyncIOMotorDatabase):
    """Verify aggregation pipelines handle zero matching records gracefully."""
    empty_filter = _build_mongo_filter(category="NonExistentCategory")

    overview = await repository._mongo_get_overview(mongo_db, empty_filter)
    assert overview.total_jobs == 0
    assert overview.eligible_salary_jobs == 0
    assert overview.overall_salary_median is None
    assert overview.category_breakdown == []

    salaries = await repository._mongo_get_salary_by_category(mongo_db, empty_filter)
    assert salaries == []

    regions = await repository._mongo_get_salary_by_region(mongo_db, empty_filter)
    assert regions == []

    skills = await repository._mongo_get_skills_top(mongo_db, empty_filter)
    assert skills.total_jobs == 0
    assert skills.tagged_skills_jobs == 0
    assert skills.coverage_ratio is None
    assert skills.skills == []

    jobs = await repository._mongo_get_jobs(mongo_db, empty_filter)
    assert jobs.total == 0
    assert jobs.items == []
    assert jobs.total_pages == 0
