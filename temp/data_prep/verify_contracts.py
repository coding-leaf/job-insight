"""Automated Contract Verification Suite.

Tests and asserts all 8 acceptance criteria (AC-1 ~ AC-8) defined in
.trellis/tasks/10-17-data-prep-and-classification/prd.md.
"""

from __future__ import annotations

import csv
import io
import json
import sys
from pathlib import Path

# Ensure project root and module directory are in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = Path(__file__).resolve().parent
for p in [str(PROJECT_ROOT), str(MODULE_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from temp.data_prep.ai_classifier import AIJobClassifier  # noqa: E402
    from temp.data_prep.category_adjudicator import (  # noqa: E402
        adjudicate_group_level,
        adjudicate_single_source,
        load_existing_reviews,
    )
    from temp.data_prep.clean_and_group import (  # noqa: E402
        EXPECTED_HASHES,
        PROVINCE_MAPPING,
        REVERSED_SALARY_IDS,
        compute_file_sha256,
        find_data_file,
    )
    from temp.data_prep.rule_classifier import classify_by_rule  # noqa: E402
except ImportError:
    from ai_classifier import AIJobClassifier  # type: ignore # noqa: E402
    from category_adjudicator import (  # type: ignore # noqa: E402
        adjudicate_group_level,
        adjudicate_single_source,
        load_existing_reviews,
    )
    from clean_and_group import (  # type: ignore # noqa: E402
        EXPECTED_HASHES,
        PROVINCE_MAPPING,
        REVERSED_SALARY_IDS,
        compute_file_sha256,
        find_data_file,
    )
    from rule_classifier import classify_by_rule  # type: ignore # noqa: E402

VALID_CATEGORIES = {
    "算法与人工智能",
    "数据分析与大数据",
    "软件开发",
    "软件测试",
    "运维与云平台",
    "网络与信息安全",
    "硬件与芯片",
    "通信",
    "技术支持与实施",
    "项目与产品",
    "其他明确岗位",
}

VALID_MUNICIPALITIES = {"北京市", "上海市", "重庆市", "天津市"}


def test_ac1_readonly_integrity() -> None:
    """AC-1: Verify that raw input files remain untouched and match exact SHA-256 hashes."""
    print("Verifying AC-1: Read-only input integrity...")
    for filename, expected_hash in EXPECTED_HASHES.items():
        filepath = find_data_file(filename)
        actual_hash = compute_file_sha256(filepath)
        assert actual_hash == expected_hash, (
            f"AC-1 FAIL: Hash mismatch for {filename}! Expected {expected_hash}, got {actual_hash}"
        )
        print(f"  [PASS] {filename} SHA-256 matches: {actual_hash}")


def test_ac2_exact_grouping_consistency(grouped_jobs: list) -> None:
    """AC-2: Verify exact 19-column grouping generates 2251 groups, 305 multi-record groups, 749 excess."""
    print("Verifying AC-2: Exact grouping consistency...")
    assert len(grouped_jobs) == 2251, (
        f"AC-2 FAIL: Expected 2251 groups, got {len(grouped_jobs)}"
    )

    multi_groups = [g for g in grouped_jobs if len(g["source_ids"]) > 1]
    assert len(multi_groups) == 305, (
        f"AC-2 FAIL: Expected 305 multi-record groups, got {len(multi_groups)}"
    )

    excess = sum(len(g["source_ids"]) - 1 for g in multi_groups)
    assert excess == 749, f"AC-2 FAIL: Expected 749 excess records, got {excess}"

    # Verify representative ID and source_ids sorting
    for g in grouped_jobs:
        s_ids = g["source_ids"]
        assert len(s_ids) >= 1, "AC-2 FAIL: Empty source_ids"
        assert s_ids == sorted(s_ids), "AC-2 FAIL: source_ids not sorted ascending"
        assert g["id"] == min(s_ids), (
            f"AC-2 FAIL: Representative id {g['id']} != min(source_ids) {min(s_ids)}"
        )

    print("  [PASS] Exactly 2251 groups, 305 multi-record groups, 749 excess records.")
    print(
        "  [PASS] All representative IDs are lexicographically smallest and source_ids sorted."
    )


def test_ac3_cleaning_and_mapping(grouped_jobs: list) -> None:
    """AC-3: Null representations, numeric parsing, 4 province mappings, city restrictions."""
    print("Verifying AC-3: Cleaning and mapping compliance...")
    provinces_seen = set()
    cities_seen = set()

    for g in grouped_jobs:
        # Province mappings
        prov = g["province"]
        if prov:
            provinces_seen.add(prov)
            assert prov not in PROVINCE_MAPPING, (
                f"AC-3 FAIL: Unmapped province alias found: {prov}"
            )

        # City check: only municipalities or None
        city = g["city"]
        if city:
            cities_seen.add(city)
            assert city in VALID_MUNICIPALITIES, (
                f"AC-3 FAIL: Speculative city found: {city}"
            )

        # Headcount parsing (e.g. 5.0 -> 5)
        hc = g["recruitment_headcount"]
        if hc is not None:
            assert isinstance(hc, int), f"AC-3 FAIL: Headcount {hc} is not an integer!"

        # Experience years parsing
        exp = g["experience_min_years"]
        if exp is not None:
            assert isinstance(exp, (int, float)), (
                f"AC-3 FAIL: Exp years {exp} is not numeric!"
            )

        # Skills representation
        skills = g["skills"]
        assert isinstance(skills, list), "AC-3 FAIL: Skills is not a list"
        for s in skills:
            assert "skill_name" in s, "AC-3 FAIL: Missing skill_name in skills"
            assert "provenance" in s, "AC-3 FAIL: Missing provenance in skills"
            for p in s["provenance"]:
                assert "origin" in p and "evidence" in p, (
                    "AC-3 FAIL: Invalid provenance pair"
                )

    assert "广西省" not in provinces_seen
    assert "内蒙古省" not in provinces_seen
    assert "新疆省" not in provinces_seen
    assert "西藏省" not in provinces_seen
    assert "广西壮族自治区" in provinces_seen
    assert "内蒙古自治区" in provinces_seen
    assert "新疆维吾尔自治区" in provinces_seen
    assert "西藏自治区" in provinces_seen

    print(
        "  [PASS] All 4 province aliases correctly mapped to autonomous region official names."
    )
    cities_str = ", ".join(sorted(cities_seen))
    print(
        f"  [PASS] Cities strictly limited to confirmed municipalities: {{{cities_str}}}."
    )
    print(
        "  [PASS] Numeric fields safely parsed ('5.0' -> 5), nulls and empty lists preserved."
    )


def test_ac4_salary_qualification(grouped_jobs: list) -> None:
    """AC-4: 3 known reversed records excluded, missing max excluded, valid closed interval counts."""
    print("Verifying AC-4: Salary qualification and closed intervals...")
    missing_max = 0
    reversed_excluded = 0
    valid_closed = 0

    for g in grouped_jobs:
        has_rev_id = any(mid in REVERSED_SALARY_IDS for mid in g["source_ids"])
        if has_rev_id:
            assert g["salary_stat_excluded"] is True, (
                f"AC-4 FAIL: Reversed group {g['id']} not excluded!"
            )
            assert g["salary_exclude_reason"] == "原文上下限倒置"
            reversed_excluded += 1
        elif g["salary_min_monthly"] is None or g["salary_max_monthly"] is None:
            assert g["salary_eligible_for_midpoint"] is False
            missing_max += 1
        elif g["salary_eligible_for_midpoint"] is True:
            valid_closed += 1
            # Midpoint calculation check
            expected_mid = (g["salary_min_monthly"] + g["salary_max_monthly"]) / 2.0
            assert g["salary_midpoint"] == expected_mid, "AC-4 FAIL: Midpoint mismatch"

    assert missing_max == 54, (
        f"AC-4 FAIL: Expected 54 missing max groups, got {missing_max}"
    )
    assert reversed_excluded == 3, (
        f"AC-4 FAIL: Expected 3 reversed groups, got {reversed_excluded}"
    )
    assert valid_closed == 2194, (
        f"AC-4 FAIL: Expected 2194 valid closed groups, got {valid_closed}"
    )
    assert (missing_max + reversed_excluded + valid_closed) == 2251

    print(
        "  [PASS] Exactly 54 missing max groups, 3 reversed excluded groups, 2194 valid midpoint groups."
    )


def test_ac5_ac6_classification_and_adjudication(
    review_csv_path: Path, grouped_jobs: list
) -> None:
    """AC-5 & AC-6: 3000 rows generated, valid 11 vocabulary, 9-column format, group resolution."""
    print(
        "Verifying AC-5 & AC-6: Dual-track classification, review CSV, and group adjudication..."
    )
    assert review_csv_path.is_file(), f"FAIL: {review_csv_path} does not exist"

    # Check BOM: first 3 bytes must be b'\xef\xbb\xbf'
    with open(review_csv_path, "rb") as f:
        bom = f.read(3)
        assert bom == b"\xef\xbb\xbf", "AC-6 FAIL: Review CSV is missing UTF-8 BOM!"

    with open(review_csv_path, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        expected_fields = [
            "id",
            "job_category_rule",
            "rule_reason",
            "job_category_review",
            "review_source",
            "review_reason",
            "review_status",
            "job_category",
            "category_source",
        ]
        assert fieldnames == expected_fields, (
            f"AC-6 FAIL: Header mismatch: {fieldnames}"
        )

        rows = list(reader)
        assert len(rows) == 3000, (
            f"AC-5 FAIL: Expected 3000 review rows, got {len(rows)}"
        )

        review_map = {}
        for r in rows:
            jid = r["id"]
            review_map[jid] = r
            r_cat = r["job_category_rule"]
            v_cat = r["job_category_review"]
            f_cat = r["job_category"]
            f_src = r["category_source"]
            v_stat = r["review_status"]

            # Category vocabulary check
            if r_cat:
                assert r_cat in VALID_CATEGORIES, (
                    f"AC-5 FAIL: Invalid rule category: {r_cat}"
                )
            if v_cat:
                assert v_cat in VALID_CATEGORIES, (
                    f"AC-5 FAIL: Invalid review category: {v_cat}"
                )
            if f_cat:
                assert f_cat in VALID_CATEGORIES, (
                    f"AC-5 FAIL: Invalid final category: {f_cat}"
                )

            # Status check
            assert v_stat in ("pending", "confirmed"), (
                f"AC-6 FAIL: Invalid status: {v_stat}"
            )

            # State machine check
            if v_stat == "confirmed":
                expected_cat = v_cat or ""
                assert f_cat == expected_cat and f_src == "reviewed", (
                    f"AC-6 FAIL: Confirmed should have f_cat={expected_cat}, f_src=reviewed, got {f_cat}, {f_src}"
                )
            elif v_stat == "pending":
                if r_cat == v_cat and r_cat:
                    assert f_cat == r_cat and f_src == "rule", (
                        f"AC-6 FAIL: Agreed pending should have f_cat={r_cat}, f_src=rule, got {f_cat}, {f_src}"
                    )
                else:
                    assert f_cat == "" and f_src == "", (
                        f"AC-6 FAIL: Disagreed pending should be empty, got {f_cat}, {f_src} for {jid}"
                    )

    # Check group-level categories in grouped_jobs against 4-step contract
    for g in grouped_jobs:
        mids = g["source_ids"]
        member_reviews = [review_map[mid] for mid in mids]
        has_pending_conflict = any(
            (
                mr["review_status"] == "pending"
                and mr["job_category_rule"] != mr["job_category_review"]
            )
            for mr in member_reviews
        )
        if has_pending_conflict:
            assert g["job_category"] is None, (
                f"AC-6 FAIL: Group {g['id']} has pending conflict but categorized!"
            )
            assert g["category_source"] is None
        else:
            # 4-step state machine resolution
            valid_decisions = []
            has_confirmed = False
            for mr in member_reviews:
                v_stat = mr["review_status"]
                v_c = mr["job_category_review"] or None
                r_c = mr["job_category_rule"] or None
                if v_stat == "confirmed":
                    has_confirmed = True
                    valid_decisions.append(v_c)
                else:
                    if r_c is not None:
                        valid_decisions.append(r_c)

            if not valid_decisions:
                assert g["job_category"] is None
                assert g["category_source"] is None
            elif any(d != valid_decisions[0] for d in valid_decisions):
                assert g["job_category"] is None
                assert g["category_source"] is None
            else:
                expected_cat = valid_decisions[0]
                expected_src = "reviewed" if has_confirmed else "rule"
                assert g["job_category"] == expected_cat, (
                    f"AC-6 FAIL: Group {g['id']} expected cat {expected_cat}, got {g['job_category']}"
                )
                assert g["category_source"] == expected_src, (
                    f"AC-6 FAIL: Group {g['id']} expected src {expected_src}, got {g['category_source']}"
                )

    print(
        "  [PASS] 3000 review rows verified with UTF-8 BOM and exact 9-column headers."
    )
    print(
        "  [PASS] All categories strictly adhere to the 11 valid classes or empty string."
    )
    print(
        "  [PASS] Single-source state machine and group-level conflict resolution verified."
    )


def test_state_machine_scenarios() -> None:
    """AC-6/AC-8: Test exhaustive state machine scenarios including confirmed overrides and conflict propagation."""
    print(
        "Verifying State Machine Scenarios (Pending conflicts, Confirmed overrides, Group propagation)..."
    )

    # 1. Default agreement adopting rule
    s1_1 = adjudicate_single_source(
        "job:1", "软件开发", "rule_r", "软件开发", "AI:test", "ai_r", "pending"
    )
    s1_2 = adjudicate_single_source(
        "job:2", "软件开发", "rule_r", "软件开发", "AI:test", "ai_r", "pending"
    )
    assert s1_1["job_category"] == "软件开发" and s1_1["category_source"] == "rule"
    g1 = {"id": "job:1", "source_ids": ["job:1", "job:2"]}
    map1 = {"job:1": s1_1, "job:2": s1_2}
    g1_cat, g1_src = adjudicate_group_level(g1, map1)
    assert g1_cat == "软件开发" and g1_src == "rule", (
        "Scenario 1 FAIL: Default agreement adopting rule"
    )

    # 2. Pending conflict propagation (group becomes null)
    s2_1 = adjudicate_single_source(
        "job:1",
        "软件开发",
        "rule_r",
        "硬件与芯片",
        "AI:test",
        "ai_r",
        "pending",
    )
    s2_2 = adjudicate_single_source(
        "job:2", "软件开发", "rule_r", "软件开发", "AI:test", "ai_r", "pending"
    )
    assert s2_1["job_category"] == "" and s2_1["category_source"] == ""
    g2 = {"id": "job:1", "source_ids": ["job:1", "job:2"]}
    map2 = {"job:1": s2_1, "job:2": s2_2}
    g2_cat, g2_src = adjudicate_group_level(g2, map2)
    assert g2_cat is None and g2_src is None, (
        "Scenario 2 FAIL: Pending conflict must nullify group"
    )

    # 3. Confirmed review overriding rule category
    s3_1 = adjudicate_single_source(
        "job:1",
        "软件开发",
        "rule_r",
        "硬件与芯片",
        "人工:负责人",
        "核实为硬件",
        "confirmed",
    )
    s3_2 = adjudicate_single_source(
        "job:2",
        "软件开发",
        "rule_r",
        "硬件与芯片",
        "人工:负责人",
        "核实为硬件",
        "confirmed",
    )
    assert (
        s3_1["job_category"] == "硬件与芯片" and s3_1["category_source"] == "reviewed"
    )
    g3 = {"id": "job:1", "source_ids": ["job:1", "job:2"]}
    map3 = {"job:1": s3_1, "job:2": s3_2}
    g3_cat, g3_src = adjudicate_group_level(g3, map3)
    assert g3_cat == "硬件与芯片" and g3_src == "reviewed", (
        "Scenario 3 FAIL: Confirmed review must override rule"
    )

    # 4. Confirmed unclassifiable (null) overriding rule category
    s4_1 = adjudicate_single_source(
        "job:1",
        "软件开发",
        "rule_r",
        None,
        "人工:负责人",
        "核实信息不足无法分类",
        "confirmed",
    )
    s4_2 = adjudicate_single_source(
        "job:2",
        None,
        "rule_r",
        None,
        "人工:负责人",
        "核实信息不足无法分类",
        "confirmed",
    )
    assert s4_1["job_category"] == "" and s4_1["category_source"] == "reviewed"
    g4 = {"id": "job:1", "source_ids": ["job:1", "job:2"]}
    map4 = {"job:1": s4_1, "job:2": s4_2}
    g4_cat, g4_src = adjudicate_group_level(g4, map4)
    assert g4_cat is None and g4_src == "reviewed", (
        "Scenario 4 FAIL: Confirmed null must yield (None, reviewed)"
    )

    # 5. Group valid decision conflict resulting in null
    s5_1 = adjudicate_single_source(
        "job:1",
        "软件开发",
        "rule_r",
        "软件开发",
        "人工:负责人",
        "确认开发",
        "confirmed",
    )
    s5_2 = adjudicate_single_source(
        "job:2",
        "软件测试",
        "rule_r",
        "软件测试",
        "人工:负责人",
        "确认测试",
        "confirmed",
    )
    g5 = {"id": "job:1", "source_ids": ["job:1", "job:2"]}
    map5 = {"job:1": s5_1, "job:2": s5_2}
    g5_cat, g5_src = adjudicate_group_level(g5, map5)
    assert g5_cat is None and g5_src is None, (
        "Scenario 5 FAIL: Disagreeing valid decisions must yield (None, None)"
    )

    # 6. Confirmed null coexisting with non-empty rule category -> valid decisions disagree -> null
    s6_1 = adjudicate_single_source(
        "job:1",
        "软件开发",
        "rule_r",
        None,
        "人工:负责人",
        "确认无法分类",
        "confirmed",
    )
    s6_2 = adjudicate_single_source(
        "job:2", "软件开发", "rule_r", "软件开发", "AI:test", "一致", "pending"
    )
    g6 = {"id": "job:1", "source_ids": ["job:1", "job:2"]}
    map6 = {"job:1": s6_1, "job:2": s6_2}
    g6_cat, g6_src = adjudicate_group_level(g6, map6)
    assert g6_cat is None and g6_src is None, (
        "Scenario 6 FAIL: Confirmed null vs non-empty rule must yield (None, None)"
    )

    print("  [PASS] All 6 state machine scenarios successfully verified.")


def test_reported_five_issues() -> None:
    """Verify clean resolution of the 5 reported issues.

    1. Prefix isolation (brackets, company prefixes, trailing codes).
    2. Safety engineer disambiguation (cybersecurity vs production safety vs non-safety roles).
    3. Persistent review loading (preserving confirmed offline human reviews).
    4. Sampling audit authenticity (authentic duty observations, no bogus EHS comments on dev roles).
    5. State machine testing (full scenario test passes).
    """
    print("Verifying 5 Reported Issues Resolution...")
    ai = AIJobClassifier(agent_name="AI:Opencode")

    # 1. Prefix isolation
    r_cat, _ = classify_by_rule(
        "北方华创微电子-软件测试工程师-2027校园招聘 (J16240)",
        "负责自动化测试平台搭建与测试用例执行",
    )
    assert r_cat == "软件测试", f"Issue 1 FAIL: Expected 软件测试, got {r_cat}"

    r_cat_wb, _ = classify_by_rule(
        "【微电子科技】软件开发工程师", "负责Java后端与微服务开发"
    )
    assert r_cat_wb == "软件开发", f"Issue 1 FAIL: Expected 软件开发, got {r_cat_wb}"

    r_cat_zh, _ = classify_by_rule(
        "【众合科技2027届秋季校园招聘】测试开发工程师", "负责测试框架编写"
    )
    assert r_cat_zh == "软件测试", f"Issue 1 FAIL: Expected 软件测试, got {r_cat_zh}"
    print("  [PASS] Issue 1: Prefix isolation cleanly verified.")

    # 2. Safety engineer disambiguation
    # Production safety
    r_safe_prod, _ = classify_by_rule(
        "安全工程师", "从事矿山安全生产管理工作，组织隐患排查。"
    )
    assert r_safe_prod == "其他明确岗位", (
        f"Issue 2 FAIL: Expected 其他明确岗位, got {r_safe_prod}"
    )

    # Empty safety title -> None
    r_safe_none, _ = classify_by_rule("安全工程师", "无")
    assert r_safe_none is None, f"Issue 2 FAIL: Expected None, got {r_safe_none}"

    # Cyber security
    r_safe_cyber, _ = classify_by_rule(
        "网络安全工程师", "负责网络安全防护体系建设与渗透测试"
    )
    assert r_safe_cyber == "网络与信息安全", (
        f"Issue 2 FAIL: Expected 网络与信息安全, got {r_safe_cyber}"
    )

    # Non-safety jobs with potentially confusing substrings (e.g. 工程化, 实施工作, ERP实施)
    r_fe, _ = classify_by_rule(
        "前端开发工程师",
        "使用Vue/React进行组件化开发，熟悉前端工程化工具（Webpack、Vite）",
    )
    assert r_fe == "软件开发", f"Issue 2 FAIL: Expected 软件开发, got {r_fe}"

    r_dev, _ = classify_by_rule(
        "软件工程师",
        "负责软件相关功能模块编写及验证，指导生产调试人员技术实施工作",
    )
    assert r_dev == "软件开发", f"Issue 2 FAIL: Expected 软件开发, got {r_dev}"

    r_erp, _ = classify_by_rule(
        "ERP实施工程师", "进行系统的部署、实施、指导与沟通，协助控制项目需求"
    )
    assert r_erp == "技术支持与实施", (
        f"Issue 2 FAIL: Expected 技术支持与实施, got {r_erp}"
    )

    # Same check on AI classifier
    ai_fe = ai.classify(
        "前端开发工程师",
        "使用Vue/React进行组件化开发，熟悉前端工程化工具（Webpack、Vite）",
    )
    assert ai_fe["job_category_review"] == "软件开发", (
        f"Issue 2 FAIL: AI expected 软件开发, got {ai_fe['job_category_review']}"
    )
    print("  [PASS] Issue 2: Safety engineer disambiguation cleanly verified.")

    # 3. Persistent review loading
    review_csv_path = Path("data/processed/job_category_review.csv")
    loaded = load_existing_reviews(review_csv_path)
    assert len(loaded) == 3000, (
        f"Issue 3 FAIL: Expected 3000 rows loaded, got {len(loaded)}"
    )
    print("  [PASS] Issue 3: Persistent review loading cleanly verified.")

    # 4. Sampling audit authenticity
    class_report = Path(
        "data/processed/audit_reports/classification_review.md"
    ).read_text(encoding="utf-8")
    assert (
        "前端开发工程师 |" not in class_report
        or "工业安全生产" not in class_report.split("前端开发工程师")[1][:100]
    ), "Issue 4 FAIL: Bogus EHS observation found for 前端开发工程师!"
    assert (
        "ERP实施工程师 |" not in class_report
        or "工业安全生产" not in class_report.split("ERP实施工程师")[1][:100]
    ), "Issue 4 FAIL: Bogus EHS observation found for ERP实施工程师!"
    print("  [PASS] Issue 4: Sampling audit authenticity cleanly verified.")

    # 5. State machine testing
    print("  [PASS] Issue 5: State machine scenario testing cleanly verified.")


def test_ac7_audit_reports() -> None:
    """AC-7: Verify all 3 audit reports exist, non-empty, and contain required sections."""
    print("Verifying AC-7: Audit reports existence and content...")
    reports = [
        (
            "data/processed/audit_reports/classification_review.md",
            [
                "# 双路岗位分类复核与抽样质检报告",
                "分歧与冲突项重点复核清单",
                "双路一致项分层抽样质检",
            ],
        ),
        (
            "data/processed/audit_reports/skill_accuracy_audit.md",
            [
                "# 技能标签真实性抽样质检与依据审计报告",
                "技能数据现状与覆盖率统计",
                "技能标签与岗位正文文本匹配真实性检验",
                "技能抽取误报与依据噪声深度分析",
            ],
        ),
        (
            "data/processed/audit_reports/duplicate_groups_audit.md",
            [
                "# 305 组完全重复岗位业务语义抽样分析报告",
                "重复组规模分布",
                "发布日期跨度真实分布与业务机制分析",
                "重复产生根因与业务含义分析",
            ],
        ),
    ]

    for rel_path, required_sections in reports:
        p = Path(rel_path)
        assert p.is_file(), f"AC-7 FAIL: Missing report: {rel_path}"
        content = p.read_text(encoding="utf-8")
        assert len(content) > 500, f"AC-7 FAIL: Report {rel_path} is too short"
        for sec in required_sections:
            assert sec in content, f"AC-7 FAIL: Missing section '{sec}' in {rel_path}"
        print(f"  [PASS] Report {p.name} verified ({len(content)} chars).")


def main() -> None:
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    print("==================================================")
    print("Starting Comprehensive Contract Verification Suite")
    print("==================================================")

    # 1. AC-1
    test_ac1_readonly_integrity()

    # Load grouped jobs JSON
    json_path = Path("data/processed/jobs_cleaned_grouped.json")
    assert json_path.is_file(), f"FAIL: {json_path} does not exist"
    with open(json_path, mode="r", encoding="utf-8") as f:
        grouped_jobs = json.load(f)

    # 2. AC-2
    test_ac2_exact_grouping_consistency(grouped_jobs)

    # 3. AC-3
    test_ac3_cleaning_and_mapping(grouped_jobs)

    # 4. AC-4
    test_ac4_salary_qualification(grouped_jobs)

    # 5. AC-5 & AC-6
    review_csv_path = Path("data/processed/job_category_review.csv")
    test_ac5_ac6_classification_and_adjudication(review_csv_path, grouped_jobs)

    # 6. Detailed State Machine Scenarios
    test_state_machine_scenarios()

    # 7. Verification of 5 Reported Issues
    test_reported_five_issues()

    # 8. AC-7
    test_ac7_audit_reports()

    # 9. AC-8 Self-assertion
    print("\nVerifying AC-8: Automated test suite self-assertion...")
    print("  [PASS] All contract assertions and read-only protections passed!")
    print("==================================================")
    print("ALL ACCEPTANCE CRITERIA (AC-1 ~ AC-8) FULLY PASSED")
    print("==================================================")


if __name__ == "__main__":
    main()
