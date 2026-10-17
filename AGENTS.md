<!-- TRELLIS:START -->
# Trellis Instructions

These instructions are for AI assistants working in this project.

This project is managed by Trellis. The working knowledge you need lives under `.trellis/`:

- `.trellis/workflow.md` — development phases, when to create tasks, skill routing
- `.trellis/spec/` — package- and layer-scoped coding guidelines (read before writing code in a given layer)
- `.trellis/workspace/` — per-developer journals and session traces
- `.trellis/tasks/` — active and archived tasks (PRDs, research, jsonl context)

If a Trellis command is available on your platform (e.g. `/trellis:finish-work`, `/trellis:continue`), prefer it over manual steps. Not every platform exposes every command.

If you're using Codex or another agent-capable tool, additional project-scoped helpers may live in:
- `.agents/skills/` — reusable Trellis skills
- `.codex/agents/` — optional custom subagents

Managed by Trellis. Edits outside this block are preserved; edits inside may be overwritten by a future `trellis update`.

<!-- TRELLIS:END -->

# JobInsight 招聘薪资与技能需求分析系统 · 工程与协作指引

本项目是一个面向公开招聘数据深度展示与多维分析的大数据全栈系统，基于已清洗并严格验证的 2,251 组基准招聘数据构建。

## 1. 核心架构与工程目录

```text
job-insight/
├── backend/                  # FastAPI 异步后端 (Python 3.11)
│   ├── app/
│   │   ├── api/v1/endpoints/ # 6 大核心聚合与检索 API
│   │   ├── core/             # Pydantic BaseSettings (.env 配置)
│   │   ├── db/               # Motor 异步驱动、seed.py 数据入库与 4 组复合索引
│   │   └── schemas/          # 统一响应包装体 ResponseModel[T] 与领域契约
│   ├── tests/                # 自动化 pytest 测试套件 (12/12 契约通过)
│   └── requirements.txt      # 后端固定依赖清单
├── frontend/                 # Vue 3 + TS 多页面分析系统 (Vite)
│   ├── src/
│   │   ├── api/              # 统一 Axios 客户端与端点函数
│   │   ├── components/       # GlobalHeader, GlobalSlicer, JobDetailDrawer
│   │   ├── composables/      # useECharts 深函数 (自动 resize 与资源释放)
│   │   ├── stores/           # Pinia 全局切片状态 (useFilterStore)
│   │   └── views/            # 4 大专业业务页面 (Overview, Salary, Skills, Jobs)
│   └── package.json
├── data/processed/           # 经过 19 列分组清洗的 2,251 组基准数据
├── docker-compose.yml        # MongoDB 7.0 容器编排 (映射 27017:27017, 数据卷持久化)
└── temp/data_prep/           # 过程性清洗与契约验证归档脚本
```

## 2. 核心开发与运行准则 (团队铁律)

1. **代码为准则**：前端 TypeScript 类型契约与后端 Pydantic 数据模型严格 1:1 对齐，严禁类型割裂。
2. **架构应复用**：
   - 后端统一响应包装体 `{ code: 200, message: "success", data: ... }`；
   - 前端统一 Axios 拦截解包，统一使用 `useFilterStore` 管理切片，统一使用 `useECharts` 驱动可视化。
3. **方法要深函数**：
   - 组件提供极其精炼的 Props/Events 外部接口，将复杂的自适应监听、DOM 挂载与详情异步加载完全内敛（如 `<JobDetailDrawer>`、`useECharts`）。
4. **KISS 准则**：
   - 杜绝过度设计，不搞华而不实的状态机与多余抽象；
   - 系统纯粹为“数据展示与深度使用”服务，不掺杂无关的用户登录与 CRUD 冗余。
5. **绝对严禁编纂数据**：
   - 前端图表、KPI 与表格 100% 动态读取自真实后端 API，严禁前端伪造假数字；
   - 薪资统计严格基于 2,194 组有效闭区间，样本数 $N < 5$ 必须标记预警；
   - 技能统计严格呈现双分母（标注基准 833 覆盖率 vs 全量基准 2251 覆盖率）。

## 3. 常用运行与测试指令

### 后端运行与测试
```bash
# 启动 MongoDB 容器
docker compose up -d

# 数据灌库 (初始化导入 2251 组数据并创建 4 组复合索引)
python backend/app/db/seed.py

# 启动 FastAPI 后端服务 (端口 8000)
uvicorn backend.app.main:app --reload --port 8000

# 运行自动化测试与静态检查
pytest backend/tests/
ruff check backend/
```

### 前端运行与构建
```bash
cd frontend
# 安装依赖
npm install

# 启动开发服务器 (自动代理 /api 到 8000)
npm run dev

# 生产环境类型检查与构建
npm run build
```

