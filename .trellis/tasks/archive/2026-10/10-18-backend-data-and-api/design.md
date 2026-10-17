# 后端环境搭建、MongoDB入库与核心聚合API技术设计 (Design)

## 1. 目录结构设计

```text
backend/
├── app/
│   ├── api/
│   │   ├── deps.py               # 通用 Query 切片依赖注入 (FilterParams)
│   │   └── v1/
│   │       ├── api.py            # API 路由聚合器 (include_router)
│   │       └── endpoints/
│   │           ├── meta.py       # 切片选项
│   │           ├── overview.py   # 总览指标
│   │           ├── stats.py      # 薪资、地域与技能聚合
│   │           └── jobs.py       # 岗位列表检索与详情
│   ├── core/
│   │   └── config.py             # pydantic-settings 读取 .env 配置
│   ├── db/
│   │   ├── mongodb.py            # Motor 异步客户端生命周期管理 (lifespan)
│   │   └── seed.py               # 数据入库与索引创建脚本
│   ├── schemas/
│   │   ├── response.py           # 统一响应包装体 ResponseModel[T]
│   │   └── job.py                # Pydantic 过滤与数据模型
│   └── main.py                   # FastAPI 应用入口、CORS、异常处理器
├── tests/
│   ├── conftest.py               # 异步测试 fixture 与 mock/test client
│   └── test_api.py               # AC-3 核心接口契约测试
├── requirements.txt              # 锁定依赖项
└── .env.example                  # 环境变量示例
```

## 2. 数据层设计与索引策略

数据源：`data/processed/jobs_cleaned_grouped.json`

### 集合与索引
- Database: `job_insight`
- Collection: `jobs`
- Indexes:
  1. `[("job_category", 1), ("province", 1)]` -> 支持按类别+省份的快速切片
  2. `[("salary_eligible_for_midpoint", 1), ("job_category", 1)]` -> 支持薪资统计快速过滤排除项
  3. `[("education_min_code", 1)]` -> 支持学历范围过滤
  4. `[("skills.skill_name", 1)]` -> 支持技能反查与展开统计

## 3. 聚合管道 (Aggregation Pipeline) 模式

- **类别薪资排行**：
  ```json
  [
    { "$match": { "salary_eligible_for_midpoint": true, ...filters } },
    { "$group": {
        "_id": "$job_category",
        "sample_count": { "$sum": 1 },
        "salaries": { "$push": "$salary_midpoint" }
    }},
    { "$project": {
        "category": "$_id",
        "sample_count": 1,
        "is_low_sample": { "$lt": ["$sample_count", 5] },
        "salaries": 1
    }}
  ]
  ```
  在 Python 异步处理中，对已排序的 salaries 快速计算 Exact Median、P25、P75。

- **Top 技能统计**：
  ```json
  [
    { "$match": { ...filters } },
    { "$unwind": "$skills" },
    { "$group": {
        "_id": "$skills.skill_name",
        "count": { "$sum": 1 }
    }},
    { "$sort": { "count": -1 } },
    { "$limit": 20 }
  ]
  ```
  计算 `ratio_annotated = count / 833`，`ratio_total = count / 2251`。
