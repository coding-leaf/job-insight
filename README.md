# JobInsight 招聘薪资与技能需求分析系统

面向公开招聘数据深度展示与多维分析的大数据全栈分析系统。系统**以 MongoDB 7.0 作为核心主存储与聚合分析引擎**，后端完全面向 MongoDB 进行数据检索与复杂统计聚合。

- **核心数据库**：MongoDB 7.0（Motor 异步驱动，原生 Aggregation 管道，4 组复合索引支撑）
- **后端服务**：FastAPI (Python 3.11) 异步高性能架构，100% 数据库驱动，不依赖内存常驻大 JSON
- **前端分析**：Vue 3 + TypeScript + Vite + ECharts 响应式多维分析大屏
- **质量保障**：Pytest 自动化测试套件（20/20 契约通过，包含 MongoDB 原生聚合与端点时延测试）

---

## 1. 数据说明与协作原则

1. **数据源私密保护**：原始招聘数据与清洗过程数据涉及隐私脱敏资产，**未上传至公开仓库**（受 `.gitignore` 保护）。
2. **基准数据离线分发**：项目负责人将最终清洗确认的基准数据集（Golden Dataset）打包为 `jobs.json` 发送给协作同学。
3. **前期一次性导入**：协作同学获取数据后，**仅需在本地执行一次导入命令**；数据持久化至 MongoDB 数据卷后，日常开发启动无需再次导入或重复清洗。

---

## 2. 快速部署与运行指南

### 步骤一：启动 MongoDB 数据库容器

系统使用 Docker Compose 编排 MongoDB 7.0 实例，数据持久化至本地 `mongo_data` 卷：

```bash
# 启动 MongoDB 容器 (端口映射 27017:27017)
docker compose up -d
```

### 步骤二：数据导入与索引构建 (仅首次运行需要)

1. 从项目负责人处获取 `job_data.zip` 并解压得到 `jobs.json`；
2. 运行初始化脚本一键导入数据并自动建立 4 组复合索引：

```bash
# Windows / Linux 示例 (指定解压后的 jobs.json 路径)
python backend/app/db/seed.py --data-path <你的jobs.json实际路径>
```

> **提示**：导入成功后将显示 `Successfully inserted 2251 documents` 及 `Created 4 required indexes`。数据已安全持久化在本地 Docker 卷中，日常启动无需再次运行此步骤。

### 步骤三：启动 FastAPI 后端服务

后端直连本地 MongoDB 提供数据查询与聚合 API：

```bash
# 激活 Python 虚拟环境 (示例)
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 启动后端服务 (端口 8000)
uvicorn backend.app.main:app --reload --port 8000
```

启动后可访问健康检查接口，确认 MongoDB 连接状态与数据容量：
- 健康检查：[http://localhost:8000/health](http://localhost:8000/health)（实时返回 MongoDB 状态与 2,251 组数据指标）
- Swagger API 文档：[http://localhost:8000/docs](http://localhost:8000/docs)

### 步骤四：启动 Vue 3 前端开发服务

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器 (自动代理 /api 到 8000 端口)
npm run dev
```

浏览器访问：[http://localhost:5173/](http://localhost:5173/) 即可开始体验完整分析大屏。

---

## 3. 自动化测试与质量检验

```bash
# 运行后端自动化测试 (包含原生 MongoDB 聚合管道验证)
pytest backend/tests/

# 运行代码规范检查
ruff check backend/

# 前端构建验证
cd frontend && npm run build
```
