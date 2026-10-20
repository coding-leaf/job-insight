# 审查任务执行计划

## 实施前门槛

- [x] 用户同意创建任务，并审查现有 `docs/`。
- [x] 按用户最新纠正统一使用 `docs/review/`、`docs/archive/`，新增报告和归档快照使用时间戳。
- [x] 完成初步代码/配置检查与只读数据重算，复用旧 NoSQL 复评的决策边界。
- [x] 收齐两个研究文件并完成 PRD 收敛；最终规划摘要已呈现。
- [x] `implement.jsonl` 与 `check.jsonl` 各含五条真实规范/研究上下文，`task.py validate` 路径验证通过。
- [x] 用户已纠正根目录并要求查看实际交付文件；按原定报告和归档范围执行，不再增加审批轮次或业务改造。

## 执行顺序

1. **Trellis 实施代理**：加载本任务规划、研究与规范，复核文档原文哈希；选定统一时间戳。
2. 在 `docs/archive/` 留存四份过时状态原文，带时间戳命名，校验字节级一致性。任何移动的解析绝对路径必须位于本仓库预期源/目标目录；不递归删除或移动目录。
3. 刷新 `docs/` 四个权威入口的时效状态，保留有效契约，清楚区分历史快照、已有规则处理与尚未验收。维护活动引用和历史来源说明。
4. 输出 `docs/review/<timestamp>_project-review.md`，覆盖功能、技术栈、架构/数据流、数据边界、MongoDB 判断和已知限制。
5. 输出 `docs/review/<timestamp>_documentation-audit.md`，逐份记录原路径/哈希、过时依据、处理方式、当前和归档目标、历史链接解析规则及映射；在同目录保存带时间戳的结构化只读证据，供活动文档长期引用。
6. 更新根 README 报告入口及直接相关的环境/输入说明；给 PROJECT_HANDOFF 加历史标记与当前入口。
7. **Trellis 检查代理**：独立核对事实、范围、链接、快照哈希与当前规范；直接修复文档问题，记录复核结果。
8. 主会话核对验收项、记录验证与规范影响，按 Trellis 完成当前阶段，并在聊天交付结果与文件链接。

## 所有权与并行约束

- 主会话负责规划工件、研究汇总、任务状态、最终协调与交付。
- 实施代理拥有 `docs/*.md`、本批次 `docs/review/*`、`docs/archive/*`、README 和 PROJECT_HANDOFF 的文档变更，不触碰业务代码/数据。
- 研究代理只写各自分配的 `research/*.md`，不与实施代理共享目标文件。
- 检查代理在实施代理完成之后运行，避免同时改同一文档。

## 验证

- `git diff --check`：空白/冲突标记检查。
- 用标准库只读校验：四份档案 SHA-256 与 `research/data-stack-evidence.json` 中基线一致；当前必需文件存在；所有新产物文件名匹配时间戳规范。
- 校验活动 Markdown 本地链接及仓库引用。归档原文内部历史链接使用清单映射单独核对，仓库外历史来源显式标明，不伪报为当前可复现。
- 核对报告与路由/API/依赖清单/锁文件/只读审计一致，并逐项满足 AC1—AC7。
- `python ./.trellis/scripts/task.py validate <task-dir>`：上下文清单路径校验（若 CLI 形态不同，先看帮助）。
- 不为纯文档调整新增测试框架，不为证明报告内容而启动数据库或运行遗留脚本。应用测试、UI、性能、部署验证若未执行，报告明确注明。

## 回退点

在改写每份活动文档前完成原文快照和哈希核验。若活动规则被误改，从对应快照恢复并重新只修改状态/导航。报告不作为数据库变更授权；不存在业务数据回退步骤。

## Execution results

- Both review reports, permanent evidence JSON and four original snapshots now exist under docs/review and docs/archive.
- Four active contracts, README, historical handoff and five specification documents were refreshed without changing application code or data.
- Independent QA passed: 4 exact archive hashes, 198 active local links, 21 historical link mappings, 7 timestamped outputs, git diff --check and both context manifests. See verification.md.
- Application tests, database/UI/performance validation, Git commits and task archival were not performed.
