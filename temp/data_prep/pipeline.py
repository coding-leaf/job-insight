"""End-to-End Data Preparation and Classification Pipeline.

Coordinates:
1. Exact 19-column grouping & data cleaning (clean_and_group)
2. Dual-track classification (rule_classifier & ai_classifier)
3. Single-source & group-level adjudication (category_adjudicator)
4. Export of jobs_cleaned_grouped.json and job_category_review.csv
5. Sampling audit reports generation (sampling_audit)
"""

from __future__ import annotations

import argparse
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
        export_review_csv,
        load_existing_reviews,
    )
    from temp.data_prep.clean_and_group import (  # noqa: E402
        load_raw_data,
        process_cleaning_and_grouping,
    )
    from temp.data_prep.rule_classifier import classify_by_rule  # noqa: E402
    from temp.data_prep.sampling_audit import (  # noqa: E402
        generate_classification_review_report,
        generate_duplicate_groups_audit_report,
        generate_skill_accuracy_audit_report,
    )
except ImportError:
    from ai_classifier import AIJobClassifier  # type: ignore # noqa: E402
    from category_adjudicator import (  # type: ignore # noqa: E402
        adjudicate_group_level,
        adjudicate_single_source,
        export_review_csv,
        load_existing_reviews,
    )
    from clean_and_group import (  # type: ignore # noqa: E402
        load_raw_data,
        process_cleaning_and_grouping,
    )
    from rule_classifier import classify_by_rule  # type: ignore # noqa: E402
    from sampling_audit import (  # type: ignore # noqa: E402
        generate_classification_review_report,
        generate_duplicate_groups_audit_report,
        generate_skill_accuracy_audit_report,
    )


def run_pipeline(fresh: bool = False) -> None:
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    print("=== Step 1: Loading raw data and executing 19-column exact grouping ===")
    source_records, valid_skills, job_skills_records = load_raw_data()
    grouped_jobs, grouping_stats = process_cleaning_and_grouping()
    print(
        f"Grouped {grouping_stats['total_source_records']} records into {grouping_stats['total_groups']} groups."
    )
    print(
        f"Multi-record groups: {grouping_stats['multi_record_groups']}, excess records: {grouping_stats['excess_records']}."
    )
    print(
        f"Groups with skills: {grouping_stats['groups_with_skills']}, valid closed salary groups: {grouping_stats['valid_salary_groups']}."
    )

    print("\n=== Step 2: Running dual-track classification (Rule + Independent AI) ===")
    review_csv_path = Path("data/processed/job_category_review.csv")
    existing_reviews = {}
    if not fresh and review_csv_path.is_file():
        existing_reviews = load_existing_reviews(review_csv_path)
        confirmed_count = sum(
            1
            for r in existing_reviews.values()
            if r.get("review_status") == "confirmed"
        )
        print(
            f"Loaded {len(existing_reviews)} existing reviews ({confirmed_count} confirmed preserved)."
        )

    ai_classifier = AIJobClassifier(agent_name="AI:Opencode")
    review_records = []
    source_review_map = {}
    preserved_confirmed = 0

    for row in source_records:
        jid = row["id"]
        t = row["title"]
        d = row["description"]
        m = row["major_requirement"]

        # Rule classifier
        r_cat, r_reason = classify_by_rule(t, d, m)

        # Check existing confirmed review
        existing = existing_reviews.get(jid)
        if existing and existing.get("review_status") == "confirmed":
            v_cat = existing.get("job_category_review") or None
            v_src = existing.get("review_source") or ""
            v_reason = existing.get("review_reason") or ""
            v_status = "confirmed"
            preserved_confirmed += 1
        else:
            # AI classifier
            ai_res = ai_classifier.classify(t, d, m)
            v_cat = ai_res["job_category_review"]
            v_src = ai_res["review_source"]
            v_reason = ai_res["review_reason"]
            v_status = ai_res["review_status"]

        # Adjudicate single source
        adj = adjudicate_single_source(
            job_id=jid,
            rule_category=r_cat,
            rule_reason=r_reason,
            review_category=v_cat,
            review_source=v_src,
            review_reason=v_reason,
            review_status=v_status,
        )
        review_records.append(adj)
        source_review_map[jid] = adj

    # Export review CSV (UTF-8 BOM, 9 columns)
    export_review_csv(review_records, review_csv_path)
    print(
        f"Exported offline review snapshot to {review_csv_path} (3000 rows, 9 columns, UTF-8 BOM, {preserved_confirmed} confirmed preserved)."
    )

    print("\n=== Step 3: Resolving group-level categories ===")
    classified_groups = 0
    unclassified_groups = 0

    for group in grouped_jobs:
        g_cat, g_src = adjudicate_group_level(group, source_review_map)
        group["job_category"] = g_cat
        group["category_source"] = g_src
        if g_cat is not None:
            classified_groups += 1
        else:
            unclassified_groups += 1

    # Export grouped jobs JSON
    grouped_json_path = Path("data/processed/jobs_cleaned_grouped.json")
    grouped_json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(grouped_json_path, "w", encoding="utf-8") as f:
        json.dump(grouped_jobs, f, ensure_ascii=False, indent=2)
    print(f"Exported grouped jobs to {grouped_json_path} ({len(grouped_jobs)} groups).")
    print(
        f"Group classification status: {classified_groups} categorized, {unclassified_groups} unclassified (null)."
    )

    print("\n=== Step 4: Generating sampling audit and quality inspection reports ===")
    reports_dir = Path("data/processed/audit_reports")

    # 1. classification_review.md
    class_review_path = reports_dir / "classification_review.md"
    generate_classification_review_report(
        source_records, review_records, class_review_path
    )
    print(f"Generated {class_review_path}.")

    # 2. skill_accuracy_audit.md
    skill_audit_path = reports_dir / "skill_accuracy_audit.md"
    generate_skill_accuracy_audit_report(
        source_records, job_skills_records, grouped_jobs, skill_audit_path
    )
    print(f"Generated {skill_audit_path}.")

    # 3. duplicate_groups_audit.md
    dup_audit_path = reports_dir / "duplicate_groups_audit.md"
    generate_duplicate_groups_audit_report(source_records, grouped_jobs, dup_audit_path)
    print(f"Generated {dup_audit_path}.")

    print("\n=== Pipeline execution completed successfully ===")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run JobInsight Data Prep Pipeline")
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Regenerate all review records from scratch without preserving confirmed reviews",
    )
    args = parser.parse_args()
    run_pipeline(fresh=args.fresh)
