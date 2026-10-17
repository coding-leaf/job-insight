# 前端Vite多页面工程搭建与全局切片分析大盘技术设计 (Design)

## 1. 目录结构与架构分层

贯彻“代码为准则、架构应复用、方法要深函数、KISS 准则”：

```text
frontend/
├── src/
│   ├── api/                      # 统一请求层 (架构复用)
│   │   ├── client.ts             # Axios 实例、统一解包与错误提示 (ElMessage)
│   │   ├── meta.ts               # GET /api/v1/meta/options
│   │   ├── overview.ts           # GET /api/v1/overview
│   │   ├── stats.ts              # GET /api/v1/stats/*
│   │   └── jobs.ts               # GET /api/v1/jobs & /api/v1/jobs/:id
│   ├── composables/              # 深度可复用逻辑 (深函数)
│   │   └── useECharts.ts         # 统一图表挂载、resize 监听与销毁清理
│   ├── stores/                   # 全局状态管理
│   │   └── filter.ts             # useFilterStore (全局切片参数 + URL 同步)
│   ├── types/                    # 严谨 TypeScript 契约 (代码为准则)
│   │   ├── api.ts                # ResponseModel<T>
│   │   └── job.ts                # JobGroup, OverviewData, SalaryStats, SkillStat
│   ├── components/               # 复用组件 (深函数，精炼 Props)
│   │   ├── GlobalHeader.vue      # 顶层系统导航栏
│   │   ├── GlobalSlicer.vue      # 常驻全局切片次顶栏
│   │   └── JobDetailDrawer.vue   # 岗位详情与溯源抽屉
│   ├── views/                    # 4 大专业业务页面
│   │   ├── OverviewView.vue      # 宏观综合总览大盘
│   │   ├── SalaryView.vue        # 薪资分布与地域梯队
│   │   ├── SkillsView.vue        # 技术栈与技能图谱
│   │   └── JobsView.vue          # 在招岗位多维检索库
│   ├── router/
│   │   └── index.ts              # 路由配置 (4 大路由 + 重定向)
│   ├── App.vue                   # 根组件 (Header + Slicer + router-view)
│   └── main.ts                   # 应用入口 (Vue, Pinia, Element Plus, Router)
├── index.html                    # 页面入口
├── vite.config.ts                # Vite 配置 (路径别名 @ 与 /api 代理)
├── tsconfig.json                 # TypeScript 严格配置
└── package.json                  # 依赖清单
```

## 2. 状态管理与切片数据流 (Filter Synchronization)

- **Pinia Store (`useFilterStore`)**：
  - 核心状态：`category: string | undefined`, `province: string | undefined`, `education: string | undefined`；
  - 动作：`updateFilter(key, value)`, `resetFilters()`, `syncFromQuery(query)`；
  - 双向绑定：
    - 当路由变化时（`router.afterEach`），调用 `filterStore.syncFromQuery(to.query)`；
    - 当用户在 `GlobalSlicer` 变更选项时，调用 `router.replace({ query: cleanQuery })`；
- **业务页面响应机制**：
  - 各 View 监听 `filterStore` 的变化（`watch(() => filterStore.activeParams, () => loadData())`），自动携带最新的切片参数刷新各自页面的 ECharts 图表与列表。

## 3. 核心组件“深函数”设计 (Deep Components)

1. **`useECharts(domRef)`**：
   - 入参：图表 DOM 元素的 `ref`；
   - 内部封装：`echarts.init()`、响应式 `ResizeObserver` 自动适应窗口缩放、组件卸载时 `dispose()`；
   - 对外暴露：极简的 `setOption(options)` 方法与 `chartInstance`。调用者只需关注 ECharts 配置项，无需手写重复的监听与销毁代码。
2. **`<JobDetailDrawer v-model:visible="visible" :job-id="selectedId" />`**：
   - 外部调用只需传入 `visible` 和 `job-id`；
   - 内部封装：异步加载单个岗位详情（`/api/v1/jobs/{id}`）、骨架屏加载、19 列未修饰值展示、技能 Provenance 标签化呈现。
