# JobInsight 招聘薪资与技能需求分析系统

面向公开招聘数据（基于 2,251 组严格清洗与交叉验证的基准样本）构建的全栈求职选岗与大数据分析系统。提供**条件选岗、本地候选清单、多岗位并排对比、技能标签辅助核对**以及多维宏观数据分析（薪资分布、技能频次双分母统计）。

---

## 核心架构

- **后端**：FastAPI (Python 3.11+) + Motor 异步驱动 + 复合索引 MongoDB 7.0（支持脱机真实 JSON 自动容灾回退）
- **前端**：Vue 3 + TypeScript + Vite + Element Plus + Pinia + ECharts 6
- **数据**：`data/processed/jobs_cleaned_grouped.json`（2,251 组闭环招聘样本）

---

## 快速部署与本地运行

### 前置环境
- Python 3.11+
- Node.js 18+（推荐 20 或 22+）
- Docker & Docker Compose（可选，脱机模式无需启动）

---

### 方式一：轻量开发模式（推荐，无需 Docker）

后端内置了数据容灾机制，未连接 MongoDB 时会自动无缝读取本地基准数据，无需启动数据库即可直接体验完整功能。

#### 1. 启动后端（端口 8000）
```bash
# 1. 准备并激活虚拟环境（若已有 backend/.venv 可直接使用）
python -m venv backend/.venv

# Windows PowerShell:
.\backend\.venv\Scripts\activate
# Linux / macOS:
source backend/.venv/bin/activate

# 2. 安装依赖
pip install -r backend/requirements.txt

# 3. 启动 FastAPI 服务
uvicorn backend.app.main:app --reload --port 8000
```

#### 2. 启动前端（端口 5173）
新开一个终端窗口：
```bash
cd frontend

# 安装前端依赖
npm install

# 启动开发服务器（自动代理 /api 到 8000 端口）
npm run dev
```

#### 3. 访问系统
- **前端系统入口**：[http://localhost:5173/](http://localhost:5173/)（默认进入 `/workbench` 选岗工作台）
- **API 交互文档**：[http://localhost:8000/docs](http://localhost:8000/docs)（Swagger UI）

---

### 方式二：完整数据库模式（MongoDB 原生聚合管道加速）

若需测试 MongoDB 原生复合索引与聚合加速：

1. **启动 MongoDB 容器**：
   ```bash
   docker compose up -d
   ```
2. **初始化数据灌库与创建 4 组复合索引**：
   ```bash
   # Windows PowerShell:
   .\backend\.venv\Scripts\python.exe backend/app/db/seed.py
   # Linux / macOS:
   python backend/app/db/seed.py
   ```
3. **按方式一分别启动后端与前端服务**即可。

---

## 前端构建与生产部署

```bash
cd frontend
# 运行类型检查并打包生产静态资源
npm run build
```
打包输出目录为 `frontend/dist/`，可直接部署至 Nginx 等静态资源服务器，反向代理 `/api/` 请求到 FastAPI 后端即可。

---

## 自动化测试与质量校验

```bash
# 前端单元测试 (Vitest, 42 项全部通过)
npm --prefix frontend run test:unit

# 前端类型检查与构建校验
npm --prefix frontend run build

# 后端接口契约测试 (Pytest, 12 项全部通过)
pytest backend/tests/test_api.py -q
```
