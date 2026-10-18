# 原生 MongoDB 异步聚合管道实施计划 (Implement)

## 实施清单与检查点

- [x] **Step 1: MongoDB 查询构建器实现**
  - 在 `backend/app/db/repository.py` 实现 `_build_mongo_filter(...)` 函数，将 Python 参数严格转化为 MongoDB 原生查询语法。

- [x] **Step 2: 原生聚合管道方法开发**
  - 实现 `_mongo_get_overview(...)`：采用 `$facet` 聚合提取 total, eligible_salaries, tagged_skills_count, duplicate_groups_count, categories；
  - 实现 `_mongo_get_salary_by_category(...)`：采用 `$match` -> `$sort` -> `$group` 聚合获取各类别有序薪资列表并由分位数算法计算 P25/P50/P75；
  - 实现 `_mongo_get_salary_by_region(...)`：采用 `$match` -> `$sort` -> `$group` 聚合获取省份薪资；
  - 实现 `_mongo_get_skills_top(...)`：采用 `$match` -> `$unwind` -> `$group` 聚合获取技能排行与双分母；
  - 实现 `_mongo_get_jobs(...)`：采用 `find().sort().skip().limit()` 与 `count_documents()`；
  - 实现 `_mongo_get_job_by_id(...)`：采用 `find_one()`。

- [x] **Step 3: 双轨路由调度与自愈验证**
  - 在 `get_overview`、`get_salary_by_category` 等公开方法中优先检查 `db = get_database()`：
    - 若 `db is not None`：优先调用 `_mongo_*` 异步管道方法；
    - 若 `db is None`：记录日志并平滑降级到内存引擎，保障离线单测。

- [x] **Step 4: 测试与代码检查**
  - 执行 `backend/.venv/Scripts/pytest backend/tests/` 确保所有 12 项测试通过；
  - 执行 `backend/.venv/Scripts/ruff check backend/` 确保 0 警告 0 报错。
