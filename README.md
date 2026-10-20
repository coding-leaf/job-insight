# 部署指南

## 前置环境
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose（可选）

---

## 方式一：轻量开发模式（无需 Docker）

后端未连接 MongoDB 时会自动读取本地基准数据，无需启动数据库即可直接运行。

### 1. 启动后端（端口 8000）
```bash
# 创建并激活虚拟环境（若已有 backend/.venv 可直接使用）
python -m venv backend/.venv

# Windows PowerShell:
.\backend\.venv\Scripts\activate
# Linux / macOS:
source backend/.venv/bin/activate

# 安装依赖
pip install -r backend/requirements.txt

# 启动后端服务
uvicorn backend.app.main:app --reload --port 8000
```

### 2. 启动前端（端口 5173）
新开终端窗口：
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器（自动代理 /api 到 8000 端口）
npm run dev
```

### 3. 访问系统
- 前端入口：[http://localhost:5173/](http://localhost:5173/)
- API 交互文档：[http://localhost:8000/docs](http://localhost:8000/docs)

---

## 方式二：完整数据库模式（MongoDB）

1. **启动 MongoDB 容器**：
   ```bash
   docker compose up -d
   ```

2. **初始化数据与创建索引**：
   ```bash
   # Windows PowerShell:
   .\backend\.venv\Scripts\python.exe backend/app/db/seed.py
   # Linux / macOS:
   python backend/app/db/seed.py
   ```

3. **启动后端与前端**（步骤同方式一）。

---

## 生产构建部署

```bash
cd frontend
npm run build
```
构建产物输出至 `frontend/dist/`，可使用 Nginx 作为静态服务器，反向代理 `/api/` 到后端 8000 端口。
