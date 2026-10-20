# JobInsight 文档时效审查与归档清单

审查批次：`2026-10-20_203614`（Asia/Shanghai，2026-10-20 20:36:14）。时间戳表示本轮文档整理批次，不表示招聘采集、数据修改或应用部署时间。

本轮审查 `docs/` 原有四份文档、根 README 和交接说明。结论是：四份契约仍有价值，但“尚无分类、接口或页面”等实现状态已经过时；先保留原始字节快照，再刷新原路径。新文件放 `docs/review/`，历史原文放 `docs/archive/`；稳定契约入口继续沿用原文件名。

项目功能、技术栈、架构与 MongoDB 判断见[项目现状报告](2026-10-20_203614_project-review.md)。本清单记录文档处置及证据，避免把历史待办写成当前事实。

## 1. 每份文档的时效结论

| 原路径 / 当前入口 | 原文标题与时间 | 时效判断和具体依据 | 本轮处置与原文快照 |
| --- | --- | --- | --- |
| [docs/data-dictionary.md](../data-dictionary.md) | JobInsight 字段字典；2026-10-17 契约 | 部分过时。原第 3 行称尚无数据库、接口或导入实现，现有 [repository.py](../../backend/app/db/repository.py) 和 [clean_and_group.py](../../temp/data_prep/clean_and_group.py) 已有实现。最小派生字段表缺少实际四项薪资字段，来源与 API 类型也有差异。 | 保留全部 21 列、缺失、省名映射、技能依据和追溯契约；刷新状态，说明实际 29 字段投影与 schema 差异。原文完整保存在 [archive/2026-10-20_203614_data-dictionary.md](../archive/2026-10-20_203614_data-dictionary.md)。 |
| [docs/job-classification.md](../job-classification.md) | 岗位分类与离线复核；2026-10-17 契约 | 部分过时。“未对真实岗位执行分类”已与本地结果不符，但尚不能称人工验收完成。只读审计为 1,848 个规则分类组、403 个未分类组，复核 3,000 行全部 pending。`AIJobClassifier` 实际是正则/关键词通道，不能据名字证明调用模型。 | 保留 11 类边界、独立提案、pending/confirmed 和组内裁定规则；追加真实运行及未验收边界。原文保存在 [archive/2026-10-20_203614_job-classification.md](../archive/2026-10-20_203614_job-classification.md)。 |
| [docs/statistical-methodology.md](../statistical-methodology.md) | JobInsight 统计口径；2026-10-17 契约 | 部分过时。“尚无统计代码或页面”已失效；薪资范围筛选已存在。原文只定义 K/N、L/N，现有 API 另有 K/L；列表与分析端点的条件范围不相同，显式 id 二级排序也尚未完整落实。 | 保留 19 列原始字符串分组、有效薪资、中位数、低样本和非因果解释；补充 K/L 及当前差异，不能为迎合代码删改有效规范。原文保存在 [archive/2026-10-20_203614_statistical-methodology.md](../archive/2026-10-20_203614_statistical-methodology.md)。 |
| [docs/data-preparation-checklist.md](../data-preparation-checklist.md) | 数据准备与验收清单；2026-10-17 只读快照 | 作为“全部尚未执行”的当前清单已过时。清洗、分组、分类 CSV、JSON 和接口/页面均存在；但独立模型评估、人工确认、869 条缓存薪资差异的原网页核实不能因此标为完成。 | 改为当前来源可用性、产物、完成边界及剩余核实清单；保留哈希、倒置 ID、历史审计和验收场景。原文保存在 [archive/2026-10-20_203614_data-preparation-checklist.md](../archive/2026-10-20_203614_data-preparation-checklist.md)。 |
| [README.md](../../README.md) | 部署指南；无日期 | 仍需作为运行入口。Node 18+ 与锁文件的 Vite engine 不符；本地 JSON 和 seed 被 Git 忽略，不能宣称克隆即可灌库。 | 保留运行命令，更新 Node 条件、输入交付说明、MongoDB 模式边界及报告导航；不为本轮审查重跑部署。 |
| [PROJECT_HANDOFF.md](../../PROJECT_HANDOFF.md) | JobInsight：已知事项交接；2026-10-17 | 历史交接。大量“当前未建立工程”的段落不再描述当前状态；课程背景、约束和来源审计仍可追溯。 | 在开头明确整篇历史属性、仓库外路径属性并链接当前报告；保留正文历史措辞，不重写成当日新结论。 |

归档依据是内容与当前代码/产物冲突，日期只是快照属性。四份旧原文均完整留存，当前有效契约入口没有删除；过去 Trellis 任务记录没有改写。

本轮同步刷新了 `.trellis/spec/backend/index.md`、`.trellis/spec/frontend/index.md` 的旧实现状态，以及 `.trellis/spec/guides/index.md` 的审查/归档约定；质量复核还最小修正了 `.trellis/spec/backend/data-contract.md` 的历史/当前状态和 `database-guidelines.md` 中全部原生统计、保证索引命中等无证据表述。有效数据契约仍指向原有稳定入口，不因整理改掉业务规则。

## 2. 原文完整性与恢复映射

四份源文件在复制前先与本任务研究基线比对，均一致；目标字节内容的 SHA-256 再次与源基线比对。下表的 `original_path` 也是原文链接的解析基准。

| original_path | archive_path | 原始 SHA-256 |
| --- | --- | --- |
| `docs/data-dictionary.md` | [docs/archive/2026-10-20_203614_data-dictionary.md](../archive/2026-10-20_203614_data-dictionary.md) | `aca0378c47a99c13078e62e5ffa51e510c89306e2160812bd2588277ae31f41e` |
| `docs/job-classification.md` | [docs/archive/2026-10-20_203614_job-classification.md](../archive/2026-10-20_203614_job-classification.md) | `c5c115242fea02027910c405b42aa8452bf3406b8061ec0fd865662aa03a35b1` |
| `docs/statistical-methodology.md` | [docs/archive/2026-10-20_203614_statistical-methodology.md](../archive/2026-10-20_203614_statistical-methodology.md) | `7b47c4894f7488dd7eb65e99804000a1a8efc65ba53f3d980ba4fa2a0d21fc7b` |
| `docs/data-preparation-checklist.md` | [docs/archive/2026-10-20_203614_data-preparation-checklist.md](../archive/2026-10-20_203614_data-preparation-checklist.md) | `6da869eca1230b90f392b3c2fc173fe94caf83cb8aceec8ccdda81fa147e64ac` |

快照保留原有编码、换行和全部正文，未添加历史提示或改写链接。需要恢复旧版本时可从相应快照取回原路径，恢复前应检查现有文档是否已有新修改。

## 3. 不可变快照的历史链接如何理解

归档快照里的链接是原文的一部分。把文件放进 `archive/` 后，原本的 `data-dictionary.md` 等相对链接不会自动变成带时间戳的新文件名。本轮不修改快照来伪装它们仍按新目录解析，而以原始 `docs/<name>.md` 为基准解释，并在下面提供可点击目标。

| 含该链接的原文 | 原文目标字符串 | 原路径上下文的含义 | 当前有效目标 / 同批历史目标 |
| --- | --- | --- | --- |
| 字典、分类、准备清单 | `statistical-methodology.md` | `docs/statistical-methodology.md` | [当前统计口径](../statistical-methodology.md) / [历史统计原文](../archive/2026-10-20_203614_statistical-methodology.md) |
| 字典、统计、准备清单 | `job-classification.md` | `docs/job-classification.md` | [当前分类契约](../job-classification.md) / [历史分类原文](../archive/2026-10-20_203614_job-classification.md) |
| 分类、统计、准备清单 | `data-dictionary.md` | `docs/data-dictionary.md` | [当前字段字典](../data-dictionary.md) / [历史字段原文](../archive/2026-10-20_203614_data-dictionary.md) |
| 字典、统计 | `data-preparation-checklist.md` | `docs/data-preparation-checklist.md` | [当前来源与处理状态](../data-preparation-checklist.md) / [历史准备原文](../archive/2026-10-20_203614_data-preparation-checklist.md) |
| 字典、准备清单 | `../../清洗后数据/jobs_clean_final.csv` | 仓库父目录的 `清洗后数据/jobs_clean_final.csv` | 仓库外历史输入；其哈希与交付边界见[当前来源清单](../data-preparation-checklist.md)。 |
| 字典、准备清单 | `../../清洗后数据/skills.csv` | 仓库父目录的 `清洗后数据/skills.csv` | 仓库外历史输入；见[当前来源清单](../data-preparation-checklist.md)。 |
| 字典、准备清单 | `../../清洗后数据/job_skills.csv` | 仓库父目录的 `清洗后数据/job_skills.csv` | 仓库外历史输入；见[当前来源清单](../data-preparation-checklist.md)。 |
| 准备清单 | `../../原始数据/social_cached.csv` | 仓库父目录的 `原始数据/social_cached.csv` | 仓库外来源缓存；只用于历史按 ID 对照，未经本轮原网页核实。 |

本次研究检查时三份输入及缓存都在本机相邻目录可见。以当前机器为例，原始来源根目录为 `D:/code/Workspace/bigdata/清洗后数据/` 和 `D:/code/Workspace/bigdata/原始数据/`，它们不在 `job-insight/` 仓库内。这些说明不构成对其他机器文件可用性的保证。

`PROJECT_HANDOFF.md` 的 `../清洗后数据/*`、`../原始数据/*`、`../final-homeworkwork/*` 也按其原始根目录上下文理解为仓库外历史工作区材料；其中较早样本和旧采集项目未在本轮扩大核查。当前四份活动契约已将此类输入改成文字来源说明。快照和历史交接的原文链接不纳入“按新位置逐个可打开”的活动文档链接通过数。

## 4. 当前证据及仍未解决的事项

本任务的[只读数据审计](2026-10-20_203614_data-stack-evidence.json)于 2026-10-20 重算：JSON 为 4,189,728 字节，SHA-256 为 `0f317fb486052a56f1c1f00b6c00da071c12f9fec98dd7993273469eb13498b1`；2,251 组、3,000 个来源 ID、2,194 个有效薪资组、833 个有标签组，覆盖率约 37.01%。机器可读证据随本清单存放于 `docs/review/`，不依赖活动任务目录；更多能力与证据见[项目现状报告](2026-10-20_203614_project-review.md)。这是当前本地静态数据的证据，不是生产服务或市场总体证明。

需要继续明示以下边界：

- [API schema](../../backend/app/schemas/job.py) 的公司、薪资整数和技能依据类型与[来源字段契约](../data-dictionary.md)并非完全一致；本轮只披露，不改业务代码或放宽契约。
- 分析端点使用类别、省份、学历，岗位列表另有关键词、薪资、标签条件；不能宣称当前所有页面都共享列表全部筛选。MongoDB 列表也未显式添加排序同值的 id 二级键。
- 技能页展示 `K/L`（已标注样本内部比例）、`K/N`（全量标注比例）及 `L/N`（覆盖率）；没有标签不代表无要求。薪资有效样本少于 5 必须预警且不进入排名。
- 3,000 条复核全部 pending，不代表人工确认；第二分类器由正则与关键词实现，名称中有 AI 也不等于模型 API 接入或独立模型评估完成。
- 原网页薪资核实、语义重复/独立招聘判定仍未完成；已排除三组原文倒置不等于源值已经修正。
- [Git 忽略规则](../../.gitignore)排除了 processed JSON/CSV 和旧 seed 脚本；本地存在不等于新克隆自带。README 已纠正相关前提。

MongoDB 的使用与必要性由[项目现状报告](2026-10-20_203614_project-review.md)单独评估：已有查询和聚合职责，但本轮没有性能对照、执行计划或数据库迁移，不把 NoSQL 课程约束解释成实测优势。

## 5. 本轮验证范围

本轮只执行文档与只读文件检查：归档前后哈希、目标路径边界、活动文档仓库内链接、时间戳命名和 `git diff --check`。四份快照使用上表的原路径基准及映射核对，不改动字节。源数据、业务脚本、应用代码和过去 Trellis 归档均不修改。

本轮没有运行清洗/分类/seed、安装依赖、连接或启动 MongoDB、执行应用测试/构建、浏览器验收、性能测试或生产部署。历史任务的验证记录只作历史证据；测试文件存在和任务 completed 都不等于本轮运行通过。
