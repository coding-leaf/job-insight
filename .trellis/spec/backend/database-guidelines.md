# Backend Database & MongoDB Guidelines

## Overview

The JobInsight persistence layer uses MongoDB 7.0 as its **core primary datastore** via Motor (`AsyncIOMotorClient`). All domain queries, KPI aggregations, percentile sorting arrays, and paginated searches are executed directly against the MongoDB collection `jobs`.

The local JSON (`data/processed/jobs_cleaned_grouped.json`) is strictly demoted to a **secondary cold backup snapshot** for archival and disaster recovery. The backend **no longer preloads JSON data into memory at startup**.

---

## Database Configuration

- Database Name: `job_insight`
- Primary Collection: `jobs` (2,251 benchmark documents)
- Environment Variables:
  - `MONGODB_URL`: `mongodb://localhost:27017`
  - `DATABASE_NAME`: `job_insight`
  - `ENABLE_JSON_FALLBACK`: `False` (defaults to `False`; forces strict primary database operation)

---

## Required Indexes

Four core compound and single-field indexes are created during seeding or pipeline execution:

1. `idx_category_province`: `[("job_category", 1), ("province", 1)]` — multi-dimensional category & regional slicer acceleration.
2. `idx_salary_category`: `[("salary_eligible_for_midpoint", 1), ("job_category", 1)]` — salary benchmark filtering.
3. `idx_education_min_code`: `[("education_min_code", 1)]` — educational hierarchy filtering.
4. `idx_skills_name`: `[("skills.skill_name", 1)]` — skill penetration and tag lookup acceleration.

---

## Native MongoDB Aggregation Pipelines

All aggregation endpoints execute natively on MongoDB:

1. **Overview Metrics (`_mongo_get_overview`)**:
   Uses `$facet` to compute `total`, `eligible_salaries`, `tagged_skills_count`, `duplicate_groups_count`, and `categories` in a single round-trip.
2. **Category Salary Rankings (`_mongo_get_salary_by_category`)**:
   Uses `$match` -> `$sort: {"salary_midpoint": 1}` -> `$group: {"_id": "$job_category", "salaries": {"$push": "$salary_midpoint"}}` to pull sorted salary arrays for exact P25/Median/P75 calculation with sample size threshold (<5) flagging.
3. **Regional Salary Gradient (`_mongo_get_salary_by_region`)**:
   Uses `$match` -> `$sort` -> `$group: {"_id": "$province", "salaries": {"$push": "$salary_midpoint"}}`.
4. **Skills Penetration Top 20 (`_mongo_get_skills_top`)**:
   Uses `$match` and `$facet`; the metadata branch counts all/tagged groups and the skills branch uses `$unwind` -> `$group` -> `$sort` -> `$limit`. Responses expose dual denominators (annotated ratio vs total ratio).
5. **Job Explorer Search & Pagination (`_mongo_get_jobs`)**:
   Uses native Motor `db.jobs.find(query).sort().skip().limit()` alongside `db.jobs.count_documents(query)`.
6. **Job Detail Retrieval (`_mongo_get_job_by_id`)**:
   Directly queries `{"$or": [{"id": job_id}, {"source_ids": job_id}]}`. If not found in MongoDB, returns `None` (404), strictly avoiding cross-source mixing.

---

## Demoted JSON Role & Fallback Policy

1. **No Startup Preload**:
   `JobRepository.__init__()` initializes `_dataset` and `_id_index` as `None`. Zero memory footprint overhead from JSON files on normal boot.
2. **Strict Availability Check**:
   If MongoDB is unreachable, the system raises `HTTPException(503, "Primary datastore MongoDB is unavailable")` by default. Silent degradation that hides database outages is prohibited.
3. **Explicit Fallback Mode (For Offline Tests Only)**:
   Only when `ENABLE_JSON_FALLBACK=True` is explicitly configured will `_ensure_fallback_data()` lazily read the local backup snapshot, accompanied by a prominent warning log `[FALLBACK DEGRADED]`.
4. **Deep Health Check**:
   `/health` actively probes MongoDB status, returning `engine`, `status`, `collection`, `document_count` (2,251), and `indexes`.
