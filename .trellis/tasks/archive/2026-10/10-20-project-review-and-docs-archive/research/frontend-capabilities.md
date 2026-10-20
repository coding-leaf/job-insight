# Research: 前端实际功能与能力边界

- Query: 当前前端真正实现了哪些页面、交互、数据调用与浏览器状态，哪些表述不能用于项目汇报？
- Scope: internal；仅审查 `frontend/` 源码、测试定义与相关 Trellis 规范，不涉及数据库实现或现有文档内容审计。
- Date: 2026-10-20（Asia/Shanghai）
- Method: 只读源码检查；未启动服务、运行测试、安装依赖或访问数据库。

## Findings

### 1. 页面与已实现交互

路由实际注册 **7 个业务页面**，根路径与未知路径均跳转工作台；页面组件采用动态 import，使用 HTML5 history（`frontend/src/router/index.ts:4`、`:58`）。旧指引中的“4 页”不能作为当前功能数量。

| 页面 | 实际实现 | 关键证据 |
| --- | --- | --- |
| `/workbench` 求职工作台 | 类别、省份、学历快捷条件带入岗位探索；显示本浏览器候选数量和当前对比数量；设置个人技能标签；进入概况、薪资、技能分析。这里的两个计数来自用户状态，不是市场指标。 | `frontend/src/views/WorkbenchView.vue:36`、`:46`、`:59`、`:71`；个人标签逻辑 `frontend/src/components/SkillPicker.vue:29` |
| `/jobs` 岗位探索 | 组合类别、省份、学历、关键词、月薪上下界与是否有技能标签；条件 chips、单项移除和清空；按 ID、发布时间、最低/最高月薪、薪资中点升降序；10/20/50/100 条分页；行点击和按钮打开详情；收藏和加入对比。关键词 UI 标注匹配标题、企业、正文或技能标签，实际检索语义仍应结合后端核对。 | `frontend/src/views/JobsView.vue:28`、`:53`、`:86`、`:100`、`:137`、`:179`、`:213`、`:500`、`:517`；排序白名单 `frontend/src/utils/jobQuery.ts:4` |
| `/shortlist` 候选清单 | 由本地收藏 ID 组成，最近加入项排前；固定每页 10 条，仅拉取当前页岗位详情；查看详情、来源和技能；移除收藏或加入对比；单条/批量重试失败项。404 保留 ID，提示“当前数据中未找到”，不会自动认定下架或删除收藏。 | `frontend/src/views/ShortlistView.vue:11`、`:22`、`:40`、`:48`、`:122`；插入顺序 `frontend/src/stores/workspace.ts:57` |
| `/compare` 岗位对比 | 最多 3 列事实字段，包括企业、地点、薪资原文/中点、学历、经验、专业、技能、发布时间与来源；支持从候选添加、替换、移除；详情解析到代表岗位 ID 后去重；逐项失败隔离和重试；个人技能标签核对；对比 ID 写入 URL 可分享与刷新恢复。 | `frontend/src/views/CompareView.vue:36`、`:43`、`:78`、`:97`、`:113`、`:164`、`:171`、`:181`；上限 `frontend/src/types/workspace.ts:25` |
| `/overview` 样本概况 | API 驱动的岗位总量、有效薪资组数、技能标注组数、重复合并组数、薪资中点中位数、类别构成环图；显示筛选范围；带全局条件跳转其他分析/探索页。前端文案“多源重复合并组”本身不能证明当前存在多个招聘平台。 | `frontend/src/views/OverviewView.vue:34`、`:49`、`:135`、`:166`、`:238`、`:258` |
| `/salary` 薪资与地域 | 并行请求按类别、按省份的薪资统计；横向柱图与两张透视表；展示中位数、P25/P75、总样本数、有效薪资样本数和服务端返回的低样本/位次标记；省份图取有中位数且非“未注明”的前 15 项。统计值与位次不是浏览器重新计算。 | `frontend/src/views/SalaryView.vue:32`、`:55`、`:155`、`:302`、`:377`；契约 `frontend/src/types/job.ts:66` |
| `/skills` 技能标签 | 请求 Top 20，横向双系列柱图并列显示 K/L 和 K/N；雷达图取前 8 项；表格列频次、两个比例、标注覆盖率；“搜索该标签”携带当前全局条件跳转关键词搜索，**不是精确技能筛选**。 | `frontend/src/views/SkillsView.vue:39`、`:60`、`:155`、`:239`、`:253`、`:379` |

共用详情抽屉保留岗位原文、缺失状态、月薪边界/中点及排除原因、技能名称与每条来源字段/证据、合并来源 ID、原始招聘链接（`frontend/src/components/JobDetailDrawer.vue:49`、`:131`、`:206`、`:247`、`:299`）。来源只允许 HTTP(S)，新窗口采用 `noopener noreferrer`（`frontend/src/utils/jobDisplay.ts:9`）。打开来源不等于确认招聘仍有效。

全局底部对比栏显示最多 3 项，支持移除/清空；至少 2 项时允许按钮进入并排对比（`frontend/src/components/CompareTray.vue:13`、`:74`）。直接打开只有 0/1 项的 `/compare` 会给出继续选择提示。

### 2. “技能匹配”的准确含义

- `checkSkills` 计算岗位既有标签集合 T 与用户自选集合 U 的 **交集 T∩U** 和 **差集 T−U**；只按清理首尾空白后的标签名称进行精确相等比较，岗位重复标签只计一次（`frontend/src/utils/skillCheck.ts:16`、`:24`、`:35`）。
- `knownSkills = null` 表示未设置，`[]` 表示用户明确一个标签都未选；岗位无标签返回不可核对状态。这些状态不能被解释为无能力或岗位不需要技能（`frontend/src/utils/skillCheck.ts:20`、`:31`；`frontend/src/types/workspace.ts:5`）。
- 没有匹配分、百分比、熟练度推断、岗位必需程度、推荐排名或录用概率。对比页明确声明这一边界（`frontend/src/views/CompareView.vue:224`、`:359`）。
- `SkillPicker` 通过全量条件下的 `/stats/skills-top?limit=100` 获取可选名称，并保留之前选中的名称；这只是当前样本标签候选集，不应称作完整行业技能词库。选择只写本浏览器，不上传后端（`frontend/src/components/SkillPicker.vue:29`、`:46`、`:81`）。

### 3. 浏览器状态与 URL 分工

| 状态 | 保存位置及行为 | 证据 |
| --- | --- | --- |
| 候选 ID、个人技能 | `localStorage` 键 `jobinsight:workspace:v1`，载荷 version=1；只存用户动作状态，不存岗位快照；更换浏览器/设备不会同步。 | `frontend/src/utils/workspace.ts:3`、`:80`、`:105`、`:116`；`frontend/src/stores/workspace.ts:18` |
| 对比 ID | Pinia 内存；`/compare?ids=a&ids=b` 为可恢复/分享入口，读单值或重复参数、去空、去重、最多 3 项；个人技能与收藏不进入对比链接。 | `frontend/src/stores/workspace.ts:22`、`:78`、`:98`；`frontend/src/utils/compareIds.ts:9`；`frontend/src/views/CompareView.vue:36`、`:43` |
| 分析切片 | Pinia `useFilterStore` 存类别、省份、学历，路由 query 同步；全局切片仅出现在 jobs/overview/salary/skills；进入工作台、候选、对比会重置切片，避免隐性过滤。 | `frontend/src/stores/filter.ts:6`、`:39`；`frontend/src/router/index.ts:62`；`frontend/src/components/GlobalSlicer.vue:47`、`:99` |
| 岗位探索全部已应用条件 | URL 为事实来源，包含关键词、薪资、是否有标签、页码/页大小/排序；控件保有提交前 draft；使用 `router.replace`，默认参数省略，非法 query 值退回默认。 | `frontend/src/views/JobsView.vue:28`、`:42`、`:127`、`:234`；`frontend/src/utils/jobQuery.ts:66`、`:92` |

正常浏览器保存可刷新恢复；存储不可用、未知版本或写入失败时保留会话内操作并告警；未知版本载荷不覆盖，损坏载荷初次只读不清空、用户主动修改时可重建自身键。不会调用 `localStorage.clear()` 清除其他数据（`frontend/src/stores/workspace.ts:6`、`:24`、`:30`；`frontend/src/utils/workspace.ts:38`、`:105`、`:116`）。取消收藏与移除对比互不影响（`frontend/src/stores/workspace.ts:61`、`:86`）。

导航在四个可切片页面之间携带三个全局条件，局部关键词等不会成为所有页面的全局条件（`frontend/src/components/GlobalHeader.vue:21`、`:37`、`:43`）。使用 `replace` 不会为每次筛选额外创建历史条目，不能声称每次筛选都能逐步后退。

### 4. API 与前端架构

```text
Vue 路由/页面 + Element Plus
  ├─ Pinia 筛选/工作区状态 ─ URL query、localStorage
  ├─ 页面/详情组件 → API 函数 → Axios → /api/v1 → 后端
  └─ API 返回统计值 → useECharts → ECharts 图表
```

- Axios 设置 `/api/v1` 与 15 秒超时，校验响应包装体 `code === 200`，统一错误消息；支持 `silentError` 由调用者处理局部错误（`frontend/src/api/client.ts:12`、`:20`）。**拦截器返回完整 Axios response，具体端点函数读取 `res.data.data`；不应写成“拦截器统一解包成 data”**（`frontend/src/api/client.ts:29`；`frontend/src/api/jobs.ts:7`）。
- 前端实际调用的路径均为 GET：`/meta/options`、`/overview`、`/stats/salary-by-category`、`/stats/salary-by-region`、`/stats/skills-top`、`/jobs`、`/jobs/{id}`（`frontend/src/api/meta.ts:6`；`overview.ts:6`；`stats.ts:13`、`:22`、`:31`；`jobs.ts:6`、`:19`）。候选、对比、技能配置没有 POST/PUT/PATCH/DELETE API。
- 候选及对比复用 `useJobDetails` 逐 ID 并行详情请求，各项有 loading/success/not_found/error，已成功项不重复请求，新批次 token 阻止旧响应覆盖（`frontend/src/composables/useJobDetails.ts:25`、`:41`、`:51`、`:71`、`:91`）。这不是独立批量详情后端接口；底部栏也有自己的详情加载实例。
- 图表共用 `useECharts`：挂载初始化、ResizeObserver/窗口 resize、clear、卸载 dispose（`frontend/src/composables/useECharts.ts:5`、`:41`、`:45`、`:56`）。
- Vite 开发端口 5173，`/api` 代理到本机 8000；生产构建手动拆分 ECharts、Element Plus 和 Vue 相关 vendor 块（`frontend/vite.config.ts:12`、`:21`）。只据此不能宣称已具备生产反向代理/SPA history 回退配置或已部署上线。

### 5. 空结果、失败与尚需注意的限制

- 岗位探索成功且 0 条显示明确空态及清空条件按钮；失败显示可重试 alert；已有成功结果发生失败时保留旧结果并警告可能不是最新；详情抽屉有 404/其他错误及重试，切换 ID 清理上一条并用 token 防串台（`frontend/src/views/JobsView.vue:100`、`:362`、`:512`；`frontend/src/components/JobDetailDrawer.vue:35`、`:49`、`:87`）。
- 候选/对比对单条失败隔离，404 不等同招聘下架；失败不会删除本地选择（`frontend/src/views/ShortlistView.vue:122`、`:136`；`frontend/src/views/CompareView.vue:259`、`:320`）。
- 概况无类别数据清环图，薪资无分组清图、无有效省份清图，技能无项清柱图且少于 3 项清雷达（`frontend/src/views/OverviewView.vue:58`；`SalaryView.vue:58`、`:164`；`SkillsView.vue:64`、`:159`）。
- **三张分析页的错误恢复弱于岗位探索**：catch 仅 console，统一 Axios toast 报错；页面无独立失败重试状态，也未在 catch 清除旧图/旧数据。三个页面无请求 token，快速切片后的异步响应顺序未被保护。不能笼统汇报“所有页面已完善异常和并发处理”（`frontend/src/views/OverviewView.vue:34`；`SalaryView.vue:32`；`SkillsView.vue:39`）。此为源码边界判断，未进行浏览器复现。
- 技能页在 API 未成功/覆盖率为 null 时部分 KPI 默认显示 0/0.0%，可能与真实空样本混淆；薪资类别图对 null median 采用 0 高度占位，但 tooltip/label/table 仍说明暂无有效中点（`frontend/src/views/SkillsView.vue:270`、`:281`；`frontend/src/views/SalaryView.vue:66`、`:141`）。因此不能说 UI 的每个 0 都是已获取的统计值。
- 全局切片有静态默认类别、省份、学历选项，正常情况以 metadata API 覆盖，API 失败则仍可显示默认项（`frontend/src/components/GlobalSlicer.vue:13`、`:27`、`:37`、`:51`、`:81`）。不要声称“前端所有下拉项都完全来自实时数据”；工作台另用空选项加失败/重试提示。
- 手工提交矛盾薪资区间会被阻止；直接 URL 的矛盾区间会显示警告，API 参数生成函数会省略该区间并继续其他条件查询，**不是完全停止所有请求**（`frontend/src/views/JobsView.vue:137`、`:225`；`frontend/src/utils/jobQuery.ts:114`、`:136`；`frontend/src/utils/__tests__/job-query.spec.ts:121`）。
- 源码检索未发现导出/下载 CSV、Excel、PDF、图像或复制链接按钮；对比链接可通过浏览器地址分享。未发现前端账号登录、服务端收藏、跨设备同步、投递跟踪、简历解析、智能推荐/预测或实时招聘状态验证实现。它是面向既有招聘样本的分析与选岗辅助前端。

### 6. 依赖与已有测试定义

`frontend/package.json:12` 声明 Vue `^3.5.42`、Vue Router `^5.4.0`、Pinia `^4.1.0`、Element Plus `^2.14.7`、ECharts `^6.1.0`、Axios `^1.20.0`；开发声明 TypeScript `~6.0.2`、Vite `^8.3.0`、Vitest `^5.0.5`、vue-tsc `^3.3.11`（`:21`）。这是**仓库 manifest 的版本范围**，本研究未验证 lockfile 或实际安装版本，也不声称为当前最新版本。

构建脚本先 `vue-tsc -b` 再 `vite build`，单测脚本 `vitest run`（`frontend/package.json:6`）。仓库发现 3 个测试文件、静态计数共 **42 个 `it` 用例定义**：

| 测试文件 | 定义数与覆盖范围 |
| --- | --- |
| `frontend/src/utils/__tests__/job-query.spec.ts:25` | 12：URL 默认值、布尔解析、非法值/重复参数、排序白名单、query 往返、薪资矛盾及 null 控件值、请求参数、缺失显示、安全来源 URL。 |
| `frontend/src/utils/__tests__/compare-ids.spec.ts:4` | 4：空/单个/重复 ids、去空去重、上限 3。 |
| `frontend/src/utils/__tests__/workspace-utils.spec.ts:55` | 26：载荷恢复、null 与 []、损坏/未知版本、存储不可用/写失败、收藏恢复/移除、对比去重/上限/不持久化、收藏对比解耦，以及不评分的技能交集/差集行为。关键边界见 `:187`、`:197`、`:217`、`:226`、`:265`、`:279`。 |

这些是工具函数/Pinia 行为测试定义；未发现组件或浏览器 E2E 测试。**本研究没有执行测试，42 不是通过数，也不是整体 UI 的可用性证明。**

## Files Found

- `frontend/src/router/index.ts` — 7 页路由、根重定向、页面标题与筛选状态边界。
- `frontend/src/views/{Workbench,Jobs,Shortlist,Compare,Overview,Salary,Skills}View.vue` — 对应上表的实际页面及交互。
- `frontend/src/components/{GlobalHeader,GlobalSlicer,CompareTray,JobActions,JobDetailDrawer,SkillPicker}.vue` — 导航、筛选、对比栏、收藏/对比、详情及个人技能设置。
- `frontend/src/stores/{filter,workspace}.ts` — 全局切片与本浏览器用户状态。
- `frontend/src/utils/{jobQuery,compareIds,workspace,skillCheck,jobDisplay}.ts` — URL 编解码、持久化、标签集合核对及缺失/来源显示。
- `frontend/src/composables/{useECharts,useJobDetails}.ts` — 图表资源生命周期和逐项详情加载。
- `frontend/src/api/{client,meta,overview,stats,jobs}.ts` — GET 调用及统一 Axios 错误约定。
- `frontend/src/types/{api,job,workspace}.ts` — 响应、岗位/统计、用户状态契约。
- `frontend/src/utils/__tests__/*.spec.ts` — 3 个测试文件，42 个静态用例定义。
- `frontend/package.json`、`frontend/vite.config.ts` — 声明依赖、构建测试命令、开发代理和产物分块。

## Related Specs

- `.trellis/workflow.md` — 本任务研究持久化要求及只读调研所处阶段。
- `.trellis/spec/frontend/index.md` — 真实数据、薪资有效样本数、技能双分母、缺失状态规范。
- `.trellis/spec/frontend/state-management.md` — Pinia/URL/workspace 分工、对比最多 3 项、浏览器持久化与空图清理。
- `.trellis/spec/frontend/type-safety.md`、`quality-guidelines.md` — 本次读取时大部分仍为待填模板，不能当成完整落实的质量制度。
- `.trellis/spec/guides/index.md` — 跨层/复用思考入口；本研究未修改规范。

## External References

无。此文件只陈述当前仓库实现和 manifest 声明，不评价外部库最新状态；外部架构/数据库选型由主会话或其他研究负责。

## Caveats / Not Found

- 所有“已实现”指源码中具备相应路径和逻辑，未做当前环境运行验证；接口实际返回与数据库模式由后端研究补证。
- 没有检查 docs/ 的文档时效，也没有读取数据库或写入应用文件；不根据前端文案推导多源采集、实时状态或数据库独有能力。
- 日期为本次审查时间，不代表样本采集时间、招聘有效期或部署完成时间。
