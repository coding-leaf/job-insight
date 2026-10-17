"""Data cleaning and 19-column exact grouping module.

Performs exact 19-column grouping prior to any normalization, verifies counts,
unions skills provenance, cleans numeric and string values, normalizes province names,
and flags salary statistical eligibility.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Constants
REVERSED_SALARY_IDS: Set[str] = {
    "ncss:Am6VEAbf4rZZ4mwyaKuHBe",
    "ncss:DBvsD7jVecfg3YmmnLaSHo",
    "ncss:gmFNdf4Ef3TeSbWzfEeon",
}

EXPECTED_HASHES: Dict[str, str] = {
    "jobs_clean_final.csv": "9115d09875b3b11b2b2af584e45023ac95d6955f37b6d33b9b777a84b8a84a00",
    "skills.csv": "937b05c9791ad9e75228dfe5ad5994c140f4cf06c93f26c1492190a7b9d3133c",
    "job_skills.csv": "f95e85e77ebb77321868587931dac2e0bbb5a2a6bd3bab37ef503b0c8cda528e",
}

PROVINCE_MAPPING: Dict[str, str] = {
    "广西省": "广西壮族自治区",
    "内蒙古省": "内蒙古自治区",
    "新疆省": "新疆维吾尔自治区",
    "西藏省": "西藏自治区",
}


def compute_file_sha256(path: Path | str) -> str:
    """Compute SHA-256 of a file in binary mode without modifying it."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def find_data_file(filename: str, base_dir: Optional[Path] = None) -> Path:
    """Locate an input file from possible relative directory layouts."""
    candidates = [
        Path(f"../清洗后数据/{filename}"),
        Path(f"../../清洗后数据/{filename}"),
        Path(__file__).resolve().parents[2] / "清洗后数据" / filename,
        Path(__file__).resolve().parents[3] / "清洗后数据" / filename,
    ]
    if base_dir:
        candidates.insert(0, base_dir / filename)

    for p in candidates:
        if p.is_file():
            return p.resolve()
    raise FileNotFoundError(
        f"Cannot find input file: {filename} in candidates: {candidates}"
    )


def parse_numeric(val_str: Optional[str]) -> Optional[int | float]:
    """Parse numeric values safely, e.g. '5.0' -> 5, '8.0' -> 8."""
    if val_str is None or not val_str.strip():
        return None
    val_str = val_str.strip()
    try:
        f = float(val_str)
        if f.is_integer():
            return int(f)
        return f
    except ValueError:
        raise ValueError(f"Failed to parse numeric string: {val_str!r}")


def clean_string(val_str: Optional[str]) -> Optional[str]:
    """Map empty strings to None (null in JSON). Keep non-empty strings as-is."""
    if val_str is None or val_str == "":
        return None
    return val_str


def load_raw_data() -> Tuple[List[Dict[str, str]], List[str], List[Dict[str, str]]]:
    """Load the 3 read-only source CSV files, validating their hashes first."""
    jobs_path = find_data_file("jobs_clean_final.csv")
    skills_path = find_data_file("skills.csv")
    job_skills_path = find_data_file("job_skills.csv")

    # Verify hashes
    for name, path in [
        ("jobs_clean_final.csv", jobs_path),
        ("skills.csv", skills_path),
        ("job_skills.csv", job_skills_path),
    ]:
        actual_hash = compute_file_sha256(path)
        expected_hash = EXPECTED_HASHES[name]
        if actual_hash != expected_hash:
            raise ValueError(
                f"Hash mismatch for {name}: expected {expected_hash}, got {actual_hash}"
            )

    # Read jobs_clean_final.csv
    with open(jobs_path, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        jobs_rows = list(reader)

    # Read skills.csv
    with open(skills_path, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        skills = [r["skill_name"] for r in reader]

    # Read job_skills.csv
    with open(job_skills_path, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        job_skills_rows = list(reader)

    return jobs_rows, skills, job_skills_rows


def process_cleaning_and_grouping() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Execute 19-column exact grouping, skills union, field projection, and salary qualification.

    Returns:
        grouped_jobs: List of 2251 grouped job dicts.
        stats: Dictionary containing validation statistics.
    """
    jobs_rows, valid_skills, job_skills_rows = load_raw_data()

    # Build skills map by job_id
    valid_skill_set = set(valid_skills)
    job_skills_map: Dict[str, List[Dict[str, Any]]] = {}
    for r in job_skills_rows:
        job_id = r["job_id"]
        skill_name = r["skill_name"]
        if skill_name not in valid_skill_set:
            raise ValueError(f"Dangling skill name: {skill_name} for job {job_id}")
        origin = clean_string(r.get("origin"))
        evidence = clean_string(r.get("evidence"))
        job_skills_map.setdefault(job_id, []).append(
            {
                "skill_name": skill_name,
                "origin": origin,
                "evidence": evidence,
            }
        )

    # The 19 columns for exact grouping (all columns except id and source_url)
    group_col_names = [
        "published_at",
        "title",
        "company",
        "company_type",
        "company_size",
        "work_location",
        "province",
        "city",
        "salary_display",
        "salary_min_monthly",
        "salary_max_monthly",
        "education_requirement",
        "education_min_code",
        "experience_requirement",
        "experience_min_years",
        "experience_status",
        "major_requirement",
        "description",
        "recruitment_headcount",
    ]

    # Perform exact grouping on raw decoded string tuple
    groups_dict: Dict[Tuple[str, ...], List[Dict[str, str]]] = {}
    for row in jobs_rows:
        key = tuple(row[col] for col in group_col_names)
        groups_dict.setdefault(key, []).append(row)

    total_groups = len(groups_dict)
    multi_record_groups = [g for g in groups_dict.values() if len(g) > 1]
    excess_records = sum(len(g) - 1 for g in multi_record_groups)

    if total_groups != 2251:
        raise ValueError(f"Expected 2251 groups, got {total_groups}")
    if len(multi_record_groups) != 305:
        raise ValueError(
            f"Expected 305 multi-record groups, got {len(multi_record_groups)}"
        )
    if excess_records != 749:
        raise ValueError(f"Expected 749 excess records, got {excess_records}")

    grouped_jobs: List[Dict[str, Any]] = []

    # Process each group
    for raw_key, members in groups_dict.items():
        # Representative ID: lexicographically smallest original string ID
        member_ids = [m["id"] for m in members]
        source_ids = sorted(list(set(member_ids)))
        rep_id = min(source_ids)
        rep_row = next(m for m in members if m["id"] == rep_id)

        # Union skills across all group members
        skills_dict: Dict[str, List[Dict[str, Optional[str]]]] = {}
        for mid in source_ids:
            for s in job_skills_map.get(mid, []):
                sname = s["skill_name"]
                skills_dict.setdefault(sname, []).append(
                    {
                        "origin": s["origin"],
                        "evidence": s["evidence"],
                    }
                )

        # De-duplicate provenance pairs and sort
        formatted_skills = []
        for sname in sorted(skills_dict.keys()):
            raw_provs = skills_dict[sname]
            # De-duplicate
            unique_provs = []
            seen_pairs = set()
            for p in raw_provs:
                pair_key = (p["origin"], p["evidence"])
                if pair_key not in seen_pairs:
                    seen_pairs.add(pair_key)
                    unique_provs.append(p)
            # Sort provenance: null/empty first, then lexicographically
            unique_provs.sort(
                key=lambda p: (
                    0 if p["origin"] is None else 1,
                    p["origin"] or "",
                    0 if p["evidence"] is None else 1,
                    p["evidence"] or "",
                )
            )
            formatted_skills.append(
                {
                    "skill_name": sname,
                    "provenance": unique_provs,
                }
            )

        # Field projection & normalization
        raw_province = clean_string(rep_row["province"])
        norm_province = (
            PROVINCE_MAPPING.get(raw_province, raw_province) if raw_province else None
        )

        salary_min = parse_numeric(rep_row["salary_min_monthly"])
        salary_max = parse_numeric(rep_row["salary_max_monthly"])
        salary_display = clean_string(rep_row["salary_display"])

        # Check reversed salary exclusion
        has_reversed_id = any(mid in REVERSED_SALARY_IDS for mid in source_ids)

        salary_stat_excluded = False
        salary_eligible_for_midpoint = False
        salary_midpoint = None
        salary_exclude_reason = None

        if has_reversed_id:
            salary_stat_excluded = True
            salary_exclude_reason = "原文上下限倒置"
        elif salary_min is None or salary_max is None:
            salary_stat_excluded = False
            salary_exclude_reason = "缺少上限或下限"
        elif salary_min <= 0 or salary_max <= 0 or salary_min > salary_max:
            salary_stat_excluded = True
            salary_exclude_reason = "数值上下限倒置或非正数"
        else:
            salary_eligible_for_midpoint = True
            salary_midpoint = (float(salary_min) + float(salary_max)) / 2.0

        group_doc = {
            "id": rep_id,
            "source_ids": source_ids,
            "source_url": rep_row["source_url"],
            "published_at": clean_string(rep_row["published_at"]),
            "title": rep_row["title"],
            "company": clean_string(rep_row["company"]),
            "company_type": clean_string(rep_row["company_type"]),
            "company_size": clean_string(rep_row["company_size"]),
            "work_location": clean_string(rep_row["work_location"]),
            "province": norm_province,
            "city": clean_string(rep_row["city"]),
            "salary_display": salary_display,
            "salary_min_monthly": salary_min,
            "salary_max_monthly": salary_max,
            "salary_eligible_for_midpoint": salary_eligible_for_midpoint,
            "salary_midpoint": salary_midpoint,
            "salary_stat_excluded": salary_stat_excluded,
            "salary_exclude_reason": salary_exclude_reason,
            "education_requirement": clean_string(rep_row["education_requirement"]),
            "education_min_code": parse_numeric(rep_row["education_min_code"]),
            "experience_requirement": clean_string(rep_row["experience_requirement"]),
            "experience_min_years": parse_numeric(rep_row["experience_min_years"]),
            "experience_status": clean_string(rep_row["experience_status"]),
            "major_requirement": clean_string(rep_row["major_requirement"]),
            "description": clean_string(rep_row["description"]),
            "recruitment_headcount": parse_numeric(rep_row["recruitment_headcount"]),
            "skills": formatted_skills,
            "job_category": None,
            "category_source": None,
        }
        grouped_jobs.append(group_doc)

    # Sort grouped jobs by id ascending for stability
    grouped_jobs.sort(key=lambda x: x["id"])

    stats = {
        "total_source_records": len(jobs_rows),
        "total_groups": total_groups,
        "multi_record_groups": len(multi_record_groups),
        "excess_records": excess_records,
        "groups_with_skills": sum(1 for g in grouped_jobs if len(g["skills"]) > 0),
        "valid_salary_groups": sum(
            1 for g in grouped_jobs if g["salary_eligible_for_midpoint"]
        ),
        "missing_max_salary_groups": sum(
            1 for g in grouped_jobs if g["salary_exclude_reason"] == "缺少上限或下限"
        ),
        "reversed_salary_groups": sum(
            1 for g in grouped_jobs if g["salary_exclude_reason"] == "原文上下限倒置"
        ),
    }

    return grouped_jobs, stats


if __name__ == "__main__":
    jobs, stats = process_cleaning_and_grouping()
    print("Clean and group completed:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
