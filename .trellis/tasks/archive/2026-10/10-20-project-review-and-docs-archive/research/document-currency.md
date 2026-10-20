# Research: 现有文档时效与归档方案

- Query: 审查现有四份 `docs/*.md` 的有效约定、过时实现状态、历史证据与引用关系，形成可复核的组织方案。
- Scope: internal；只读检查当前仓库代码、已归档任务、既有处理产物及明确引用的相邻工作区文件是否存在/哈希是否匹配。
- Date: 2026-10-20（Asia/Shanghai）。
- Active task: `.trellis/tasks/10-20-project-review-and-docs-archive`。
- Boundary: 本研究只写本文件；未移动文档、修改代码/规范、执行旧处理或灌库脚本、启动/测试数据库、联网检索。

## Findings

### 1. 总体判断

四份文档均存在已过时的实现状态描述，但不是四份内容全部无效。字段、精确分组、类别边界、复核状态与统计解释仍是代码所引用的有效约定。不能仅因日期为 2026-10-17 就整体删除或让活跃入口失效。

建议执行 **原文快照归档 + 原路径刷新契约 + 新增时间戳审查报告**：

1. 将四份原始字节内容保存至 `docs/archive/`，文件名用同一次整理的 Asia/Shanghai 时间戳 `YYYY-MM-DD_HHmmss_<original-stem>.md`；路径已按用户最新纠正同步到 `docs/` 根目录，归档使用规范英文拼写。
2. 保留并刷新 `docs/data-dictionary.md`、`docs/job-classification.md`、`docs/statistical-methodology.md`、`docs/data-preparation-checklist.md`，继续作为稳定契约入口。文件日期、状态和能力说明更新；有效业务约定保留。
3. 新项目评估与归档清单写入 `docs/review/`，文件名带同格式时间戳；报告引用刷新后的契约和历史原文。
4. `README.md` 增加报告/审查入口；`PROJECT_HANDOFF.md` 增加“2026-10-17 历史交接”说明及当前报告链接，避免全文改写而抹去历史背景。
5. 保持规范与当前文档链接有效；历史任务的原始路径记录不应被当作需要批量重写的当前规划。

此处稳定契约入口不改名；时间戳用于本次新增报告和归档快照。这一组织方式保留现有引用契约，需在最终规划中明确披露。

### 2. Files found

| 文件 | 用途与审查结论 |
| --- | --- |
| `docs/data-dictionary.md` | 21 列来源字段、缺失规则、技能嵌套、来源追溯的权威定义；状态段落过时，缺少实际新增的薪资派生字段说明。 |
| `docs/job-classification.md` | 11 类词汇、提案/确认状态、组内裁定契约；“本次未分类”仅是旧任务历史，不能描述当前。 |
| `docs/statistical-methodology.md` | 19 列精确分组、有效薪资、排名阈值、比例分母、因果与覆盖边界；“尚无代码/页面”过时；部分规范不能冒充当前实现已经全部满足。 |
| `docs/data-preparation-checklist.md` | 2026-10-17 输入哈希/问题审计、待处理步骤、验收场景；作为“全部尚未执行”的当前清单已被实现取代，历史快照与剩余限制仍有用。 |
| `temp/data_prep/clean_and_group.py` | 当前原始输入查找、校验、19 列分组、技能并集、薪资标志与 JSON 投影实现。 |
| `temp/data_prep/pipeline.py` | 分类、裁定、CSV/JSON 和抽样报告生成流程；只读查看，未运行。 |
| `temp/data_prep/category_adjudicator.py` | 单来源/组级类别采用规则与 9 列 CSV 输出实现。 |
| `temp/data_prep/ai_classifier.py` | 名为 AI 的第二分类通道，实际以正则和关键词执行，返回 pending 提案；不是模型服务调用证据。 |
| `backend/app/db/repository.py` | MongoDB/内存两条查询统计路径；当前排序、排名、技能比例等实际行为。 |
| `backend/app/schemas/job.py` | 实际 API 投影类型；与来源业务契约存在需要说明的边界差异。 |
| `data/processed/jobs_cleaned_grouped.json` | 当前本地 2,251 组真实处理结果，29 个顶层字段；被 `.gitignore` 忽略。 |
| `data/processed/job_category_review.csv` | 当前本地 3,000 条复核快照，均 pending；被 `.gitignore` 忽略。 |
| `data/processed/audit_reports/*.md` | 已生成的分类/技能/重复抽样历史报告；其自动生成解释不等同于独立外部事实核实。 |
| `.trellis/tasks/archive/2026-10/10-17-data-contract/verification.md` | 旧纯文档任务验证范围和审计数值，不能用来证明后续应用已验证。 |
| `.trellis/tasks/archive/2026-10/10-17-data-prep-and-classification/task.json` | 处理任务已于 2026-10-18 completed；须结合脚本和实际产物判断完成范围。 |
| `.trellis/tasks/archive/2026-10/10-18-backend-data-and-api/task.json` | 后端任务归档，当前实际代码佐证接口已存在。 |
| `.trellis/tasks/archive/2026-10/10-18-mongodb-aggregation-refactor/task.json` | MongoDB 查询重构历史，不能由 task completed 推断数据库已运行或性能优越。 |
| `.trellis/tasks/archive/2026-10/10-20-frontend-crawl-demo/verification.md` | 后续应用已有页面与自动化验证记录；本研究未做广泛前端能力复查。 |
| `.trellis/tasks/archive/2026-10/10-20-nosql-data-layer-review/closure.md` | 已关闭选型复评的边界，明确没有证明 MongoDB 胜出且候选改造未授权。 |
| `README.md` | 当前启动说明，尚无 docs/ 报告导航；无需因本次审查整体归档。 |
| `PROJECT_HANDOFF.md` | 2026-10-17 交接历史，其中大量“当前未实现”已失效；应显式历史化并导向新报告。 |

### 3. 逐文件时效判断与建议处置

| 原路径 | 仍有效、应保留的内容 | 已过时或需要澄清的内容 | 建议最终路径与处理 |
| --- | --- | --- | --- |
| `docs/data-dictionary.md` | `:9-12` 缺失/原文/日期规则；`:20-40` 来源 21 字段含义；`:42-51` 显式省名映射与不可推测城市；`:55-72` 技能来源与完整依据对；`:78-83` source_ids、组级类别与统计值边界。 | `:3` “尚未建立数据库、接口或导入实现”已与代码不符。`:7` 输入链接位于仓库外，需标注历史工作区来源而非仓库自带。`:16-40` 的非空数量属于来源快照，应继续标日期而非改作常量。`:74-83` 仅列最小派生字段，现有 JSON 另有四项薪资派生字段，需说明实际投影。来源业务类型与 API 类型不能笼统称完全一致。 | 原文 → `docs/archive/<STAMP>_data-dictionary.md`；刷新后的权威入口仍为 `docs/data-dictionary.md`。 |
| `docs/job-classification.md` | `:7-23` 11 类、标题/正文和边界；`:37-59` 独立性与确认区别及 CSV 状态；`:63-85` 单来源/组级 pending 冲突传播和显式裁定；不接模型 API、不建在线复核页面的当前边界仍成立。 | `:3` “本次未对真实岗位执行分类”只描述旧文档任务；现在已有规则分类和真实复核 CSV。不能改成“人工复核完成”：当前 3,000 行均 pending，1,848 组 category_source=rule、403 组 null。`:37` 的独立 AI 通道契约不能被类名 `AIJobClassifier` 自动证明已经按模型或独立工具运行。 | 原文 → `docs/archive/<STAMP>_job-classification.md`；刷新入口 `docs/job-classification.md`，加“实现与验收状态”段，将真实分类运行与人工验收分开。 |
| `docs/statistical-methodology.md` | `:7-21` 原始字符串 19 列分组及岗位组解释；`:25-41` 有效区间、中位数、5 组门槛、薪资重叠筛选；`:45-49` 地区/学历/经验限制；`:55-66` K/N、L/N 与不可做因果结论；这些均有持续价值。 | `:3` “尚无统计代码或页面实现”过时；`:41` “若后续提供薪资范围筛选”已被岗位列表筛选实现。`:16-19` 是全局集合契约，当前分析端点仅使用类别/省份/学历，不接收列表所有关键词/薪资/标签条件，不可声称所有页面筛选已全量统一。`:17` 稳定同值 id 排序是规范，Mongo 列表实现没有该二级键。`:58` 的“技能标注比例”只定义 K/N，而当前 API 额外有 K/L，必须加清晰标签并说明 K/L 为已标注样本内部比例，不能伪称整体需求率。 | 原文 → `docs/archive/<STAMP>_statistical-methodology.md`；刷新入口 `docs/statistical-methodology.md`；保持规范目标，并单列目前实现边界/差异。 |
| `docs/data-preparation-checklist.md` | `:5-34` 输入快照/哈希、原文倒置 ID、来源缓存差异与错误维度恢复禁令；`:53-68` 验收案例与复算要求是可复用核验资产。 | `:3`、`:38`、`:40-49` 把已存在的清洗、分组、CSV、统计、接口与页面描述为未执行；`:43` “当前并无已经生成的复核文件”已明确失实。但 `:44` 人工验收/真实语义核查不可机械全部勾选；869 条来源缓存薪资差异和三条原文倒置也没有证据已修正。 | 原文 → `docs/archive/<STAMP>_data-preparation-checklist.md`；入口仍为 `docs/data-preparation-checklist.md`，可将标题刷新为“数据来源、处理状态与验收”。用“代码/产物存在”“历史验证记录”“未验证/未完成”区分每项，不把 task completed 当全部人工验收。 |

### 4. 代码模式与实际产物证据

#### 4.1 来源、分组、派生字段

- `temp/data_prep/clean_and_group.py:22-25` 固定了历史三份来源 CSV 的 SHA-256；本研究只读重算得到相同值，见后文。
- `temp/data_prep/clean_and_group.py:45-61` 在多个相邻工作区位置查找输入，证明处理流程不是仅依赖仓库自带输入。
- `temp/data_prep/clean_and_group.py:64-82` 数值解析和空单元格转换；`:150-175` 明确原始 19 字符串字段键；`:195-235` 代表 ID/source_ids 与技能依据对并集去重；`:242-245` 分组后规范省名。
- `temp/data_prep/clean_and_group.py:251-290` 已设置倒置原文排除、闭区间资格、薪资中点及排除原因，四项实际派生字段为 `salary_eligible_for_midpoint`、`salary_midpoint`、`salary_stat_excluded`、`salary_exclude_reason`。原文“中点不要求新增持久化字段”是最低契约，不禁止现实现持久化；刷新时应如实记录现有投影。
- `temp/data_prep/pipeline.py:81-94` 使用既有复核 CSV 并保留 confirmed 行；`:105-138` 规则与第二通道输出后裁定并写 CSV；`:147-160` 组级裁定及 JSON；`:166-185` 生成审计报告。这些实现和本地文件足以否定“脚本/复核文件尚未存在”，不等同于本次运行过脚本。
- `.trellis/tasks/archive/2026-10/10-17-data-prep-and-classification/task.json:6,14` 记载 completed/2026-10-18；但历史 `implement.md` 内未勾选项不是当前状态的唯一证据。

主会话保存的只读重算证据 `research/data-stack-evidence.json` 显示：2,251 组、3,000 唯一来源 ID、305 多记录组、2,194 有效薪资组、833 带技能组、24 标签；当前 JSON 29 字段；1,848 组为规则类别、403 组未分类；3,000 条复核全部 pending。这里引用该主会话证据，不重复运行生成脚本。

#### 4.2 分类与“AI”措辞

- `temp/data_prep/category_adjudicator.py:45-105` 实现 pending/confirmed 单来源采用；`:109-171` 实现全组冲突/一致裁定；`:179-198` 写 UTF-8 BOM 9 列 CSV。与原契约的主要边界有直接对应。
- `temp/data_prep/ai_classifier.py:121` 默认名字为 `AI:Opencode`；`:142-148` 调用本类 `_evaluate_semantics` 并直接写来源与 pending；`:151` 起主体由正则与关键词分支组成（例如 `:194` 正则查找、`:408` AI 词组判断、`:428` 数据词组判断）。类名、文本“AI评估”和来源标签不是实际大模型调用或人工确认记录。
- 旧 `data/processed/audit_reports/classification_review.md:31` 明确未决冲突保留 null，与当前 pending 状态相容；但其 `:65-67` “AI深入正文”等解释只应作为自动生成历史文本看待。
- 原文 `docs/job-classification.md:37-59` 仍是应执行的独立性/确认契约；更新状态时不能以“两段不同规则”冒充经独立模型评审或人工验收完成。

#### 4.3 统计规范与当前差异

- `backend/app/db/repository.py:91-105` 已实现中位数与 inclusive 四分位数；`:408-429` 是类别低样本标志和排除未分类/低样本排名；`:484-492` 是未知省份/低样本排除。
- `backend/app/db/repository.py:501-581` Mongo 技能聚合同时计算 N、L、K；`:568-571` 明确 `ratio_annotated=K/L`、`ratio_total=K/N`，覆盖率 `:561` 为 L/N。原文 K/N 整体标注比例与 L/N 覆盖仍成立，但新增 K/L 的命名需要准确说明。
- `backend/app/api/v1/endpoints/stats.py:25-28,39-42,54-58` 统计只传类别/省份/学历；`backend/app/api/v1/endpoints/jobs.py:31-42` 列表另外传关键词、薪资上下限、有无标签、排序分页。原统一集合约定不应被解读为当前所有列表专属条件都会驱动图表。
- `docs/statistical-methodology.md:17` 要求同值以 id 升序；`backend/app/db/repository.py:600-601` Mongo 路径只对单字段排序，没有显式 id 二级键。内存路径 `:933-945` 也未显式构造二级键，当前结果的稳定性依赖预载数组顺序及 Python 稳定排序。此处应记录为实现差异，不在本任务改代码，也不为迎合实现而删掉有效排序契约。
- `docs/statistical-methodology.md:27` 要求有限正数；`temp/data_prep/clean_and_group.py:265-270` 只做非正数和倒置比较，未见显式 isfinite。当前真实基准没有因此构成异常的证据；不能将其泛化验证声称全部覆盖。
- `docs/data-dictionary.md:24,31-32,70` 的来源业务类型允许 company=null、十进制薪资、origin/evidence=null；`backend/app/schemas/job.py:5-7,21,28-29` API 类型分别是非空字符串/整数。这些是来源契约与 API 投影的实际差异；不得将 21 列来源定义简单改写成 API schema 后宣称完全一致。当前来源值是否触发异常另行核查，不能由类型差异断言现有样本已坏。

### 5. 引用关系与组织兼容性

#### 5.1 当前入口和规范 backlinks

| 引用方 | 位置 | 目标/处理建议 |
| --- | --- | --- |
| `PROJECT_HANDOFF.md` | `:7-14` | 将四份 docs 称当前权威文档并逐一链接；保留这些稳定目标，加历史交接标记与新报告入口。 |
| `PROJECT_HANDOFF.md` | `:36-41,57,74,107-109,118-119,135-137` | “数据库/业务代码/依赖/分类未实现”“下一步仍设计”等语句过时；适合整体标记为 2026-10-17 历史，不建议逐条重写伪装成当日新结论。 |
| `README.md` | `:10-12,49-64,68-74` | 当前提供离线/数据库启动与构建说明；尚无 docs/ 报告 backlink，可加导航；这些命令不是本研究已实际执行的部署验证。 |
| `.trellis/spec/backend/data-contract.md` | `:9-12` | 链接四份 docs；稳定路径保留后不用大范围改引用。 |
| `.trellis/spec/backend/data-contract.md` | `:3` 对照 `:18,28,54,68,70` | 既写 implemented 又残留 future/pure-doc-task 文案，内部状态矛盾；main 可通过 update-spec 补齐当前状态/代码边界，不改业务约定。 |
| `.trellis/spec/backend/index.md` | `:9,14,27` | “future implementation / pending”与代码不符；应最小刷新状态，避免 spec 继续误导。 |
| `.trellis/spec/frontend/index.md` | `:9,13-14` | 保留字典/统计/Data Contract 链接；“Application conventions remain scaffolding”属旧状态。 |
| `.trellis/spec/backend/database-guidelines.md` | `:32-43,49-51` | “所有统计原生聚合”和“100% 命中四索引”不受代码/执行计划充分支持，不能随旧文档照搬；分位数在 Python 计算，是否命中索引需 explain 证据。 |
| 四份 `docs/*.md` | 相互引用分布见下节 | 保持原文件名可继续解析，刷新内容时指向当前契约。 |

其他检索发现的旧任务路径引用：`10-17-data-contract/design.md:9-12`、同任务 `task.json:24-27`、`10-17-data-prep-and-classification/prd.md:5,34`。历史 task manifests 也引用现有 docs；本研究未加载 implement/check manifest 内容。保留当前入口即可兼容；不需要为整理而重写历史任务。

#### 5.2 原文互链及历史解析基准

- 字典：`:3` → 准备清单；`:7` → 统计；`:31` → 统计；`:79` → 分类；`:83` → 分类和统计。
- 分类：`:3` → 字典；`:76` → 统计。
- 统计：`:3` → 字典、分类、准备清单。
- 准备清单：`:3` → 字典、分类、统计。

**精确原文归档与新位置相对链接不能同时自然成立。** 例如归档文件 `docs/archive/<STAMP>_data-dictionary.md` 原文仍链接 `data-preparation-checklist.md`，该无时间戳 peer 在新位置不再存在；外部输入相对路径也会改变含义。不可为修复新位置链接而修改“原样快照”的字节内容。

主会话已确认的方案：归档清单逐份记 `original_path`、`archive_path`、`sha256`、原始解析基准 `docs/`，并为历史链接记录“原始路径上下文 → 当前有效目标/仓库外历史来源”的映射。当前入口和新报告的链接必须按实际所在位置可解析；不可变快照的原文链接按记录的原始基准审计。最终 AC/链接检查应明确区分这两类，不能让普通链接检查器按新位置把历史原文误报成未修复当前链接。

### 6. 仓库外来源链接与可复现性

以下是本地工作区文件路径，不是 HTTP 外部资料。本研究未联网。2026-10-20 `Test-Path` 结果表明三份 CSV 与来源缓存当前均存在于相邻目录；它们在本仓库根目录之外，clone 仓库本身不保证可获得这些输入。

| 原文位置 | 写入的链接/路径 | 按原位置解析后的来源 |
| --- | --- | --- |
| `docs/data-dictionary.md:7`；`docs/data-preparation-checklist.md:11` | `../../清洗后数据/jobs_clean_final.csv` | `D:/code/Workspace/bigdata/清洗后数据/jobs_clean_final.csv` |
| `docs/data-dictionary.md:7`；`docs/data-preparation-checklist.md:12` | `../../清洗后数据/skills.csv` | `D:/code/Workspace/bigdata/清洗后数据/skills.csv` |
| `docs/data-dictionary.md:7`；`docs/data-preparation-checklist.md:13` | `../../清洗后数据/job_skills.csv` | `D:/code/Workspace/bigdata/清洗后数据/job_skills.csv` |
| `docs/data-preparation-checklist.md:23` | `../../原始数据/social_cached.csv` | `D:/code/Workspace/bigdata/原始数据/social_cached.csv` |
| `PROJECT_HANDOFF.md:61,65-68` | `../清洗后数据/*` | 同一仓库外核心数据目录；手工交接说明也在其中，不应冒充仓库内文档。 |
| `PROJECT_HANDOFF.md:49-55` | `../原始数据/*`、`../final-homeworkwork/*` | 相邻采集/旧资料历史路径；本研究没有扩大检查这些非核心文件的内容或状态。 |

当前只读重算的输入 SHA-256 与准备清单历史值一致：

| 来源 | SHA-256 |
| --- | --- |
| `jobs_clean_final.csv` | `9115d09875b3b11b2b2af584e45023ac95d6955f37b6d33b9b777a84b8a84a00` |
| `skills.csv` | `937b05c9791ad9e75228dfe5ad5994c140f4cf06c93f26c1492190a7b9d3133c` |
| `job_skills.csv` | `f95e85e77ebb77321868587931dac2e0bbb5a2a6bd3bab37ef503b0c8cda528e` |

`.gitignore:56-61` 明确忽略 `data/processed/*.json`、`data/processed/*.csv` 和 `backend/app/db/seed.py`。这些本地文件存在，并不等于新 clone 已具备离线基准与灌库入口。整理文档时应保留这个交付边界，不运行生成器掩盖缺失。

### 7. 归档原文完整性基准

本研究于整理前读取原文 SHA-256；执行阶段若原件已有他人变更，必须重新核对而非覆盖：

| 原路径 | SHA-256 |
| --- | --- |
| `docs/data-dictionary.md` | `aca0378c47a99c13078e62e5ffa51e510c89306e2160812bd2588277ae31f41e` |
| `docs/job-classification.md` | `c5c115242fea02027910c405b42aa8452bf3406b8061ec0fd865662aa03a35b1` |
| `docs/statistical-methodology.md` | `7b47c4894f7488dd7eb65e99804000a1a8efc65ba53f3d980ba4fa2a0d21fc7b` |
| `docs/data-preparation-checklist.md` | `6da869eca1230b90f392b3c2fc173fe94caf83cb8aceec8ccdda81fa147e64ac` |

建议审查清单对每份包含：原路径、原始标题/日期、判断（部分过时/历史清单）、具体过时依据、保留的契约、归档路径、当前入口、原文哈希、原文链接解析基准。这样四份原文不是无解释地搬走，且可独立复核字节一致性。

### 8. Related specs

- `.trellis/workflow.md`：规划/研究/实现/核验阶段；本次只完成研究产物。
- `.trellis/spec/backend/data-contract.md`：继续持有来源、分组、复核与统计约定，不因状态旧文案而作废。
- `.trellis/spec/backend/index.md`：数据变更前阅读契约、同组一致与运行时不可写死计数。
- `.trellis/spec/frontend/index.md`：字典/统计入口、低样本和缺失值展示约定。
- `.trellis/spec/backend/database-guidelines.md`：本次报告应以代码与查询证据校正的状态说明，尤其不应将索引定义当执行计划。
- `.trellis/spec/guides/index.md:70-79`：修改值前先搜索所有引用；本研究已执行针对四个文件名/路径的仓库检索。

## Caveats / Not Found

- 文档根目录已按用户最新纠正统一为 `docs/`；其中审查/归档子目录和实际时间戳由后续已批准执行阶段创建。本研究没有提前移动/复制任何原文。
- 本研究没有执行 `pipeline.py`、`verify_contracts.py`、灌库脚本、pytest 或 MongoDB 连接；历史验证记录不能描述为本次复测。
- 旧 `.trellis/tasks/archive/2026-10/10-17-data-contract/verification.md:3,16,28` 是 2026-10-17 文档任务的证据，曾明确没有应用；后续脚本/产物和归档任务已改变实现状态。两者并不互相冲突，错误来自把旧历史状态继续作为“现在”。
- `data/processed/audit_reports/duplicate_groups_audit.md:54-59,94-103` 把日期跨度/URL 差异解释为平台刷新与企业机制，现有字段本身不能证明具体机制；不得将这些历史自动生成因果叙述抄成当前事实。保留“精确字面分组不等于独立招聘”的有效结论即可。
- 人工确认、独立模型评估和原网页薪资核实均未由本次证据证明完成。更新准备清单应保留这些未完成事项。
- 已归档 NoSQL 复评 `closure.md:5-12` 明确：主题和功能保留，未证明 MongoDB 胜过 MySQL；复杂收藏/版本方案无实施授权。不能因整理文档而复活旧设计/benchmark-plan。
- 本研究定位到几处实现与规范差异，均供报告披露及未来明确范围内处理；未扩大为当前修复或迁移任务。
