"""Job Category Adjudication Module.

Resolves single-source job categories based on the dual-track state machine
and computes unanimous group-level categories following docs/job-classification.md.
Exports the standard UTF-8 BOM 9-column review snapshot CSV.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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


def load_existing_reviews(csv_path: Path | str) -> Dict[str, Dict[str, str]]:
    """Load existing review CSV if it exists, preserving confirmed human reviews."""
    p = Path(csv_path)
    if not p.is_file():
        return {}

    existing: Dict[str, Dict[str, str]] = {}
    with open(p, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            jid = row.get("id")
            if jid:
                existing[jid] = row
    return existing


def adjudicate_single_source(
    job_id: str,
    rule_category: Optional[str],
    rule_reason: str,
    review_category: Optional[str],
    review_source: Optional[str] = "",
    review_reason: Optional[str] = "",
    review_status: Optional[str] = "pending",
) -> Dict[str, Optional[str]]:
    """Determine single-source final category and category source based on state machine."""
    rev_src = review_source or ""
    rev_rsn = review_reason or ""
    status = review_status or "pending"

    # Validate categories if non-empty
    if rule_category and rule_category not in VALID_CATEGORIES:
        raise ValueError(f"Invalid rule category: {rule_category} for {job_id}")
    if review_category and review_category not in VALID_CATEGORIES:
        raise ValueError(f"Invalid review category: {review_category} for {job_id}")
    if status not in ("pending", "confirmed"):
        raise ValueError(f"Invalid review status: {status} for {job_id}")

    final_cat: Optional[str] = None
    final_src: Optional[str] = None

    if status == "confirmed":
        # Confirmed proposal overrides old rule
        final_cat = review_category
        final_src = "reviewed"
    elif not rev_src and not rev_rsn:
        # No review proposal
        if rule_category:
            final_cat = rule_category
            final_src = "rule"
        else:
            final_cat = None
            final_src = None
    else:
        # Pending review proposal
        if rule_category == review_category:
            if rule_category is not None:
                final_cat = rule_category
                final_src = "rule"
            else:
                final_cat = None
                final_src = None
        else:
            # Conflict or one empty -> unresolved conflict
            final_cat = None
            final_src = None

    return {
        "id": job_id,
        "job_category_rule": rule_category or "",
        "rule_reason": rule_reason or "",
        "job_category_review": review_category or "",
        "review_source": rev_src,
        "review_reason": rev_rsn,
        "review_status": status,
        "job_category": final_cat or "",
        "category_source": final_src or "",
    }


def adjudicate_group_level(
    group: Dict[str, Any],
    source_records_map: Dict[str, Dict[str, Optional[str]]],
) -> Tuple[Optional[str], Optional[str]]:
    """Resolve group-level category according to Section 4 of docs/job-classification.md.

    1. Any member has pending conflict between rule and review -> (None, None).
    2. Collect valid decisions: confirmed proposals (including confirmed null),
       plus non-empty rule categories from remaining members.
    3. If valid decisions disagree (including null vs class) -> (None, None).
    4. If all valid decisions agree -> adopt that value. If any confirmed decision
       exists, category_source="reviewed", otherwise "rule". If no valid decisions, (None, None).
    """
    member_ids = group["source_ids"]
    member_records = [source_records_map[mid] for mid in member_ids]

    # Step 1: Check if any member has pending disagreement between rule and review
    for rec in member_records:
        r_cat = rec.get("job_category_rule") or None
        v_cat = rec.get("job_category_review") or None
        v_status = rec.get("review_status") or "pending"
        v_src = rec.get("review_source") or ""
        v_rsn = rec.get("review_reason") or ""

        has_proposal = bool(v_src or v_rsn)
        if v_status == "pending":
            if has_proposal:
                if r_cat != v_cat:
                    # Unresolved pending conflict
                    return None, None
            else:
                # No proposal: r_cat is unreviewed, no conflict
                pass

    # Step 2: Collect valid decisions: confirmed proposals (including None),
    # and non-empty rule categories from remaining members
    valid_decisions: List[Optional[str]] = []
    has_confirmed = False

    for rec in member_records:
        v_status = rec.get("review_status") or "pending"
        v_cat = rec.get("job_category_review") or None
        r_cat = rec.get("job_category_rule") or None

        if v_status == "confirmed":
            has_confirmed = True
            valid_decisions.append(v_cat)
        else:
            # Remaining members: non-empty rule category
            if r_cat is not None:
                valid_decisions.append(r_cat)

    # Step 3: Check consistency of valid decisions
    if not valid_decisions:
        return None, None

    first_decision = valid_decisions[0]
    if any(d != first_decision for d in valid_decisions):
        return None, None

    # Step 4: Unanimous decision
    category_source = "reviewed" if has_confirmed else "rule"
    return first_decision, category_source


def export_review_csv(
    review_records: List[Dict[str, Optional[str]]],
    output_path: Path | str,
) -> None:
    """Export standard UTF-8 BOM 9-column CSV for offline review."""
    fieldnames = [
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

    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    with open(out_p, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in review_records:
            clean_row = {k: (r.get(k) or "") for k in fieldnames}
            writer.writerow(clean_row)
