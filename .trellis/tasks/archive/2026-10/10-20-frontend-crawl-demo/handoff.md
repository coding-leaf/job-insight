# 下一 agent 从这里接手

Active task: .trellis/tasks/10-20-frontend-crawl-demo

## 1. 一分钟理解

用户最终要一个有实际用途的功能性系统。已认可首版核心为：

**条件选岗 → 保存候选 → 对比岗位 → 核对已有技能标签 → 查看来源。**

现有数据和 API 可以支撑上述主体。技能核对只是有限标签辅助，不能发展成完整任职评估。已有 Docker 未开不代表缺少数据。

用户明确要求：本轮规划 agent 只写详细文档和解释，通过 Trellis 交接；具体代码由其他 agent 编写。本轮没有派发代码 agent、修改产品代码、安装依赖、启动 Docker 或采集。

## 2. 状态与批准

- 任务状态：planning。
- 已批准：功能方向、本轮文档与交接工作。
- 最终技术文档：prd.md、design.md、implement.md 已准备供审阅。
- 尚未批准：在本版最终摘要出现后的实施启动；请查看最新用户消息是否已经明确要求“按这份文档实施”。
- 若没有该后续批准，展示本节摘要及关键边界，请用户审阅后再开始；不要重新询问已确认的产品定位和是否创建任务。
- 不要仅为让新窗口识别任务而提前执行 task.py start。

最终审阅摘要：
- 目标：帮助求职学生形成有依据的岗位候选清单和对比结果。
- 范围：工作台、岗位探索、浏览器本地收藏、最多 3 个岗位对比、已有技能标签核对，保留分析页。
- 不含：登录/同步/投递/预测/完整能力评估；爬虫另行推进。
- 验收：刷新和地址恢复、收藏一致、缺失/错误状态正确、技能未知明确、完整用户流程与真实数据验证。
- 默认值：本浏览器保存、岗位学历标签保持精确筛选、比较 2–3 项、不改后端业务 DTO。
- 风险：标签仅覆盖 833/2251；正文仅 1340/2251；无核实的当前在招状态。

## 3. 阅读顺序

1. prd.md：R1–R6 和 AC01–AC14，包含用户决定和边界。
2. research/functional-feasibility.md：实际数据与代码依据。
3. design.md：页面、状态、URL、接口、异常行为的精确定义。
4. implement.md：按依赖顺序实施和验证。
5. implement.jsonl / check.jsonl 引用的项目规范；其中只登记规格/研究，不登记代码文件。

旧 PROJECT_HANDOFF.md 是历史材料，不应据此否认现有前后端已存在。当前 JobItem/Pydantic 契约、接口和仓库实现以可执行代码为准。

## 4. Trellis 如何发现与接续

在仓库根执行：

~~~powershell
python ./.trellis/scripts/get_context.py
python ./.trellis/scripts/task.py list
python ./.trellis/scripts/task.py validate .trellis/tasks/10-20-frontend-crawl-demo
python ./.trellis/scripts/get_context.py --mode phase --step 1.4 --platform codex
~~~

重要：Trellis 的 active task 指针按 session/window 保存。当前会话已经指向本任务，但一个全新 agent 窗口不保证自动继承该指针。任务在非归档列表中可见，开发者仍是 coding-leaf；直接使用本文件首行的任务路径即可定位，无需新建重复任务。

在最终方案得到后续明确批准后，接手者运行：

~~~powershell
python ./.trellis/scripts/task.py start .trellis/tasks/10-20-frontend-crawl-demo
python ./.trellis/scripts/get_context.py --mode phase --step 2.1 --platform codex
~~~

若使用 Trellis 子 agent，每个派发提示第一行使用：

~~~text
Active task: .trellis/tasks/10-20-frontend-crawl-demo
~~~

优先原生上下文注入；没有注入时由子 agent 读取任务三份规划与对应 jsonl 引用。按当前项目规定派发 trellis-implement / trellis-check；不要假设子 agent 看过这段聊天。

## 5. 当前已做与未做的验证

已做：
- 从真实 data/processed/jobs_cleaned_grouped.json 重算字段覆盖率，保存 research/data-capability-audit.json。
- 检查现有列表、详情、统计、筛选、路由和 Axios 数据流。
- 在本会话运行 backend/.venv/Scripts/python.exe -m pytest backend/tests/test_api.py -q：12 passed。
- 规划和上下文文件的完整性检查结果见 verification.md。

未做：
- 新功能代码、前端构建、前端单测、浏览器验收、MongoDB 集成验证。
- 新采集或验证外部来源当前招聘状态。
- 产品提交、部署、归档。

ASGITransport 测试没有走应用 lifespan 的 MongoDB 连接，读取的是本地真实样本；不能将 12 passed 宣称为数据库或浏览器通过。

## 6. 可直接给接手 agent 的提示

~~~text
Active task: .trellis/tasks/10-20-frontend-crawl-demo
请读取 handoff.md、prd.md、design.md、implement.md 和 implement.jsonl，接续本任务。
用户认可的功能方向是：条件选岗、本浏览器候选清单、最多三个岗位对比，技能标签核对作为辅助。
数据已存在，Docker 暂未开启；不得造数据或无条件重新灌库。
先根据最新用户消息核实最终方案审阅批准，再按 Trellis 阶段进入实施。
你不是唯一编辑者，请保留他人改动；按 implement.md 的阶段和 AC01–AC14 交付并留下验证证据。
~~~

## 7. 后续采集事项

原 ../final-homeworkwork Java 爬虫存在，详情见 research/current-state.md。此次没有把它搬入本仓库、运行或改写。若用户再要求采集演示，先建独立关联任务，验证所选来源当下能否访问，限制条数，将输出放进新的本仓库目录。不得使用 --fresh 清空历史目录，不得把新样本直接混入正式基准。
