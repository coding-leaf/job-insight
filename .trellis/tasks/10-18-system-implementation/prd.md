# 全栈多页面数据分析与检索系统实现 (Parent Task PRD)

## Goal

构建 JobInsight 招聘数据多维分析与深度检索系统。基于已清洗并严格验证的 2,251 组招聘数据，打造兼具学术严肃性与工程实用性的全栈应用：
- 摒弃单页面玩具感与无意义的实现过程自嗨，提供专门面向“数据展示与深度使用”的四核心业务页面；
- 采用常驻次顶栏进行全局切片（Pinia + URL Query 双向同步），实现跨页面分析上下文无缝共享；
- 后端采用 FastAPI + Motor 异步驱动，利用 MongoDB 聚合管道实现毫秒级动态多维交叉切片。

## Task Tree & Scope Decomposition

- **Parent Task (当前任务)**: `10-18-system-implementation` — 全局架构、API 契约规范、集成验收与联调。
  - **Child Task 1**: `10-18-backend-data-and-api` — Docker Compose (mongo:7.0)、backend/ .venv 隔离环境、MongoDB 2251 组数据持久化与 4 组复合索引、FastAPI 异步聚合 API 及端点单元测试。
  - **Child Task 2**: `10-18-frontend-analytics-views` — Vite + Vue 3 + TS + Element Plus + ECharts + Pinia + Vue Router 多页面工程搭建、常驻全局切片次顶栏、4 大业务页面与岗位详情抽屉。

## System Requirements

1. **业务与功能定位**：
   - 纯只读数据展示与多维使用系统，不引入用户登录/权限与岗位 CRUD 等无关冗余；
   - 坚守真实数据底座，所有图表指标严谨标明样本量 $N$ 与分母口径，严格执行样本量不足 5 组不入榜或低置信度警告规则。
2. **多页面功能架构**：
   - `Overview` (`/overview`)：宏观核心 KPI 看板（2251 组全貌、2194 薪资基准、833 技能基准）、全行业薪资中位数、技术方向构成比、核心专题导航；
   - `Salary` (`/salary`)：类别薪资中位数排行（中位数条形图，标注样本量 N）、31 省份薪资梯度分布、企业规模与性质薪酬对比；
   - `Skills` (`/skills`)：Top 20 核心技术栈渗透率（严格展示 833 标注基准 vs 2251 全量基准双分母覆盖率）、各技术方向技能雷达画像、技术栈共现组合；
   - `Jobs` (`/jobs`)：在招岗位深度检索工作台（继承全局切片，支持关键字搜索、薪资过滤、分页表格、点击行滑出抽屉展示 19 列未修饰值与技能抽取溯源证据链）。
3. **全局切片条 (Global Slicer)**：
   - 顶部导航下方常驻次顶栏，包含：技术方向、目标省份、学历门槛、重置按钮；
   - 切片状态由 Pinia Store 集中管理，并双向同步至浏览器 URL Query 参数（`?category=...&province=...`），跨页面切换无缝保持，支持浏览器刷新与前进后退。
4. **技术栈与依赖约束**：
   - 后端：Python 3.11 + FastAPI + Motor 异步驱动 + Pydantic v2 + Uvicorn；
   - 数据库：Docker Compose 编排 `mongo:7.0`，映射 `27017:27017`，数据卷持久化；
   - 前端：Vite + Vue 3 + TypeScript + Element Plus + Apache ECharts + Pinia + Vue Router + Axios。

## Cross-Child Acceptance Criteria

- [ ] **AC-1 (环境与数据库持久化)**：通过 `docker-compose.yml` 成功拉起 MongoDB 7.0 容器；执行 `backend/app/db/seed.py` 成功将 2,251 组岗位数据导入集合 `jobs`，并建立 4 组只读复合索引。
- [ ] **AC-2 (后端聚合性能与契约一致性)**：FastAPI 后端提供 `/api/v1/overview`、`/api/v1/meta/options`、`/api/v1/stats/salary-by-category`、`/api/v1/stats/education-salary`、`/api/v1/stats/skills-top`、`/api/v1/jobs` 接口；响应时间均在 20ms 以内；统一输出 `{ code: 200, message: "success", data }` 包裹体；支持通用切片参数。
- [ ] **AC-3 (统计口径与门槛一致性)**：薪资中位数与四分位基于 2,194 组有效样本计算；样本数小于 5 组的技术类别被明确剔除或附带 low_confidence 标志；技能频次统计严格提供双分母（标注基准 833 与全量基准 2251）。
- [ ] **AC-4 (前端多页面工程与路由)**：前端成功配置 Vue Router 4 大独立视图（`/overview`, `/salary`, `/skills`, `/jobs`），页面无单页拥挤感，各页面图表渲染完整。
- [ ] **AC-5 (常驻切片栏与状态连续性)**：常驻次顶栏选择条件后，URL Query 自动更新；在 4 个页面间切换时，筛选状态完整保留并联动各页面图表重新请求。
- [ ] **AC-6 (岗位透视与溯源下钻)**：`/jobs` 页面表格分页流畅，点击任意岗位行可展开抽屉，查阅包含原始 19 列分组代表 ID、招聘正文与技能溯源依据详情。
