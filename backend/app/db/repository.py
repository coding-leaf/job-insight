"""Data repository supporting MongoDB and high-performance in-memory fallback.

Provides full filtering, aggregation, statistical percentiles, and pagination
for JobInsight endpoints.
"""

from __future__ import annotations

import json
import logging
import math
import re
import statistics
from pathlib import Path
from typing import Any, cast

from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import settings
from app.db.mongodb import get_database
from app.schemas.job import (
    CategoryProportion,
    CategorySalaryStat,
    JobItem,
    JobListData,
    MetaOptionsData,
    OverviewData,
    RegionSalaryStat,
    SkillStatItem,
    SkillsTopData,
)

logger = logging.getLogger(__name__)

OFFICIAL_CATEGORIES = [
    "算法与人工智能",
    "数据分析与大数据",
    "软件开发",
    "软件测试",
    "运维与云平台",
    "网络与信息安全",
    "硬件与芯片",
    "通信",
    "技术支持与实施",
    "项目与产品",
    "其他明确岗位",
]

ALL_PROVINCES = [
    "北京市",
    "天津市",
    "河北省",
    "山西省",
    "内蒙古自治区",
    "辽宁省",
    "吉林省",
    "黑龙江省",
    "上海市",
    "江苏省",
    "浙江省",
    "安徽省",
    "福建省",
    "江西省",
    "山东省",
    "河南省",
    "湖北省",
    "湖南省",
    "广东省",
    "广西壮族自治区",
    "海南省",
    "重庆市",
    "四川省",
    "贵州省",
    "云南省",
    "西藏自治区",
    "陕西省",
    "甘肃省",
    "青海省",
    "宁夏回族自治区",
    "新疆维吾尔自治区",
]

EDUCATION_LEVELS = [
    "博士及以上",
    "硕士及以上",
    "本科及以上",
    "大专及以上",
    "不限",
]


def compute_percentiles(
    salaries: list[float],
) -> tuple[float | None, float | None, float | None]:
    """Compute exact Median, P25, and P75 according to methodology."""
    if not salaries:
        return None, None, None
    sorted_salaries = sorted(salaries)
    n = len(sorted_salaries)
    med = float(statistics.median(sorted_salaries))
    if n == 1:
        return med, med, med
    quants = statistics.quantiles(sorted_salaries, n=4, method="inclusive")
    p25 = round(float(quants[0]), 2)
    p75 = round(float(quants[2]), 2)
    return round(med, 2), p25, p75


def _build_mongo_filter(
    category: str | None = None,
    province: str | None = None,
    education: str | None = None,
    keyword: str | None = None,
    min_salary: int | None = None,
    max_salary: int | None = None,
    has_skills: bool | None = None,
) -> dict[str, Any]:
    """Build standard MongoDB query dict from filtering parameters."""
    query: dict[str, Any] = {}

    if category:
        if category in ("未分类", "null", "None"):
            query["job_category"] = None
        else:
            query["job_category"] = category

    if province:
        if province in ("未注明", "null", "None"):
            query["province"] = None
        else:
            query["province"] = province

    if education:
        query["education_requirement"] = education

    if has_skills is not None:
        query["skills.0"] = {"$exists": bool(has_skills)}

    if min_salary is not None or max_salary is not None:
        query["salary_eligible_for_midpoint"] = True
        if min_salary is not None:
            query["salary_max_monthly"] = {"$gte": min_salary}
        if max_salary is not None:
            query["salary_min_monthly"] = {"$lte": max_salary}

    if keyword:
        kw = keyword.strip()
        if kw:
            pattern = {"$regex": re.escape(kw), "$options": "i"}
            query["$or"] = [
                {"title": pattern},
                {"company": pattern},
                {"description": pattern},
                {"skills.skill_name": pattern},
            ]

    return query


class JobRepository:
    def __init__(self) -> None:
        self._dataset: list[dict[str, Any]] | None = None
        self._id_index: dict[str, dict[str, Any]] | None = None
        # MongoDB is the primary datastore. In-memory JSON dataset is NOT preloaded at startup.

    def _ensure_fallback_data(self) -> None:
        """Lazy-load jobs_cleaned_grouped.json only when fallback is explicitly enabled."""
        if self._dataset is not None:
            return
        if not settings.ENABLE_JSON_FALLBACK:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Primary datastore MongoDB is unavailable. Please ensure MongoDB is running and seeded.",
            )
        self._load_dataset()
        if not self._dataset:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Primary datastore MongoDB is unavailable and fallback dataset could not be loaded.",
            )

    def _load_dataset(self) -> None:
        """Load jobs_cleaned_grouped.json strictly for offline test/fallback mode."""
        candidates = [
            Path(__file__).resolve().parents[3]
            / "data"
            / "processed"
            / "jobs_cleaned_grouped.json",
            Path(__file__).resolve().parents[2]
            / "data"
            / "processed"
            / "jobs_cleaned_grouped.json",
            Path("data/processed/jobs_cleaned_grouped.json").resolve(),
        ]
        target_path = None
        for c in candidates:
            if c.is_file():
                target_path = c
                break

        if target_path and target_path.is_file():
            try:
                with open(target_path, encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    self._dataset = data
                    self._id_index = {}
                    for item in data:
                        self._id_index[item["id"]] = item
                        for sid in item.get("source_ids", []):
                            self._id_index[sid] = item
                    logger.warning(
                        "[FALLBACK DEGRADED] Loaded in-memory JSON backup with %d records.",
                        len(self._dataset),
                    )
            except (json.JSONDecodeError, OSError) as e:
                logger.error("Could not load in-memory fallback dataset: %s", e)
        else:
            logger.error("Fallback dataset jobs_cleaned_grouped.json could not be found.")

    def _matches_filter(
        self,
        job: dict[str, Any],
        category: str | None = None,
        province: str | None = None,
        education: str | None = None,
        keyword: str | None = None,
        min_salary: int | None = None,
        max_salary: int | None = None,
        has_skills: bool | None = None,
    ) -> bool:
        if category:
            job_cat = job.get("job_category")
            if category in ("未分类", "null", "None"):
                if job_cat is not None:
                    return False
            elif job_cat != category:
                return False

        if province:
            job_prov = job.get("province")
            if province in ("未注明", "null", "None"):
                if job_prov is not None:
                    return False
            elif job_prov != province:
                return False

        if education and job.get("education_requirement") != education:
            return False

        if has_skills is not None:
            skills = job.get("skills") or []
            if has_skills and len(skills) == 0:
                return False
            if not has_skills and len(skills) > 0:
                return False

        # Salary interval overlap filter:
        # A valid job interval [job_min, job_max] overlaps with [min_salary, max_salary]
        # if job is eligible, job_max >= min_salary, and job_min <= max_salary
        if min_salary is not None or max_salary is not None:
            if not job.get("salary_eligible_for_midpoint"):
                return False
            j_min = job.get("salary_min_monthly")
            j_max = job.get("salary_max_monthly")
            if j_min is None or j_max is None:
                return False
            if min_salary is not None and j_max < min_salary:
                return False
            if max_salary is not None and j_min > max_salary:
                return False

        if keyword:
            kw = keyword.lower()
            title = (job.get("title") or "").lower()
            company = (job.get("company") or "").lower()
            desc = (job.get("description") or "").lower()
            skills_text = " ".join(
                s.get("skill_name", "") for s in (job.get("skills") or [])
            ).lower()
            if kw not in title and kw not in company and kw not in desc and kw not in skills_text:
                return False

        return True

    def _get_filtered_dataset(
        self,
        category: str | None = None,
        province: str | None = None,
        education: str | None = None,
        keyword: str | None = None,
        min_salary: int | None = None,
        max_salary: int | None = None,
        has_skills: bool | None = None,
    ) -> list[dict[str, Any]]:
        self._ensure_fallback_data()
        assert self._dataset is not None
        return [
            j
            for j in self._dataset
            if self._matches_filter(
                j,
                category=category,
                province=province,
                education=education,
                keyword=keyword,
                min_salary=min_salary,
                max_salary=max_salary,
                has_skills=has_skills,
            )
        ]

    # --- Native MongoDB Asynchronous Aggregation Methods ---

    _build_mongo_filter = staticmethod(_build_mongo_filter)

    async def _mongo_get_overview(
        self,
        db: AsyncIOMotorDatabase,
        match_filter: dict[str, Any],
    ) -> OverviewData:
        """Calculate KPI overview metrics via MongoDB $facet aggregation pipeline."""
        pipeline: list[dict[str, Any]] = [
            *([{"$match": match_filter}] if match_filter else []),
            {
                "$facet": {
                    "total": [{"$count": "count"}],
                    "eligible_salaries": [
                        {"$match": {"salary_eligible_for_midpoint": True}},
                        {"$group": {"_id": None, "salaries": {"$push": "$salary_midpoint"}}},
                    ],
                    "tagged_skills_count": [
                        {"$match": {"skills.0": {"$exists": True}}},
                        {"$count": "count"},
                    ],
                    "duplicate_groups_count": [
                        {"$match": {"source_ids.1": {"$exists": True}}},
                        {"$count": "count"},
                    ],
                    "categories": [
                        {
                            "$group": {
                                "_id": {"$ifNull": ["$job_category", "未分类"]},
                                "count": {"$sum": 1},
                            }
                        }
                    ],
                }
            },
        ]
        res = await db.jobs.aggregate(pipeline).to_list(length=None)
        data = res[0] if res else {}

        total_jobs = data["total"][0]["count"] if data.get("total") else 0
        salary_docs = data.get("eligible_salaries", [])
        eligible_salaries = salary_docs[0].get("salaries", []) if salary_docs else []
        eligible_count = len(eligible_salaries)
        tagged_skills_jobs = (
            data["tagged_skills_count"][0]["count"] if data.get("tagged_skills_count") else 0
        )
        duplicate_groups = (
            data["duplicate_groups_count"][0]["count"] if data.get("duplicate_groups_count") else 0
        )

        overall_median = None
        if eligible_count > 0:
            overall_median, _, _ = compute_percentiles(eligible_salaries)

        coverage_ratio = round(tagged_skills_jobs / total_jobs, 4) if total_jobs > 0 else None

        raw_categories = data.get("categories", [])
        raw_categories.sort(key=lambda x: -x["count"])
        breakdown = [
            CategoryProportion(
                category=c["_id"],
                count=c["count"],
                ratio=round(c["count"] / total_jobs, 4) if total_jobs > 0 else 0.0,
            )
            for c in raw_categories
        ]

        return OverviewData(
            total_jobs=total_jobs,
            eligible_salary_jobs=eligible_count,
            tagged_skills_jobs=tagged_skills_jobs,
            duplicate_groups=duplicate_groups,
            overall_salary_median=overall_median,
            skill_coverage_ratio=coverage_ratio,
            category_breakdown=breakdown,
        )

    _aggregate_overview = _mongo_get_overview

    async def _mongo_get_salary_by_category(
        self,
        db: AsyncIOMotorDatabase,
        match_filter: dict[str, Any],
    ) -> list[CategorySalaryStat]:
        """Category salary stats via MongoDB $sort -> $group aggregation pipeline."""
        pipeline: list[dict[str, Any]] = [
            *([{"$match": match_filter}] if match_filter else []),
            {"$sort": {"salary_midpoint": 1}},
            {
                "$group": {
                    "_id": {"$ifNull": ["$job_category", "未分类"]},
                    "sample_count": {"$sum": 1},
                    "salaries": {
                        "$push": {
                            "$cond": [
                                {"$eq": ["$salary_eligible_for_midpoint", True]},
                                "$salary_midpoint",
                                "$$REMOVE",
                            ]
                        }
                    },
                }
            },
        ]
        docs = await db.jobs.aggregate(pipeline).to_list(length=None)
        results: list[CategorySalaryStat] = []
        for doc in docs:
            cat = doc["_id"]
            tot = doc["sample_count"]
            salaries = [s for s in doc.get("salaries", []) if s is not None]
            elig = len(salaries)
            med, p25, p75 = compute_percentiles(salaries)
            is_low = elig < 5
            results.append(
                CategorySalaryStat(
                    category=cat,
                    sample_count=tot,
                    eligible_count=elig,
                    median=med,
                    p25=p25,
                    p75=p75,
                    is_low_sample=is_low,
                )
            )

        # Rank eligible categories (excluding "未分类" and low sample items from ranking)
        rankable = [
            r
            for r in results
            if not r.is_low_sample and r.category != "未分类" and r.median is not None
        ]
        rankable.sort(key=lambda x: (-(x.median or 0.0), x.category))
        for idx, item in enumerate(rankable, start=1):
            item.rank = idx

        unranked = [r for r in results if r.rank is None]
        unranked.sort(key=lambda x: (-(x.median or 0), x.category))

        return rankable + unranked

    _aggregate_salary_by_category = _mongo_get_salary_by_category

    async def _mongo_get_salary_by_region(
        self,
        db: AsyncIOMotorDatabase,
        match_filter: dict[str, Any],
    ) -> list[RegionSalaryStat]:
        """Province salary stats via MongoDB $sort -> $group aggregation pipeline."""
        pipeline: list[dict[str, Any]] = [
            *([{"$match": match_filter}] if match_filter else []),
            {"$sort": {"salary_midpoint": 1}},
            {
                "$group": {
                    "_id": {"$ifNull": ["$province", "未注明"]},
                    "sample_count": {"$sum": 1},
                    "salaries": {
                        "$push": {
                            "$cond": [
                                {"$eq": ["$salary_eligible_for_midpoint", True]},
                                "$salary_midpoint",
                                "$$REMOVE",
                            ]
                        }
                    },
                }
            },
        ]
        docs = await db.jobs.aggregate(pipeline).to_list(length=None)
        results: list[RegionSalaryStat] = []
        for doc in docs:
            prov = doc["_id"]
            tot = doc["sample_count"]
            salaries = [s for s in doc.get("salaries", []) if s is not None]
            elig = len(salaries)
            med, p25, p75 = compute_percentiles(salaries)
            is_low = elig < 5
            results.append(
                RegionSalaryStat(
                    province=prov,
                    sample_count=tot,
                    eligible_count=elig,
                    median=med,
                    p25=p25,
                    p75=p75,
                    is_low_sample=is_low,
                )
            )

        # Rank eligible provinces (unknown/未注明 and low sample excluded from ranking)
        rankable = [
            r
            for r in results
            if not r.is_low_sample and r.province not in ("未注明", "其他") and r.median is not None
        ]
        rankable.sort(key=lambda x: (-(x.median or 0.0), x.province))
        for idx, item in enumerate(rankable, start=1):
            item.rank = idx

        unranked = [r for r in results if r.rank is None]
        unranked.sort(key=lambda x: (-(x.median or 0), x.province))

        return rankable + unranked

    _aggregate_salary_by_region = _mongo_get_salary_by_region

    async def _mongo_get_skills_top(
        self,
        db: AsyncIOMotorDatabase,
        match_filter: dict[str, Any],
        limit: int = 20,
    ) -> SkillsTopData:
        """Top skills via MongoDB $unwind -> $group aggregation pipeline with dual denominators."""
        pipeline: list[dict[str, Any]] = [
            *([{"$match": match_filter}] if match_filter else []),
            {
                "$facet": {
                    "meta": [
                        {
                            "$group": {
                                "_id": None,
                                "total": {"$sum": 1},
                                "tagged": {
                                    "$sum": {
                                        "$cond": [
                                            {
                                                "$gt": [
                                                    {"$size": {"$ifNull": ["$skills", []]}},
                                                    0,
                                                ]
                                            },
                                            1,
                                            0,
                                        ]
                                    }
                                },
                            }
                        }
                    ],
                    "skills": [
                        {"$unwind": "$skills"},
                        {
                            "$match": {
                                "skills.skill_name": {
                                    "$exists": True,
                                    "$nin": [None, ""],
                                }
                            }
                        },
                        {
                            "$group": {
                                "_id": "$skills.skill_name",
                                "count": {"$sum": 1},
                            }
                        },
                        {"$sort": {"count": -1, "_id": 1}},
                        {"$limit": limit},
                    ],
                }
            },
        ]
        docs = await db.jobs.aggregate(pipeline).to_list(length=None)
        doc = docs[0] if docs else {}
        meta = doc.get("meta", [{}])[0] if doc.get("meta") else {}
        total_jobs = meta.get("total", 0)
        tagged_skills_jobs = meta.get("tagged", 0)
        coverage_ratio = round(tagged_skills_jobs / total_jobs, 4) if total_jobs > 0 else None

        raw_skills = doc.get("skills", [])
        skill_items = [
            SkillStatItem(
                skill_name=s["_id"],
                count=s["count"],
                ratio_annotated=(
                    round(s["count"] / tagged_skills_jobs, 4) if tagged_skills_jobs > 0 else None
                ),
                ratio_total=(round(s["count"] / total_jobs, 4) if total_jobs > 0 else None),
            )
            for s in raw_skills
        ]

        return SkillsTopData(
            total_jobs=total_jobs,
            tagged_skills_jobs=tagged_skills_jobs,
            coverage_ratio=coverage_ratio,
            skills=skill_items,
        )

    _aggregate_skills_top = _mongo_get_skills_top

    async def _mongo_get_jobs(
        self,
        db: AsyncIOMotorDatabase,
        query: dict[str, Any],
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "id",
        sort_order: str = "asc",
    ) -> JobListData:
        """Paginated search with multi-dimensional filtering via MongoDB cursor."""
        total = await db.jobs.count_documents(query)
        total_pages = math.ceil(total / page_size) if total > 0 else 0

        direction = -1 if sort_order.lower() == "desc" else 1
        skip = (page - 1) * page_size
        cursor = (
            db.jobs.find(query, {"_id": 0}).sort(sort_by, direction).skip(skip).limit(page_size)
        )
        items = await cursor.to_list(length=page_size)

        return JobListData(
            items=cast(list[JobItem], items),
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    _query_jobs = _mongo_get_jobs

    async def _mongo_get_job_by_id(
        self,
        db: AsyncIOMotorDatabase,
        job_id: str,
    ) -> dict[str, Any] | None:
        """Find a job by representative id or member source id via MongoDB."""
        return await db.jobs.find_one(
            {"$or": [{"id": job_id}, {"source_ids": job_id}]},
            {"_id": 0},
        )

    # --- Public API Methods with Dual Dispatching ---

    async def get_meta_options(self) -> MetaOptionsData:
        """Return available options for query filters."""
        categories = list(OFFICIAL_CATEGORIES)
        categories.append("未分类")

        db: AsyncIOMotorDatabase | None = get_database()
        if db is not None:
            dataset_provinces = set(await db.jobs.distinct("province", {"province": {"$ne": None}}))
        else:
            self._ensure_fallback_data()
            assert self._dataset is not None
            dataset_provinces = {j["province"] for j in self._dataset if j.get("province")}

        ordered_provinces = [p for p in ALL_PROVINCES if p in dataset_provinces]
        for p in dataset_provinces:
            if p not in ordered_provinces:
                ordered_provinces.append(p)

        return MetaOptionsData(
            categories=categories,
            provinces=ordered_provinces,
            education_levels=EDUCATION_LEVELS,
        )

    async def get_overview(
        self,
        category: str | None = None,
        province: str | None = None,
        education: str | None = None,
    ) -> OverviewData:
        """Calculate KPI overview metrics."""
        db: AsyncIOMotorDatabase | None = get_database()
        if db is not None:
            match_filter = self._build_mongo_filter(
                category=category, province=province, education=education
            )
            return await self._mongo_get_overview(db, match_filter)

        logger.warning("MongoDB unavailable: running degraded in-memory get_overview.")
        filtered = self._get_filtered_dataset(
            category=category, province=province, education=education
        )
        total_jobs = len(filtered)

        eligible_jobs = [j for j in filtered if j.get("salary_eligible_for_midpoint")]
        eligible_count = len(eligible_jobs)

        tagged_skills_jobs = sum(1 for j in filtered if j.get("skills") and len(j["skills"]) > 0)

        duplicate_groups = sum(1 for j in filtered if len(j.get("source_ids", [])) > 1)

        overall_median = None
        if eligible_count > 0:
            salaries = [j["salary_midpoint"] for j in eligible_jobs]
            overall_median, _, _ = compute_percentiles(salaries)

        coverage_ratio = round(tagged_skills_jobs / total_jobs, 4) if total_jobs > 0 else None

        cat_counts: dict[str, int] = {}
        for j in filtered:
            cat = j.get("job_category") or "未分类"
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

        breakdown = [
            CategoryProportion(
                category=cat,
                count=count,
                ratio=round(count / total_jobs, 4) if total_jobs > 0 else 0.0,
            )
            for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1])
        ]

        return OverviewData(
            total_jobs=total_jobs,
            eligible_salary_jobs=eligible_count,
            tagged_skills_jobs=tagged_skills_jobs,
            duplicate_groups=duplicate_groups,
            overall_salary_median=overall_median,
            skill_coverage_ratio=coverage_ratio,
            category_breakdown=breakdown,
        )

    async def get_salary_by_category(
        self,
        category: str | None = None,
        province: str | None = None,
        education: str | None = None,
    ) -> list[CategorySalaryStat]:
        """Category salary stats with P25, median, P75 and sample size threshold (<5)."""
        db: AsyncIOMotorDatabase | None = get_database()
        if db is not None:
            match_filter = self._build_mongo_filter(
                category=category, province=province, education=education
            )
            return await self._mongo_get_salary_by_category(db, match_filter)

        logger.warning("MongoDB unavailable: running degraded in-memory get_salary_by_category.")
        filtered = self._get_filtered_dataset(
            category=category, province=province, education=education
        )

        grouped: dict[str, dict[str, Any]] = {}
        for j in filtered:
            cat = j.get("job_category") or "未分类"
            if cat not in grouped:
                grouped[cat] = {"total": 0, "salaries": []}
            grouped[cat]["total"] += 1
            if j.get("salary_eligible_for_midpoint"):
                grouped[cat]["salaries"].append(j["salary_midpoint"])

        results: list[CategorySalaryStat] = []
        for cat, data in grouped.items():
            tot = data["total"]
            salaries = data["salaries"]
            elig = len(salaries)
            med, p25, p75 = compute_percentiles(salaries)
            is_low = elig < 5
            results.append(
                CategorySalaryStat(
                    category=cat,
                    sample_count=tot,
                    eligible_count=elig,
                    median=med,
                    p25=p25,
                    p75=p75,
                    is_low_sample=is_low,
                )
            )

        rankable = [
            r
            for r in results
            if not r.is_low_sample and r.category != "未分类" and r.median is not None
        ]
        rankable.sort(key=lambda x: (-(x.median or 0.0), x.category))
        for idx, item in enumerate(rankable, start=1):
            item.rank = idx

        unranked = [r for r in results if r.rank is None]
        unranked.sort(key=lambda x: (-(x.median or 0), x.category))

        return rankable + unranked

    async def get_salary_by_region(
        self,
        category: str | None = None,
        province: str | None = None,
        education: str | None = None,
    ) -> list[RegionSalaryStat]:
        """Province salary stats with P25, median, P75 and sample size threshold (<5)."""
        db: AsyncIOMotorDatabase | None = get_database()
        if db is not None:
            match_filter = self._build_mongo_filter(
                category=category, province=province, education=education
            )
            return await self._mongo_get_salary_by_region(db, match_filter)

        logger.warning("MongoDB unavailable: running degraded in-memory get_salary_by_region.")
        filtered = self._get_filtered_dataset(
            category=category, province=province, education=education
        )

        grouped: dict[str, dict[str, Any]] = {}
        for j in filtered:
            prov = j.get("province") or "未注明"
            if prov not in grouped:
                grouped[prov] = {"total": 0, "salaries": []}
            grouped[prov]["total"] += 1
            if j.get("salary_eligible_for_midpoint"):
                grouped[prov]["salaries"].append(j["salary_midpoint"])

        results: list[RegionSalaryStat] = []
        for prov, data in grouped.items():
            tot = data["total"]
            salaries = data["salaries"]
            elig = len(salaries)
            med, p25, p75 = compute_percentiles(salaries)
            is_low = elig < 5
            results.append(
                RegionSalaryStat(
                    province=prov,
                    sample_count=tot,
                    eligible_count=elig,
                    median=med,
                    p25=p25,
                    p75=p75,
                    is_low_sample=is_low,
                )
            )

        rankable = [
            r
            for r in results
            if not r.is_low_sample and r.province not in ("未注明", "其他") and r.median is not None
        ]
        rankable.sort(key=lambda x: (-(x.median or 0.0), x.province))
        for idx, item in enumerate(rankable, start=1):
            item.rank = idx

        unranked = [r for r in results if r.rank is None]
        unranked.sort(key=lambda x: (-(x.median or 0), x.province))

        return rankable + unranked

    async def get_skills_top(
        self,
        limit: int = 20,
        category: str | None = None,
        province: str | None = None,
        education: str | None = None,
    ) -> SkillsTopData:
        """Top skills with dual denominators: annotated ratio and total ratio."""
        db: AsyncIOMotorDatabase | None = get_database()
        if db is not None:
            match_filter = self._build_mongo_filter(
                category=category, province=province, education=education
            )
            return await self._mongo_get_skills_top(db, match_filter, limit=limit)

        logger.warning("MongoDB unavailable: running degraded in-memory get_skills_top.")
        filtered = self._get_filtered_dataset(
            category=category, province=province, education=education
        )
        total_jobs = len(filtered)
        tagged_skills_jobs = sum(1 for j in filtered if j.get("skills") and len(j["skills"]) > 0)

        coverage_ratio = round(tagged_skills_jobs / total_jobs, 4) if total_jobs > 0 else None

        skill_counts: dict[str, int] = {}
        for j in filtered:
            skills = j.get("skills") or []
            seen_in_job = set()
            for s in skills:
                name = s.get("skill_name")
                if name and name not in seen_in_job:
                    seen_in_job.add(name)
                    skill_counts[name] = skill_counts.get(name, 0) + 1

        sorted_skills = sorted(skill_counts.items(), key=lambda x: (-x[1], x[0]))[:limit]

        skill_items = [
            SkillStatItem(
                skill_name=name,
                count=count,
                ratio_annotated=(
                    round(count / tagged_skills_jobs, 4) if tagged_skills_jobs > 0 else None
                ),
                ratio_total=(round(count / total_jobs, 4) if total_jobs > 0 else None),
            )
            for name, count in sorted_skills
        ]

        return SkillsTopData(
            total_jobs=total_jobs,
            tagged_skills_jobs=tagged_skills_jobs,
            coverage_ratio=coverage_ratio,
            skills=skill_items,
        )

    async def get_jobs(
        self,
        page: int = 1,
        page_size: int = 20,
        category: str | None = None,
        province: str | None = None,
        education: str | None = None,
        keyword: str | None = None,
        min_salary: int | None = None,
        max_salary: int | None = None,
        has_skills: bool | None = None,
        sort_by: str = "id",
        sort_order: str = "asc",
    ) -> JobListData:
        """Paginated search with multi-dimensional filtering."""
        db: AsyncIOMotorDatabase | None = get_database()
        if db is not None:
            query = self._build_mongo_filter(
                category=category,
                province=province,
                education=education,
                keyword=keyword,
                min_salary=min_salary,
                max_salary=max_salary,
                has_skills=has_skills,
            )
            return await self._mongo_get_jobs(
                db,
                query=query,
                page=page,
                page_size=page_size,
                sort_by=sort_by,
                sort_order=sort_order,
            )

        logger.warning("MongoDB unavailable: running degraded in-memory get_jobs.")
        filtered = self._get_filtered_dataset(
            category=category,
            province=province,
            education=education,
            keyword=keyword,
            min_salary=min_salary,
            max_salary=max_salary,
            has_skills=has_skills,
        )
        total = len(filtered)
        total_pages = math.ceil(total / page_size) if total > 0 else 0

        reverse = sort_order.lower() == "desc"

        def sort_key(item: dict[str, Any]):
            val = item.get(sort_by)
            if val is None:
                return (1, "") if not reverse else (-1, "")
            return (0, val)

        sorted_jobs = sorted(filtered, key=sort_key, reverse=reverse)

        start = (page - 1) * page_size
        end = start + page_size
        page_items = sorted_jobs[start:end]

        return JobListData(
            items=cast(list[JobItem], page_items),
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def get_job_by_id(self, job_id: str) -> dict[str, Any] | None:
        """Find a job by representative id or member source id."""
        db: AsyncIOMotorDatabase | None = get_database()
        if db is not None:
            return await self._mongo_get_job_by_id(db, job_id)

        self._ensure_fallback_data()
        assert self._id_index is not None
        return self._id_index.get(job_id)


repository = JobRepository()


def get_repository() -> JobRepository:
    return repository
