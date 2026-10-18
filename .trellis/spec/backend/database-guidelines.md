# Backend Database & MongoDB Guidelines

## Overview

The persistence layer connects to MongoDB 7.0 via Motor (`AsyncIOMotorClient`). Data is seeded from `data/processed/jobs_cleaned_grouped.json` (2,251 records).

---

## Database Configuration

- Database Name: `job_insight`
- Collection: `jobs`
- Environment Variables:
  - `MONGODB_URL`: `mongodb://localhost:27017`
  - `DATABASE_NAME`: `job_insight`

---

## Required Indexes

The `jobs` collection maintains 4 compound and single-field indexes built by `app/db/seed.py`:

1. `idx_category_province`: `[("job_category", 1), ("province", 1)]`
2. `idx_salary_category`: `[("salary_eligible_for_midpoint", 1), ("job_category", 1)]`
3. `idx_education_min_code`: `[("education_min_code", 1)]`
4. `idx_skills_name`: `[("skills.skill_name", 1)]`

---

## Native MongoDB Aggregation Pipelines

All analytical and statistical operations in `backend/app/db/repository.py` execute as native MongoDB aggregation pipelines when a database connection is active:

1. **Overview Metrics (`_mongo_get_overview`)**:
   Uses `$facet` to compute `total`, `eligible_salaries`, `tagged_skills_count`, `duplicate_groups_count`, and `categories` in a single round-trip.
2. **Category Salary Rankings (`_mongo_get_salary_by_category`)**:
   Uses `$match` -> `$sort: {"salary_midpoint": 1}` -> `$group: {"_id": "$job_category", "salaries": {"$push": "$salary_midpoint"}}` to pull sorted salary arrays for exact P25/Median/P75 calculation.
3. **Regional Salary Gradient (`_mongo_get_salary_by_region`)**:
   Uses `$match` -> `$sort` -> `$group: {"_id": "$province", "salaries": {"$push": "$salary_midpoint"}}`.
4. **Skills Penetration Top 20 (`_mongo_get_skills_top`)**:
   Uses `$match` -> `$unwind: "$skills"` -> `$group: {"_id": "$skills.skill_name", "count": {"$sum": 1}}` -> `$sort: {"count": -1}` -> `$limit: limit`.
5. **Job Explorer Search & Pagination (`_mongo_get_jobs`)**:
   Uses native Motor `db.jobs.find(query).sort().skip().limit()` alongside `db.jobs.count_documents(query)`.

---

## Dual Dispatch & Offline Fallback

`JobRepository` checks `get_database()`:
- **Online (Primary)**: 100% executes native Motor aggregation pipelines hitting the 4 compound indexes.
- **Offline (Fallback)**: When Docker/MongoDB is unstarted, falls back smoothly to an in-memory dataset, ensuring development and local CI tests never deadlock.
