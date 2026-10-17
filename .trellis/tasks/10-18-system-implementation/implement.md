# 全栈多页面数据分析与检索系统实施计划 (Parent Task Implementation)

## 任务执行路线图

本父任务统筹两个可独立开发与验证的子任务：

```text
[阶段 1: 后端与数据库] (子任务: 10-18-backend-data-and-api)
  ├── 1.1 编写根目录 docker-compose.yml 并拉起 mongo:7.0 容器
  ├── 1.2 创建 backend/ 目录与 Python 3.11 .venv 虚拟环境，编写 requirements.txt
  ├── 1.3 编写 backend/app/db/seed.py 导入 2251 组数据并创建复合索引
  ├── 1.4 编写 FastAPI 异步架构 (app/api, app/models, app/services, app/db)
  ├── 1.5 实现 6 大核心聚合与检索 API
  └── 1.6 编写自动化 API 单元测试并验证 AC-1 ~ AC-3
                               │
                               v
[阶段 2: 前端多页面工程] (子任务: 10-18-frontend-analytics-views)
  ├── 2.1 运行 Vite 官方脚手架初始化 frontend/ (vue-ts)
  ├── 2.2 安装 Element Plus, Apache ECharts, Pinia, Vue Router, Axios
  ├── 2.3 搭建基础布局：GlobalHeader 顶栏 + GlobalSlicer 常驻切片次顶栏 (Pinia + URL Query 同步)
  ├── 2.4 实现 4 大业务页面：Overview, Salary, Skills, Jobs
  ├── 2.5 实现 JobDetailDrawer 岗位溯源穿透抽屉
  └── 2.6 前后端全链路联调与验证 AC-4 ~ AC-6
                               │
                               v
[阶段 3: 全局集成与交付] (本父任务闭环)
  ├── 3.1 跨端端到端联调测试
  ├── 3.2 归档两个子任务与本父任务
  └── 3.3 记录最终工程日志
```
