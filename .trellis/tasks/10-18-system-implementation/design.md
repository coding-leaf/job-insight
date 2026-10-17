# 全栈多页面数据分析与检索系统设计方案 (Parent Task Design)

## 1. 系统整体拓扑架构

```text
               +-------------------------------------------------------------+
               |                浏览器客户端 (Vue 3 + TS SPA)                 |
               |  - 常驻顶栏 (路由导航)                                       |
               |  - 常驻次顶栏 (全局切片器: Pinia Store <-> URL Query 同步)  |
               |  - 页面路由: /overview | /salary | /skills | /jobs          |
               +------------------------------+------------------------------+
                                              | HTTP REST API (/api/v1/*)
                                              v
               +-------------------------------------------------------------+
               |                 FastAPI 异步后端服务 (ASGI)                  |
               |  - 全局统一响应包装中间件 / 异常拦截器 ({ code, message, data}) |
               |  - 共享 Query 切片依赖注入 (category, province, education)  |
               |  - 路由模块: meta, stats, jobs                              |
               +------------------------------+------------------------------+
                                              | Motor 异步管道调用 (Non-blocking)
                                              v
               +-------------------------------------------------------------+
               |                  MongoDB 7.0 (Docker 容器)                   |
               |  - 数据库: job_insight, 集合: jobs (2,251 组规范化文档)      |
               |  - 只读复合索引:                                             |
               |      * [("job_category", 1), ("province", 1)]               |
               |      * [("salary_eligible_for_midpoint", 1), ("category", 1)]|
               |      * [("education_min_code", 1)]                          |
               |      * [("skills.skill_name", 1)]                           |
               +-------------------------------------------------------------+
```

## 2. API 接口契约定义

统一响应包裹结构：
```json
{
  "code": 200,
  "message": "success",
  "data": ...
}
```

### 核心端点规范：
1. `GET /api/v1/meta/options`：
   返回候选切片字典：11 类别白名单、31 省级行政区列表、学历标准层级。
2. `GET /api/v1/overview`：
   宏观概览数据：全量样本 2251、闭区间有效薪资样本 2194、有技能标注样本 833、完全重复合并组 305；全行业总体中位数薪资；各类别岗位占比结构。
3. `GET /api/v1/stats/salary-by-category?province=...&education=...`：
   各技术类别中位数薪资排行，附带 P25、P75 四分位及样本数 N；对于 $N < 5$ 的类别打上 `is_low_sample: true` 或从榜单剔除。
4. `GET /api/v1/stats/salary-by-region?category=...&education=...`：
   各省份薪资中位数与岗位量梯队分布。
5. `GET /api/v1/stats/skills-top?category=...&province=...&education=...&limit=20`：
   Top 技能频次排行，返回：`skill_name`、`count`、`ratio_annotated` ($count / 833$)、`ratio_total` ($count / 2251$)。
6. `GET /api/v1/jobs?category=...&province=...&education=...&keyword=...&page=1&page_size=20`：
   多条件联合分页检索，返回总记录数与列表；每条记录包含 `id`, `source_ids`, `title`, `company`, `company_size`, `company_type`, `province`, `city`, `salary_display`, `salary_midpoint`, `education_requirement`, `skills` (含 `provenance`)。

## 3. 前端状态与跨页面切片连续性设计

- **Pinia `useFilterStore`**：
  - 状态：`category`, `province`, `education`;
  - 动作：`setFilters(newFilters)`, `resetFilters()`;
  - 双向同步：监听路由变化读取 URL Query 初始化 Store；切片器值改变时调用 `router.replace({ query: { ... } })`；
- **页面视图结构**：
  - `views/OverviewView.vue`
  - `views/SalaryView.vue`
  - `views/SkillsView.vue`
  - `views/JobsView.vue`
- **公共组件**：
  - `components/GlobalHeader.vue`：顶栏导航
  - `components/GlobalSlicer.vue`：常驻切片次顶栏
  - `components/JobDetailDrawer.vue`：岗位详情与溯源抽屉
