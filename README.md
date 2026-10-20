# JobInsight 招聘薪资与技能需求分析系统

面向公开招聘数据深度展示与多维分析的大数据全栈分析系统。系统**以 MongoDB 7.0 作为核心主存储与聚合分析引擎**，后端完全面向 MongoDB 进行数据检索与复杂统计聚合。

- **核心数据库**：MongoDB 7.0（Motor 异步驱动，原生 Aggregation 管道，4 组复合索引支撑）
- **后端服务**：FastAPI (Python 3.11) 异步高性能架构，100% 数据库驱动，不依赖内存常驻大 JSON
- **前端分析**：Vue 3 + TypeScript + Vite + ECharts 响应式多维分析大屏
- **质量保障**：Pytest 自动化测试套件（20/20 契约通过，包含 MongoDB 原生聚合与端点时延测试）

---

## 1. 数据源说明与协作流程

### 数据私密性与协作原则
1. **数据源不可上传**：原始招聘源数据与清洗过程数据涉及私密性，**严禁上传到 Git 仓库**（已被 `.gitignore` 严格忽略保护）。
2. **离线协作传递**：规范数据由项目负责人通过私下渠道（如 QQ）发送给协作同学，仓库中不包含数据文件。
3. **前期一次性手动入库**：
   - 数据脚本是一次性针对特定脏数据字段编写的清洗工具，不具有通用性，无需也不应在日常运行中重复执行；
   - 协作同学收到数据后，在本地前期**手动执行一次导入 MongoDB 即可**（之后数据持久化在数据库中，不需要每次都重新洗数据或重复入库）；
   - 入库后建议创建的 4 组索引：
     - `idx_category_province`: `[("job_category", 1), ("province", 1)]`
     - `idx_salary_category`: `[("salary_eligible_for_midpoint", 1), ("job_category", 1)]`
     - `idx_education_min_code`: `[("education_min_code", 1)]`
     - `idx_skills_name`: `[("skills.skill_name", 1)]`
4. **降低 JSON 权重，以 MongoDB 为主内容**：
   - 彻底废除后端开机强制预载 4MB JSON 到内存的做法；
   - 系统的主要数据内容与查询完全由 MongoDB 承载；
   - 本地 JSON 仅作为离线冷备份或数据交换的载体，不再作为后端运行时的主要核心。

---

## 2. 系统快速启动指南

在数据已由前期手动导入本地 MongoDB 的前提下，日常运行极其简洁，无需重复入库：

### 步骤一：启动 MongoDB 数据库容器

系统使用 Docker Compose 编排 MongoDB 7.0 实例，数据持久化至本地 `mongo_data` 卷：

```bash
# 启动 MongoDB 容器 (端口 27017)
docker compose up -d
```

### 步骤二：启动 FastAPI 后端服务

后端默认直连本地 MongoDB（`mongodb://localhost:27017`，数据库 `job_insight`，集合 `jobs`）：

```bash
# 激活 Python 虚拟环境 (示例)
source .venv/bin/activate  # 或 Windows: .venv\Scripts\activate

# 启动后端服务 (端口 8000)
uvicorn backend.app.main:app --reload --port 8000
```

启动后可访问健康检查接口，实时确认 MongoDB 连接与数据量：
- 健康检查：[http://localhost:8000/health](http://localhost:8000/health)（返回 MongoDB 连接状态及文档总数）
- Swagger API 文档：[http://localhost:8000/docs](http://localhost:8000/docs)

### 步骤三：启动 Vue 3 前端分析大屏

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器 (自动代理 /api 到 8000 端口)
npm run dev
```

浏览器访问：[http://localhost:5173/](http://localhost:5173/)

---

## 3. 自动化测试与质量检验

```bash
# 运行后端自动化测试 (包含原生 MongoDB 管道验证)
pytest backend/tests/

# 运行代码规范检查
ruff check backend/

# 前端构建验证
cd frontend && npm run build
```
