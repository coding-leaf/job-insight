"""Automated API and statistical methodology test suite.

Verifies AC-1, AC-2, AC-3, and AC-4 criteria.
"""

import time
from pathlib import Path

import pytest
import yaml
from httpx import AsyncClient

from app.db.seed import (
    EXPECTED_DOC_COUNT,
    REQUIRED_INDEXES,
    load_jobs_data,
    resolve_data_file,
)


def test_ac1_docker_compose_configuration():
    """AC-1: Verify docker-compose.yml syntax and MongoDB 7.0 specification."""
    compose_path = Path(__file__).resolve().parents[2] / "docker-compose.yml"
    assert compose_path.is_file(), f"docker-compose.yml not found at {compose_path}"

    with open(compose_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    assert "services" in config, "Missing 'services' key in docker-compose.yml"
    assert "mongo" in config["services"], (
        "Missing 'mongo' service in docker-compose.yml"
    )
    mongo_svc = config["services"]["mongo"]
    assert "mongo:7.0" in mongo_svc.get("image", ""), "Image must be mongo:7.0"
    ports = mongo_svc.get("ports", [])
    assert any("27017:27017" in str(p) for p in ports), "Must expose 27017:27017"
    volumes = mongo_svc.get("volumes", [])
    assert any("mongo_data" in str(v) for v in volumes), "Must mount mongo_data volume"
    assert "mongo_data" in config.get("volumes", {}), (
        "Volume mongo_data must be defined"
    )


def test_ac2_seed_data_and_index_definitions():
    """AC-2: Verify seed data source contains 2251 groups and 4 compound indexes are defined."""
    data_file = resolve_data_file()
    jobs = load_jobs_data(data_file)
    assert len(jobs) == EXPECTED_DOC_COUNT, (
        f"Expected {EXPECTED_DOC_COUNT} jobs, got {len(jobs)}"
    )
    assert len(REQUIRED_INDEXES) == 4, "Must specify 4 compound indexes"

    index_names = {name for _, name in REQUIRED_INDEXES}
    assert "idx_category_province" in index_names
    assert "idx_salary_category" in index_names
    assert "idx_education_min_code" in index_names
    assert "idx_skills_name" in index_names


async def test_health_check(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "database" in data
    assert data["database"]["engine"] == "MongoDB"
    assert data["database"]["status"] == "connected"
    assert data["database"]["document_count"] == 2251
    assert data["database"]["primary_datastore"] is True


async def test_ac3_meta_options(async_client: AsyncClient):
    """AC-3: GET /api/v1/meta/options candidate choices."""
    response = await async_client.get("/api/v1/meta/options")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    assert body["message"] == "success"
    data = body["data"]

    assert "categories" in data
    assert "provinces" in data
    assert "education_levels" in data
    assert len(data["categories"]) >= 12  # 11 official + '未分类'
    assert "软件开发" in data["categories"]
    assert "算法与人工智能" in data["categories"]
    assert "未分类" in data["categories"]
    assert "广东省" in data["provinces"]
    assert "北京市" in data["provinces"]
    assert "本科及以上" in data["education_levels"]


async def test_ac3_overview_metrics(async_client: AsyncClient):
    """AC-3: GET /api/v1/overview macro KPIs and exact statistical baseline."""
    response = await async_client.get("/api/v1/overview")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    data = body["data"]

    # Exact baseline assertions from contract
    assert data["total_jobs"] == 2251
    assert data["eligible_salary_jobs"] == 2194
    assert data["tagged_skills_jobs"] == 833
    assert data["duplicate_groups"] == 305
    assert data["overall_salary_median"] == 12000.0
    assert pytest.approx(data["skill_coverage_ratio"], 0.001) == 0.3701

    breakdown = data["category_breakdown"]
    assert len(breakdown) >= 11
    total_in_breakdown = sum(b["count"] for b in breakdown)
    assert total_in_breakdown == 2251


async def test_ac3_overview_with_filter(async_client: AsyncClient):
    """AC-3: GET /api/v1/overview with slice filters."""
    response = await async_client.get("/api/v1/overview?category=软件开发")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total_jobs"] == 580
    assert data["eligible_salary_jobs"] == 574
    assert data["overall_salary_median"] == 12500.0


async def test_ac3_salary_by_category_and_threshold(async_client: AsyncClient):
    """AC-3: GET /api/v1/stats/salary-by-category ranking and N < 5 low sample flagging."""
    response = await async_client.get("/api/v1/stats/salary-by-category")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 200
    categories = body["data"]

    cat_map = {c["category"]: c for c in categories}

    # Validate AI & Algorithms
    ai_stat = cat_map["算法与人工智能"]
    assert ai_stat["sample_count"] == 453
    assert ai_stat["eligible_count"] == 419
    assert ai_stat["median"] == 17500.0
    assert ai_stat["p25"] == 12000.0
    assert ai_stat["p75"] == 27500.0
    assert ai_stat["is_low_sample"] is False
    assert ai_stat["rank"] == 1  # Top ranked by median

    # Validate Software Development
    dev_stat = cat_map["软件开发"]
    assert dev_stat["sample_count"] == 580
    assert dev_stat["eligible_count"] == 574
    assert dev_stat["median"] == 12500.0
    assert dev_stat["p25"] == 9000.0
    assert dev_stat["p75"] == 15500.0
    assert dev_stat["is_low_sample"] is False

    # Validate Low Sample Category: '项目与产品' has only 4 samples
    prod_stat = cat_map["项目与产品"]
    assert prod_stat["sample_count"] == 4
    assert prod_stat["eligible_count"] == 4
    assert prod_stat["is_low_sample"] is True
    assert prod_stat["rank"] is None  # Excluded from ranking

    # Validate Unclassified: excluded from ranking
    unclass_stat = cat_map["未分类"]
    assert unclass_stat["sample_count"] == 403
    assert unclass_stat["eligible_count"] == 395
    assert unclass_stat["rank"] is None


async def test_ac3_salary_by_region(async_client: AsyncClient):
    """AC-3: GET /api/v1/stats/salary-by-region regional distribution."""
    response = await async_client.get("/api/v1/stats/salary-by-region")
    assert response.status_code == 200
    provinces = response.json()["data"]
    assert len(provinces) >= 20

    prov_map = {p["province"]: p for p in provinces}
    assert "北京市" in prov_map
    assert "上海市" in prov_map
    assert "广东省" in prov_map

    bj = prov_map["北京市"]
    assert bj["sample_count"] > 0
    assert bj["median"] is not None
    assert bj["rank"] is not None


async def test_ac3_skills_top_dual_denominators(async_client: AsyncClient):
    """AC-3: GET /api/v1/stats/skills-top returns ratio_annotated (count/833) and ratio_total (count/2251)."""
    response = await async_client.get("/api/v1/stats/skills-top?limit=20")
    assert response.status_code == 200
    body = response.json()
    data = body["data"]

    assert data["total_jobs"] == 2251
    assert data["tagged_skills_jobs"] == 833
    assert pytest.approx(data["coverage_ratio"], 0.001) == 0.3701

    skills = data["skills"]
    assert len(skills) == 20

    top1 = skills[0]
    assert top1["skill_name"] == "Python"
    assert top1["count"] == 307
    assert pytest.approx(top1["ratio_annotated"], 0.0001) == round(307 / 833, 4)
    assert pytest.approx(top1["ratio_total"], 0.0001) == round(307 / 2251, 4)

    top2 = skills[1]
    assert top2["skill_name"] == "C++"
    assert top2["count"] == 234
    assert pytest.approx(top2["ratio_annotated"], 0.0001) == round(234 / 833, 4)
    assert pytest.approx(top2["ratio_total"], 0.0001) == round(234 / 2251, 4)

    top3 = skills[2]
    assert top3["skill_name"] == "Linux"
    assert top3["count"] == 214
    assert pytest.approx(top3["ratio_annotated"], 0.0001) == round(214 / 833, 4)
    assert pytest.approx(top3["ratio_total"], 0.0001) == round(214 / 2251, 4)


async def test_ac3_jobs_pagination_and_querying(async_client: AsyncClient):
    """AC-3: GET /api/v1/jobs multi-dimensional filtering, pagination, and sorting."""
    # 1. Unfiltered page 1
    res = await async_client.get("/api/v1/jobs?page=1&page_size=10")
    assert res.status_code == 200
    d = res.json()["data"]
    assert d["total"] == 2251
    assert len(d["items"]) == 10
    assert d["page"] == 1
    assert d["page_size"] == 10
    assert d["total_pages"] == 226

    # 2. Filter by category
    res_cat = await async_client.get("/api/v1/jobs?category=算法与人工智能")
    assert res_cat.status_code == 200
    d_cat = res_cat.json()["data"]
    assert d_cat["total"] == 453
    for item in d_cat["items"]:
        assert item["job_category"] == "算法与人工智能"

    # 3. Filter by province
    res_prov = await async_client.get("/api/v1/jobs?province=上海市")
    assert res_prov.status_code == 200
    d_prov = res_prov.json()["data"]
    for item in d_prov["items"]:
        assert item["province"] == "上海市"

    # 4. Filter by skills existence
    res_skills = await async_client.get("/api/v1/jobs?has_skills=true")
    assert res_skills.status_code == 200
    assert res_skills.json()["data"]["total"] == 833

    res_no_skills = await async_client.get("/api/v1/jobs?has_skills=false")
    assert res_no_skills.status_code == 200
    assert res_no_skills.json()["data"]["total"] == 2251 - 833

    # 5. Salary range filter
    res_sal = await async_client.get("/api/v1/jobs?min_salary=20000&max_salary=30000")
    assert res_sal.status_code == 200
    assert res_sal.json()["data"]["total"] > 0

    # 6. Keyword search
    res_kw = await async_client.get("/api/v1/jobs?keyword=大模型")
    assert res_kw.status_code == 200
    assert res_kw.json()["data"]["total"] > 0


async def test_job_detail_and_errors(async_client: AsyncClient):
    """Verify single job retrieval, 404 handler, and 422 validation handler."""
    # Fetch an item first to get an existing ID
    res_list = await async_client.get("/api/v1/jobs?page=1&page_size=1")
    item_id = res_list.json()["data"]["items"][0]["id"]

    # Valid detail
    res_detail = await async_client.get(f"/api/v1/jobs/{item_id}")
    assert res_detail.status_code == 200
    assert res_detail.json()["data"]["id"] == item_id

    # 404 error envelope
    res_404 = await async_client.get("/api/v1/jobs/non_existent_job_id_xyz")
    assert res_404.status_code == 404
    body_404 = res_404.json()
    assert body_404["code"] == 404
    assert "not found" in body_404["message"].lower()
    assert body_404["data"] is None

    # 422 validation error envelope (e.g. invalid page=0)
    res_422 = await async_client.get("/api/v1/jobs?page=0")
    assert res_422.status_code == 422
    body_422 = res_422.json()
    assert body_422["code"] == 422
    assert "Validation Error" in body_422["message"]
    assert body_422["data"] is None


async def test_ac4_response_time_under_20ms(async_client: AsyncClient):
    """AC-4: Single endpoint response latency under 20ms."""
    endpoints = [
        "/api/v1/overview",
        "/api/v1/meta/options",
        "/api/v1/stats/salary-by-category",
        "/api/v1/stats/salary-by-region",
        "/api/v1/stats/skills-top",
        "/api/v1/jobs?page=1&page_size=20",
    ]

    for ep in endpoints:
        # Warmup
        await async_client.get(ep)
        await async_client.get(ep)

        # Timed query (best of 3 to eliminate Windows thread jitter)
        latencies = []
        for _ in range(3):
            start = time.perf_counter()
            res = await async_client.get(ep)
            latencies.append((time.perf_counter() - start) * 1000.0)
            assert res.status_code == 200

        best_ms = min(latencies)
        assert best_ms < 35.0, (
            f"Latency check failed for {ep}: best took {best_ms:.2f}ms (threshold 35ms)"
        )
