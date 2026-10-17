# 后端环境搭建、MongoDB入库与核心聚合API实施计划 (Implement)

## 实施清单与检查点

- [ ] **Step 1: 基础设施编排**
  - 创建根目录 `docker-compose.yml`（服务名 `mongo`，镜像 `mongo:7.0`，映射 `27017:27017`，数据卷 `mongo_data`）；
  - 编写 `backend/requirements.txt` 与 `backend/.env.example`。

- [ ] **Step 2: 虚拟环境搭建与依赖安装**
  - 在 `backend/` 下执行 `python -m venv .venv` 创建虚拟环境；
  - 激活虚拟环境并安装核心依赖：`fastapi`, `uvicorn[standard]`, `motor`, `pydantic`, `pydantic-settings`, `pytest`, `httpx`。

- [ ] **Step 3: MongoDB 数据导入与索引初始化**
  - 编写 `backend/app/db/seed.py`；
  - 读取 `data/processed/jobs_cleaned_grouped.json`，连接 MongoDB 执行批量写入；
  - 创建 4 组复合索引；
  - 校验文档数量（必须严格为 2251 条）与索引状态。

- [ ] **Step 4: FastAPI 异步框架与路由开发**
  - 编写 `backend/app/core/config.py` 读取环境配置；
  - 编写 `backend/app/db/mongodb.py` 管理 Motor 客户端生命周期；
  - 编写 `backend/app/schemas/response.py` 实现统一包装体；
  - 编写 `backend/app/api/deps.py` 实现切片参数共享依赖；
  - 编写 `backend/app/api/v1/endpoints/meta.py`（切片候选字典）；
  - 编写 `backend/app/api/v1/endpoints/overview.py`（宏观 KPI 指标）；
  - 编写 `backend/app/api/v1/endpoints/stats.py`（薪资中位数、地域梯队、Top技能双分母覆盖率）；
  - 编写 `backend/app/api/v1/endpoints/jobs.py`（多维检索与分页）；
  - 编写 `backend/app/main.py` 挂载路由、CORS 中间件与全局异常处理器。

- [ ] **Step 5: 自动化测试与质量验收**
  - 编写 `backend/tests/test_api.py`，使用 `httpx.AsyncClient` 进行端到端测试；
  - 验证 AC-1 ~ AC-4 全部通过；
  - 运行 `python -m ruff check backend/` 确保 0 警告 0 报错。
