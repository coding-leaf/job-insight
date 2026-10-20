# Journal - coding-leaf (Part 1)

> AI development session journal
> Started: 2026-10-17

---



## Session 1: JobInsight data contract v1
<!-- trellis-session: v=2 fp=d4832c6e4beda7ed -->

**Date**: 2026-10-17
**Task**: JobInsight data contract v1

### Summary

Completed approved documentation-only field redesign, offline classification review format and statistical methodology; original data unchanged.

### Main Changes

- Added four data documents and updated handoff and Trellis data-contract entry points.
- Archived 10-17-data-contract; preserved unfinished 00-bootstrap-guidelines. No Git repository, application code or data processing.

### Git Commits

(No commits - planning session)

### Testing

- [OK] Independent Trellis review: no blocking findings; 8 documents, 53 local links, 21 fields, 11 categories and CSV/JSON examples verified.
- [OK] Read-only audit:2251 groups,833 tagged,54 missing-max,3 reversed,2194 salary-eligible; all three source hashes unchanged.

### Status

[OK] **Completed**

### Next Steps

- Converge page and interaction scope, API and MongoDB design, development toolchain and delivery workflow before application implementation.


## Session 2: Complete data preparation and lock system architecture
<!-- trellis-session: v=2 fp=6210cd04a82bd99a -->

**Date**: 2026-10-18
**Task**: Complete data preparation and lock system architecture
**Branch**: `main`

### Summary

Completed data cleaning, 19-column grouping, category adjudication, moved scripts to temp, verified AC-1~AC-8, initialized Git, and completed architecture design grilling for the multi-page analytics system.

### Git Commits

| Hash | Message |
|------|---------|
| `aa28119` | feat(data): complete data preparation, grouping, dual classification and contract verification |

### Status

[OK] **Completed**


## Session 3: Implement backend, MongoDB seeding and async aggregation APIs
<!-- trellis-session: v=2 fp=ba6738be203c2f15 -->

**Date**: 2026-10-18
**Task**: Implement backend, MongoDB seeding and async aggregation APIs
**Branch**: `main`

### Summary

Completed backend environment setup, docker-compose.yml for MongoDB, seed.py with 4 compound indexes, Motor async repository, 6 core aggregation endpoints, and automated test suite verifying AC-1~AC-4.

### Git Commits

| Hash | Message |
|------|---------|
| `58a30d9` | feat(backend): implement docker compose, mongodb seeding, and async aggregation apis |

### Status

[OK] **Completed**


## Session 4: Scaffold frontend Vite multi-page analytics platform and update AGENTS.md
<!-- trellis-session: v=2 fp=8b5786dae0b971ca -->

**Date**: 2026-10-18
**Task**: Scaffold frontend Vite multi-page analytics platform and update AGENTS.md
**Branch**: `main`

### Summary

Completed frontend Vite Vue 3 TypeScript project with Element Plus, Apache ECharts, Pinia useFilterStore synced with URL query, 4 core views (Overview, Salary, Skills, Jobs), JobDetailDrawer, verified AC-1~AC-5, updated AGENTS.md and specs, and archived system implementation tasks.

### Git Commits

| Hash | Message |
|------|---------|
| `a445b34` | feat(frontend): scaffold vite vue3 multi-page analytics platform with global slicer and echarts |

### Status

[OK] **Completed**


## Session 5: Refactor backend repository with native Motor MongoDB aggregation pipelines
<!-- trellis-session: v=2 fp=81f9bbc4867e66d2 -->

**Date**: 2026-10-18
**Task**: Refactor backend repository with native Motor MongoDB aggregation pipelines
**Branch**: `main`

### Summary

Refactored repository.py to implement native MongoDB aggregation pipelines with , +, , and index-accelerated queries, verified with 20 automated tests passing, and archived task.

### Git Commits

| Hash | Message |
|------|---------|
| `5d0a445` | feat(backend): refactor repository with native Motor MongoDB aggregation pipelines |

### Status

[OK] **Completed**


## Session 6: Archive bootstrap guidelines task and finalize baseline state
<!-- trellis-session: v=2 fp=1a4a9c7badad0bb2 -->

**Date**: 2026-10-18
**Task**: Archive bootstrap guidelines task and finalize baseline state
**Branch**: `main`

### Summary

Archived remaining 00-bootstrap-guidelines task after populating frontend and backend specs. All active tasks across the repository are now clean and archived.

### Git Commits

| Hash | Message |
|------|---------|
| `5d0a445` | feat(backend): refactor repository with native Motor MongoDB aggregation pipelines |
| `2165e3f` | fix(backend): bootstrap sys.path in main.py for robust root-level uvicorn execution |

### Status

[OK] **Completed**


## Session 7: JobInsight 功能首版规划与跨 agent 交接
<!-- trellis-session: v=2 fp=0477c82bf41d190d -->

**Date**: 2026-10-20
**Task**: JobInsight 功能首版规划与跨 agent 交接
**Branch**: `main`

### Summary

用户认可条件选岗、本地候选清单、岗位对比和辅助技能标签核对；指定本轮只产出文档，代码由其他 agent 编写。任务维持 planning。

### Main Changes

- 完成 .trellis/tasks/10-20-frontend-crawl-demo/ 下 prd.md、design.md、implement.md、handoff.md 和 verification.md；配置 6 条实现与 7 条检查上下文。

### Git Commits

(No commits - planning session)

### Testing

- [OK] 真实 JSON 数据覆盖审计已记录；本会话 API 离线真实样本测试 12 passed；Trellis 上下文校验与文档完整性检查通过。未做 MongoDB、浏览器或新功能验收。

### Status

[OK] **Completed**

### Next Steps

- 接手 agent 读取 .trellis/tasks/10-20-frontend-crawl-demo/handoff.md；最终方案经后续审阅批准后才运行 task.py start，按 AC01–AC14 实施验证。采集延后单独推进。


## Session 8: Implement JobInsight workbench, shortlist, compare and skill check
<!-- trellis-session: v=2 fp=4aa7fc2589907f2e -->

**Date**: 2026-10-20
**Task**: Implement JobInsight workbench, shortlist, compare and skill check
**Branch**: `main`

### Summary

Completed end-to-end implementation of job candidate workflow: workbench landing page, shortlist with batch loading, side-by-side job comparison, objective skill tag checking, responsive layouts, 42 passing unit tests, and production build verification.

### Git Commits

| Hash | Message |
|------|---------|
| `6a24a97` | feat(frontend): implement workbench, shortlist, job comparison and skill check |
| `70f4532` | docs(spec): document workspace state store guidelines in frontend spec |

### Status

[OK] **Completed**


## Session 9: 招聘系统 NoSQL 数据层复评与研究交接
<!-- trellis-session: v=2 fp=87b7e5f519936662 -->

**Date**: 2026-10-20
**Task**: 招聘系统 NoSQL 数据层复评与研究交接
**Branch**: `main`

### Summary

保留招聘主题和既有应用功能；现有业务脚本弃用。完成文档复评，MongoDB 文档适配可验证，当前固定小样本性能优势尚未证明；MySQL 关系与 JSON 均作公平对照。

### Main Changes

- 创建 .trellis/tasks/10-20-nosql-data-layer-review，完成需求、选型评估、候选设计、反证基准计划、后续实施门槛与 handoff。配置 7 条实现和 8 条检查上下文。只改文档，保持 planning。

### Git Commits

(No commits - planning session)

### Testing

- [OK] 只读审计输入哈希及岗位/来源成员/技能结构；任务上下文与文档完整性检查通过。没有运行旧业务脚本、数据库实验或产品测试，未报告任何数据库胜出成绩。

### Status

[OK] **Completed**

### Next Steps

- 接手 agent 先读 .trellis/tasks/10-20-nosql-data-layer-review/handoff.md。经用户审阅后再明确批准隔离验证；不直接迁移生产、不恢复旧 seed、不迁移浏览器收藏。


## Session 10: 归档 NoSQL 复评，关闭实施交接
<!-- trellis-session: v=2 fp=52e4627a3297956b -->

**Date**: 2026-10-20
**Task**: 归档 NoSQL 复评，关闭实施交接
**Branch**: `main`

### Summary

用户要求归档。评估结束：当前数据未证明 MongoDB 明显优于 MySQL。招聘主题和现有应用功能保留，没有获批的新改造或后续验证交接。

### Main Changes

- 归档 nosql-data-layer-review，新增 closure.md 并为历史 handoff、design、implement、benchmark 标明不作为执行指令；关闭 handoff_active，修正归档后的上下文引用。

### Git Commits

(No commits - planning session)

### Testing

- [OK] 确认任务已移至 archive/2026-10，状态 completed，活动任务指针已清除；未改产品代码、未操作数据库或旧业务脚本。

### Status

[OK] **Completed**

### Next Steps

- 无待执行交接；如将来提出新数据层需求，另行评估，不自动接续归档候选。
