# NoSQL 数据层复评 · 接手入口

> 已关闭：用户于 2026-10-20 要求归档。没有待实施交接；下文仅保留历史记录，不是执行入口或授权。当前结论以 closure.md 为准。

Historical task: .trellis/tasks/10-20-nosql-data-layer-review

## 1. 用户已决定的事

- 招聘主题和已经实现的功能保留。不要改题，不要为数据库重做工作台/选岗/收藏/对比/技能页面。
- 必须使用 NoSQL，但具体优势要重新论证，不能“为了用而用”。
- MySQL 应作公平对照；不能说它不支持 JSON、数组或嵌套查询。
- 现有采集/数据处理/灌库脚本弃用，不运行、不复用、不恢复跟踪、不擅自删除。Trellis 管理命令仍可使用。
- 用户要求本轮只写详细文档和解释，代码交其他 agent；本轮许可只覆盖任务创建、研究和文档。

## 2. 当前状态与结论

状态 planning。文档研究完成不代表数据库优势已证明，也不代表获准实现。

当前数据是单来源、统一结构、单快照的 2251 个岗位组；没有已测性能优势。MongoDB 值得验证的是岗位聚合文档、有限技能/依据数组、原生筛选聚合的组织成本；MySQL 关系和 JSON 两种方案都可能同样合理。

个人收藏仍是浏览器本地状态，不强行迁移。数据发布版本是可验证候选，非 MongoDB 独有，是否采用需收益支撑；异构原始层是有真实输入/需求后的条件性扩展。

## 3. 阅读顺序

1. prd.md：本轮约束、R1–R9、AC01–AC10。
2. assessment.md：当前复评结论及不成立条件。
3. research/evidence.md、input-audit.json：真实输入与代码依据。
4. research/sources.md：官方能力、版本与部署限制。
5. design.md：不改应用契约的候选模型与数据版本边界。
6. benchmark-plan.md：公平对照、反证、故障与结果记录。
7. implement.md：后续阶段、批准门槛及禁止事项。
8. verification.md：本轮实际检查，绝不是新架构验收成绩。

## 4. 特别容易误读的地方

- 旧 frontend-crawl-demo 已归档并由另一 agent 实现；此次是新的数据层研究，不恢复旧任务状态。
- 旧规范、README 和测试可能仍引用 seed.py 或自动 JSON 回退；用户关于弃用脚本的最新约束优先。
- 本机 JSON 存在但被 Git 忽略，不能默认新克隆环境有输入。
- schemaVersion 只表达资料结构，数据 release_id 表达发布快照，source_record_id 表达来源稳定身份，代表岗位 ID 表达分组展示；不能混为同一个版本/去重键。
- MongoDB schema 灵活不是不用校验；索引定义不是命中证明；单文档原子性不是全数据集自动原子。
- 当前 Docker 配置不代表已具备副本集、事务和 Change Streams。
- 先核实驱动：Motor 官方弃用日期已过，新实验检查 PyMongo Async，保留现有代码兼容而不顺手全仓迁移。
- 任何实验结果对“当前小样本”“合成压力数据”“真实多来源/版本”分别下结论。

## 5. Trellis 接续

~~~powershell
python ./.trellis/scripts/get_context.py
python ./.trellis/scripts/task.py list
python ./.trellis/scripts/task.py validate .trellis/tasks/10-20-nosql-data-layer-review
~~~

active 指针按会话保存，新 agent 不保证继承。通过显式任务路径和任务列表发现，不新建重复研究。

不要为定位任务提前 start。只有用户在看到本版最终摘要后明确批准隔离验证，才细化对应验证任务并进入执行阶段。生产改造还需依据实测再审阅，不能一步跳过。

Trellis 子 agent 派发时第一行仍为本文首行 Active task；优先原生注入 prd/design/implement 与 jsonl；无注入时由接手者手动读取。

## 6. 可直接使用的接手提示

~~~text
Active task: .trellis/tasks/10-20-nosql-data-layer-review
读取 handoff.md、prd.md、assessment.md、design.md、benchmark-plan.md、implement.md 和相应 jsonl。
招聘主题和现有应用功能保留，现有业务脚本弃用，本任务只完成了研究文档。
首先确认最新消息是否批准本版后的隔离验证，不把“许可创建评估任务”当作代码或数据库操作授权。
以 MongoDB 文档、MySQL 关系、MySQL JSON 三种等义模型验证，不预设赢家。
你不是唯一编辑者，保留其他 agent 的改动；所有实验与生产数据隔离，不恢复旧 seed，不制造真实数据成绩。
按每个假设记录支持、反对和未验证证据，再决定最小生产方案。
~~~
