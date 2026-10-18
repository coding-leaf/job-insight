# 原生 MongoDB 异步聚合管道重构设计方案 (Design)

## 1. 原生聚合管道架构设计

```text
FastAPI Endpoints (Overview, Stats, Jobs)
       │
       ▼
JobRepository (backend/app/db/repository.py)
       │
       ├─► 检查 MongoDB 实例连接 (db = get_database())
       │     │
       │     ├─► [在线 · 主通道] Motor 异步聚合管道 (db.jobs.aggregate)
       │     │     ├── Overview: $facet 多分支聚合
       │     │     ├── Salary by Category: $match -> $sort -> $group ($push salaries)
       │     │     ├── Salary by Region: $match -> $sort -> $group ($push salaries)
       │     │     ├── Skills Top: $match -> $unwind -> $group ($sum 1) -> $sort -> $limit
       │     │     └── Jobs Explorer: $match -> find().skip().limit() + count_documents
       │     │
       │     └─► [离线 · 兜底通道] 仅在未启动 Docker 时保障 pytest 与开发自愈
       │
       ▼
Pydantic Schemas Response (ResponseModel[T])
```

## 2. 核心聚合管道定义 (MongoDB Aggregation Pipelines)

### 2.1 Overview 聚合管道 (`$facet`)
```python
pipeline = [
    {"$match": match_filter},
    {
        "$facet": {
            "total": [{"$count": "count"}],
            "eligible_salaries": [
                {"$match": {"salary_eligible_for_midpoint": True}},
                {"$sort": {"salary_midpoint": 1}},
                {"$project": {"salary_midpoint": 1}},
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
```

### 2.2 类别薪资排行管道 (`$group` + `$push`)
```python
pipeline = [
    {"$match": {**match_filter, "salary_eligible_for_midpoint": True}},
    {"$sort": {"salary_midpoint": 1}},
    {
        "$group": {
            "_id": {"$ifNull": ["$job_category", "未分类"]},
            "sample_count": {"$sum": 1},
            "salaries": {"$push": "$salary_midpoint"},
        }
    },
]
```

### 2.3 Top 技能双分母管道 (`$unwind` + `$group`)
```python
pipeline = [
    {"$match": match_filter},
    {"$unwind": "$skills"},
    {
        "$group": {
            "_id": "$skills.skill_name",
            "count": {"$sum": 1},
        }
    },
    {"$sort": {"count": -1}},
    {"$limit": limit},
]
```

### 2.4 岗位检索查询构建 (`build_mongo_query`)
将统一筛选切片映射为 MongoDB 查询对象：
- `category`: `{"job_category": category}` 或 `{"job_category": None}` (当为未分类时)
- `province`: `{"province": province}`
- `education`: `{"education_requirement": education}`
- `keyword`: `{"$or": [{"title": regex}, {"company": regex}, {"description": regex}, {"skills.skill_name": regex}]}`
- `min_salary` & `max_salary`: `{"salary_eligible_for_midpoint": True, "salary_max_monthly": {"$gte": min_salary}, "salary_min_monthly": {"$lte": max_salary}}`
- `has_skills`: `{"skills.0": {"$exists": True}}` 或 `{"skills": {"$size": 0}}`
