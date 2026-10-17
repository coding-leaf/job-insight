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

## Aggregation & Statistical Rules

1. **Sample Threshold ($N < 5$)**: Categories with fewer than 5 eligible records (e.g., "项目与产品" with $N=4$) must have `is_low_sample: True` and be excluded from primary ranking charts.
2. **Dual-Denominator Skill Coverage**:
   - `ratio_annotated`: $count / 833$ (proportion among jobs with explicit skill annotations).
   - `ratio_total`: $count / 2251$ (proportion among all grouped jobs).
3. **Quartile Calculations**: P25, P50 (Median), and P75 must be calculated from sorted salary midpoints on valid records (`salary_eligible_for_midpoint == True`).
