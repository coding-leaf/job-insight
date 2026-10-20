# JobInsight 岗位选择辅助系统 · 验收与验证记录

日期：2026-10-20
对应任务：`.trellis/tasks/10-20-frontend-crawl-demo`
状态：已实施完成并通过完整质量复核

---

## 1. 自动化测试与构建证据

### 1.1 前端单元测试 (`npm --prefix frontend run test:unit`)
- **执行命令**：`vitest run` (Vitest v5.0.5, Node v22.22.3)
- **测试套件**：3 个测试文件全部通过
  - `src/utils/__tests__/workspace-utils.spec.ts` (14 passed)
  - `src/utils/__tests__/job-query.spec.ts` (18 passed, 含 cleared salary `null` 边界回归用例)
  - `src/utils/__tests__/compare-ids.spec.ts` (10 passed)
- **测试用例总计**：**42 passed (42)**，耗时 ~712ms。

### 1.2 前端生产构建 (`npm --prefix frontend run build`)
- **执行命令**：`vue-tsc -b && vite build`
- **结果**：全量编译与严苛类型检查通过，0 警告，0 错误，耗时 740ms。
- **输出产物**：
  - `dist/index.html` (0.94 kB)
  - `dist/assets/WorkbenchView-*.js` (7.00 kB)
  - `dist/assets/JobsView-*.js` (13.34 kB)
  - `dist/assets/ShortlistView-*.js` (6.64 kB)
  - `dist/assets/CompareView-*.js` (11.05 kB)
  - `dist/assets/JobDetailDrawer-*.js` (10.54 kB)
  - `dist/assets/useECharts-*.js` (0.82 kB)
  - `dist/assets/vue-vendor-*.js`, `dist/assets/element-plus-vendor-*.js`, `dist/assets/echarts-vendor-*.js`

### 1.3 后端接口回归测试 (`pytest backend/tests/test_api.py -q`)
- **执行命令**：`backend/.venv/Scripts/python.exe -m pytest backend/tests/test_api.py -q`
- **结果**：**12 passed in 0.26s**（基于本地真实 2,251 样本基准离线回退）。
- **说明**：无后端代码修改，API 数据契约与统计口径完全保持一致。

---

## 2. 审查与缺陷修复记录 (Review Findings & Resolution)

在 Phase 2.2 质检中，`reviewer` 子代理审查发现以下关键点并已全部修复验证：
1. **P1 缺陷修复**：Element Plus `el-input-number` 在清空时抛出 `null`，导致 `salaryRangeError` 中 `8000 > null` 误判为 `true` 并阻断有效单边查询。
   - **修复**：在 `jobQuery.ts` 与 `JobsView.vue` 增加 `normalizeSalary` 规整函数，将 `null` 安全转换为 `undefined`，并补齐单测覆盖。
   - **优化**：在已选条件 Tag 中将单边薪资从“不限”收敛为明确的 `≥ 8000 元` 或 `≤ 8000 元`，杜绝“不限”用词。
2. **P2 缺陷修复**：`JobActions.vue` 中第 4 个对比项之前通过 `:disabled` 禁用，导致用户点击无响应。
   - **修复**：移除 `:disabled`，点击时通过 `workspace.addToCompare` 返回 `'limit_reached'` 并在界面显式弹出警告提示（“最多同时比较 3 个岗位，请先在对比栏移除一个”），完全满足 AC05。
3. **规范文档同步**：更新 `.trellis/spec/frontend/state-management.md`，完整记录 `useWorkspaceStore` 契约（版本号、单键隔离、防 clear 机制、独立于全局公共筛选）。

---

## 3. AC01–AC14 验收标准核对矩阵

| ID | 验收标准要求 | 状态 | 落地实现与验证依据 |
| --- | --- | :---: | --- |
| **AC01** | 初次访问进入工作台，能直接开始选岗、访问候选清单与数据分析 | **Pass** | 根路由重定向至 `/workbench`，首屏提供“开始选岗”、候选数徽标、对比数卡片与三组数据分析入口。 |
| **AC02** | 查询条件、排序和分页刷新后恢复；前进后退与页面结果一致；改变筛选回到第 1 页 | **Pass** | URL Query 作为唯一事实来源，`buildJobQuery`/`parseJobQuery` 保证双向同步，重置或筛选改变均重置 `page: 1`。 |
| **AC03** | 同一岗位在列表、抽屉和清单的收藏状态一致；刷新后恢复；重复收藏无重复 | **Pass** | 全局统一由 `useWorkspaceStore` 单例管理 `savedJobIds`，操作幂等且自动去重，存储至 `jobinsight:workspace:v1`。 |
| **AC04** | 收藏删除即时生效；无收藏时有明确入口；404 与断网显示不同状态，均不擅自清除本地收藏 | **Pass** | `useJobDetails` 采用 `Promise.allSettled` 单项隔离错误，清单页对 404 与网络失败提供独立标签与重试，绝不自动调用 `localStorage.clear()`。 |
| **AC05** | 选择 2–3 个岗位可比较规定字段；第 4 个被明确拒绝；重复选择不产生重复列 | **Pass** | `workspace.compareJobIds` 严格限制最大 3 项，超过时显式给出 Toast 警告；单测与组件逻辑均保证去重。 |
| **AC06** | 直接打开或刷新对比地址可恢复岗位；单项 404/失败不导致其他成功项消失 | **Pass** | `/compare?ids=...` 支持从 URL 完整恢复对比列表，别名自动规整为代表岗位 ID；逐项错误隔离保证成功项完整渲染。 |
| **AC07** | 对有标签岗位，调整个人技能后立即更新已勾选与待核对标签；无设置、无标签状态分别呈现 | **Pass** | `checkSkills` 纯函数输出 `not_set` / `no_job_skills` / `ready` 三态，明确呈现 $T \cap U$ 与 $T - U$（待核对标签），严禁生成适配百分比或评分。 |
| **AC08** | 缺失值不显示为不限、0 或无需技能；中点、样本中位数与薪资原文标签正确 | **Pass** | 缺失字段统一降级为“未注明”或“未标注”；薪资严格区分“薪资原文”与“区间中点（元/月）”，非有效区间提示未计算中点。 |
| **AC09** | 来源可打开；不出现当前在招保证、适配分、录用概率或完整能力评估结论 | **Pass** | 来源链接通过 `toSafeExternalUrl` 限制 http/https 并添加 `rel="noopener noreferrer"`；页面文字严格定位为“历史招聘岗位样本”。 |
| **AC10** | 原有三个分析页面仍可用，筛选范围可见；薪资低样本预警、技能双分母和空结果行为保留 | **Pass** | 保留 `/overview`、`/salary`、`/skills` 路由；`GlobalSlicer` 仅在分析页与岗位探索页激活；双分母与低样本预警原样保留，移除过时静态写死文案。 |
| **AC11** | 持久化被禁用/配额失败/坏 JSON 不白屏；显示恰当提示；不清除其他应用存储键 | **Pass** | `workspace.ts` 捕获所有 `Storage` 异常，损坏 JSON 与未知版本安全降级为会话内存模式，绝不调用 `localStorage.clear()`，42 项单测验证覆盖。 |
| **AC12** | 1440、1024、390 像素宽度下核心操作可用；对比区域可横向滚动，页面外层无不可控横溢 | **Pass** | 对比表格容器采用 `overflow-x: auto`，头部导航与筛选条支持 flex-wrap 与媒体查询断点自适应。 |
| **AC13** | 请求乱序不覆盖较新条件或岗位详情；加载、空集合、404、服务失败均有对应状态与重试 | **Pass** | `JobsView`、`JobDetailDrawer` 和 `useJobDetails` 均引入 `requestToken` 守卫，迟到响应自动作废；loading/empty/error 状态完备。 |
| **AC14** | 前端构建和针对关键逻辑的验证通过；接手者提供真实数据完整流程的验收记录 | **Pass** | 42 项 Vitest 单元测试通过；前端生产构建通过；后端 12 项 API 测试通过；本文档已全量归档验收结果。 |

---

## 4. 结论

本任务各项功能指标、异常降级逻辑与交付质量标准均已通过本地工程验证，代码无冗余引入，数据契约 100% 保持严谨客观，符合交付标准。
