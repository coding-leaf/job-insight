# 前端Vite多页面工程搭建与全局切片分析大盘实施计划 (Implement)

## 实施步骤与检验点

- [ ] **Step 1: Vite 官方脚手架初始化与依赖安装**
  - 使用 `npm create vite@latest frontend -- --template vue-ts` 初始化前端骨架；
  - 安装核心生产依赖：`element-plus`, `@element-plus/icons-vue`, `echarts`, `pinia`, `vue-router`, `axios`；
  - 安装开发依赖：`@types/node`；
  - 配置 `vite.config.ts`：设置 `@` 路径别名与 `/api` 代理转发至 `http://127.0.0.1:8000`。

- [ ] **Step 2: 基础层与类型契约搭建 (KISS & 架构复用)**
  - 编写 `src/types/api.ts` 与 `src/types/job.ts`，精准映射后端 Pydantic 模型；
  - 编写 `src/api/client.ts`，配置 Axios 基础 URL 与拦截器（自动提取 `response.data.data`，错误时触发 `ElMessage.error`）；
  - 编写 `src/api/meta.ts`, `overview.ts`, `stats.ts`, `jobs.ts`；
  - 编写 `src/composables/useECharts.ts`（深函数封装）。

- [ ] **Step 3: 路由、Pinia Store 与常驻布局搭建**
  - 编写 `src/stores/filter.ts`；
  - 编写 `src/router/index.ts`，配置 `/overview`, `/salary`, `/skills`, `/jobs`；
  - 编写 `src/components/GlobalHeader.vue`；
  - 编写 `src/components/GlobalSlicer.vue`（与 URL Query 同步）；
  - 组装 `src/App.vue`。

- [ ] **Step 4: 四大专业业务页面开发 (100% 对接真实数据)**
  - 实现 `src/views/OverviewView.vue`（KPI 指标卡 + 行业薪资基准 + 类别构成比）；
  - 实现 `src/views/SalaryView.vue`（类别薪资排行中位数条形图 + 31 省份梯度 + 规模对比）；
  - 实现 `src/views/SkillsView.vue`（Top 技能渗透率双分母条形图 + 雷达图）；
  - 实现 `src/views/JobsView.vue` + `src/components/JobDetailDrawer.vue`（多维搜索、分页表格与详情穿透）。

- [ ] **Step 5: 构建验证与质量验收**
  - 运行 `npm run build` 确保 `vue-tsc` 与 Vite 生产构建 0 错误；
  - 验证 AC-1 至 AC-5 全部达成。
