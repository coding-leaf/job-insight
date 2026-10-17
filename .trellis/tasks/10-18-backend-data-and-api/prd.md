# 后端环境搭建、MongoDB入库与核心聚合API开发 (PRD)

## Goal

为 JobInsight 系统搭建完整的异步后端与数据库支撑底座：
1. 根目录编写 `docker-compose.yml`，以标准方式编排 MongoDB 7.0 实例；
2. 在 `backend/` 下建立独立的 Python 3.11 虚拟环境（`.venv`），配置精确的依赖库（FastAPI, Motor, Pydantic, Uvicorn）；
3. 编写 `seed.py` 脚本，将规范化后的 `data/processed/jobs_cleaned_grouped.json`（2,251 组）灌入 MongoDB `job_insight.jobs` 集合，并创建针对性复合索引；
4. 实现基于 FastAPI 的异步路由分层架构，提供 6 大聚合与检索接口，严格落实 5 组样本门槛、2194 组有效薪资中点与 833 组技能双分母统计口径；
5. 编写自动化 API 单元测试套件，确保所有端点高并发非阻塞、响应时间小于 20ms。

## Requirements

1. **容器与环境隔离**：
   - Docker Compose 暴露 `27017:27017`，挂载本地数据卷 `mongo_data`；
   - 后端通过 `backend/.env`（或环境变量）读取 `MONGODB_URL=mongodb://localhost:27017/job_insight`，可无缝兼容本地原生安装或 Docker 容器；
   - 依赖项固定于 `backend/requirements.txt`。
2. **数据灌库与索引**：
   - 导入数据源：`data/processed/jobs_cleaned_grouped.json`；
   - 目标集合：`jobs`，严格校验入库文档数量为 2,251；
   - 必须创建 4 组索引：
     - `[("job_category", 1), ("province", 1)]`
     - `[("salary_eligible_for_midpoint", 1), ("job_category", 1)]`
     - `[("education_min_code", 1)]`
     - `[("skills.skill_name", 1)]`
3. **接口定义与口径约束**：
   - 统一包裹格式：`{ "code": 200, "message": "success", "data": ... }`；
   - 通用 Query 切片依赖：`category: Optional[str]`, `province: Optional[str]`, `education: Optional[str]`；
   - `GET /api/v1/meta/options`：切片候选值列表（类别、省份、学历）；
   - `GET /api/v1/overview`：总体规模、薪资中位数、技术构成比；
   - `GET /api/v1/stats/salary-by-category`：类别薪资排行、P25/P50/P75 四分位，样本 $N < 5$ 标记或剔除；
   - `GET /api/v1/stats/salary-by-region`：省份薪资分布与岗位数量；
   - `GET /api/v1/stats/skills-top`：Top 技能排行，严格返回 `ratio_annotated` ($count/833$) 与 `ratio_total` ($count/2251$)；
   - `GET /api/v1/jobs`：复合多维分页检索，返回 `items` 与 `total`。
4. **性能与异常处理**：
   - 全异步 I/O：使用 `Motor`，严禁在 `async def` 路由中使用同步阻塞代码；
   - 全局异常拦截器捕获 404, 422, 500 并统一输出包装结构。

## Acceptance Criteria

- [ ] **AC-1 (Docker编排与环境)**：`docker-compose.yml` 语法合法，可拉起 MongoDB 7.0 服务；`backend/.venv` 虚拟环境搭建完成，`pip install -r requirements.txt` 无报错。
- [ ] **AC-2 (数据灌库与索引验证)**：执行 `seed.py` 成功导入 2251 条文档，集合 `jobs` 拥有 4 组预期索引且索引命中正常。
- [ ] **AC-3 (接口功能与统计口径验证)**：编写 pytest 自动化测试，验证 6 大核心端点：
  - `/overview` 统计总数 2251，有效薪资组 2194，标注技能组 833；
  - `/stats/salary-by-category` 中各类别薪资中位数与离线校验值一致，且小样本被置信度标记；
  - `/stats/skills-top` 具备双分母覆盖率数值；
  - `/jobs` 支持过滤与分页。
- [ ] **AC-4 (响应时间与异步非阻塞)**：所有测试在 20ms 内完成单接口查询，Ruff 检查 0 错误。
