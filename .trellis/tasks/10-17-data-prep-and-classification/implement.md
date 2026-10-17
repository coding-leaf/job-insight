# 数据清洗规范与双路岗位分类实施 — 执行计划

## 实施阶段与有序检查清单

### Phase 1: 准备与基础设施搭建
- [ ] 1.1 建立目录结构 `scripts/data_prep/` 与 `data/processed/` 及 `data/processed/audit_reports/`。
- [ ] 1.2 编写 `scripts/data_prep/clean_and_group.py`，实现原始 19 列分组、代表 ID 提取、技能聚合、数值安全转换、省级规范映射与薪资排除标记。
- [ ] 1.3 验证阶段一输出：确保生成 2251 个岗位组，305 个多记录组，哈希及数据结构正确。

### Phase 2: 双路分类引擎实现
- [ ] 2.1 编写 `scripts/data_prep/rule_classifier.py`，实现符合 `docs/job-classification.md` 的规则分类器。
- [ ] 2.2 编写 `scripts/data_prep/ai_classifier.py`，实现隔离规则结果、基于职责描述与 11 类别白名单的独立 AI 分类提案生成器。
- [ ] 2.3 编写 `scripts/data_prep/category_adjudicator.py`，实现单来源状态转换与组级一致性裁定逻辑，导出 9 列 `job_category_review.csv`。

### Phase 3: 抽样质检与审计报告生成
- [ ] 3.1 编写 `scripts/data_prep/sampling_audit.py`：
  - 生成 `classification_review.md`（冲突、多岗位、笼统校招、标题正文矛盾清单及一致项抽样复核）。
  - 生成 `skill_accuracy_audit.md`（针对 1107 条有标签岗位进行抽样核查正文真实性，分析“依据仅重复技能名”的客观质量）。
  - 生成 `duplicate_groups_audit.md`（针对 305 组完全重复组抽样比对业务含义，分析重复抓取与批次招聘）。
- [ ] 3.2 编写 `scripts/data_prep/pipeline.py`，实现一键端到端运行整个数据清洗、分类与报告生成流程。

### Phase 4: 自动化验收测试与只读校验
- [ ] 4.1 编写 `scripts/data_prep/verify_contracts.py`，覆盖全部 8 项验收标准（AC-1 ~ AC-8）。
- [ ] 4.2 运行验收脚本，核验三份原始输入文件 SHA-256 绝对一致，确认 2251 组数、分类状态、技能覆盖率及薪资有效样本统计。
- [ ] 4.3 整理执行结果，准备进入评审与 Finish 阶段。

---

## 验证命令与检查关卡 (Validation Commands)

```bash
# 1. 运行一键式完整清洗与分类流水线
python scripts/data_prep/pipeline.py

# 2. 运行自动化契约与只读完整性验收
python scripts/data_prep/verify_contracts.py

# 3. 检查生成文件存在性与大小
ls -la data/processed/
ls -la data/processed/audit_reports/
```

---

## 风险文件与回滚策略 (Risky Files & Rollback)

- **原始输入保护**：原始文件位于 `../清洗后数据/`，严禁任何写操作（`open(..., 'w')`）。在流水线前后通过 SHA-256 校验确保无副作用。
- **回滚方式**：所有脚本与产物均限定在 `scripts/data_prep/` 与 `data/processed/`。若实现需要推倒重来，直接删除 `data/processed/` 重新运行流水线即可，无跨模块污染风险。
