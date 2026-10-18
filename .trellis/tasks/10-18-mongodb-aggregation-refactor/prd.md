# 重构后端为原生MongoDB异步聚合管道 (PRD)

## Goal

将 `backend/app/db/repository.py` 全面重构为**基于 Motor 异步驱动的原生 MongoDB 聚合管道实现**：
1. 宏观概览指标 (`get_overview`) 采用 MongoDB `$facet` 多维分支管道异步计算；
2. 类别薪资排行 (`get_salary_by_category`) 采用 `$match` -> `$sort` -> `$group` (按类别推入有序薪资数组) 管道计算；
3. 省份薪资梯度 (`get_salary_by_region`) 采用 `$match` -> `$sort` -> `$group` (按省份分组统计) 管道计算；
4. Top 技能排行 (`get_skills_top`) 采用 `$match` -> `$unwind` -> `$group` (技能频次聚合) -> `$sort` -> `$limit` 管道计算；
5. 岗位多维检索与翻页 (`get_jobs`) 采用原生 `db.jobs.find().skip().limit()` 与 `count_documents()`；
6. 严格执行双轨设计：当 MongoDB 数据库服务在线时，100% 走原生 MongoDB 异步聚合管道并命中复合索引；当离线无连接时提供清晰警告与内存降级，保障离线单体测试与开发零死锁。

## Requirements

1. **MongoDB 聚合管道语法标准**：
   - 使用 Motor `db.jobs.aggregate([...]).to_list(length=None)` 执行所有统计分析；
   - 过滤条件构建：将 `category`, `province`, `education`, `keyword`, `min_salary`, `max_salary`, `has_skills` 转化为原生 MongoDB 查询操作符（`$and`, `$regex`, `$gte`, `$lte`, `$exists`）；
   - 薪资与切片聚合优先利用集合上建立的 4 组复合索引。
2. **聚合统计口径严格保持一致**：
   - Overview: 全量 $2251$、有效薪资 $2194$、技能打标 $833$、全行业中位数 $12000.0$；
   - Salary Category: 算法与人工智能 $17500.0$、软件开发 $12500.0$；项目与产品 $N=4$ 打上 `is_low_sample: True` 并从排名剔除；
   - Skills Top: Python 307 ($307/833$ vs $307/2251$)、C++ 234、Linux 214，双分母精准输出。
3. **高并发非阻塞与代码整洁**：
   - 所有方法维持 `async def`，杜绝任何同步阻塞调用；
   - 代码严格遵守 Python 类型注解与 Ruff 校验规范。

## Acceptance Criteria

- [x] **AC-1 (原生聚合管道覆盖)**：`repository.py` 内实现原生 MongoDB 聚合管道方法（`_aggregate_overview`, `_aggregate_salary_by_category`, `_aggregate_salary_by_region`, `_aggregate_skills_top`, `_query_jobs`），每个方法包含显式 `$aggregate` / `$facet` / `$unwind` 管道定义。
- [x] **AC-2 (统计口径与契约验证)**：现有 `backend/tests/test_api.py` 的 12 项测试全部无损通过，返回的宏观基准数、分位数、双分母与低样本标记完全一致。
- [x] **AC-3 (代码质量与静态类型)**：运行 `ruff check backend/` 检查 0 错误、0 警告。
