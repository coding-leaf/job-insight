# JobInsight Data Contract

Status: active contract; implementation state reviewed on 2026-10-20. The preparation pipeline exists in `temp/data_prep/`, with local artifacts under `data/processed/` and application read paths under `backend/app/`. The earlier 2026-10-18 preparation verification is historical; the current [project review](../../../docs/review/2026-10-20_203614_project-review.md) distinguishes implemented behavior, unresolved contract differences and checks actually run.

## 1. Scope / Trigger

Read this contract before importing recruitment data, projecting job documents, classifying jobs, adding filters or aggregating salary/skills. The Chinese implementation references are authoritative for details:

- [Field dictionary](../../../docs/data-dictionary.md)
- [Classification and offline review](../../../docs/job-classification.md)
- [Statistical methodology](../../../docs/statistical-methodology.md)
- [Preparation checklist](../../../docs/data-preparation-checklist.md)

Do not treat the historical handoff or raw cache column names as proof that industry, city or job category has been correctly extracted. Do not expand this contract into an application architecture decision.

## 2. Signatures / Data Boundaries

No public API or database signature is introduced by this contract document. The processing boundary is:

```text
jobs_clean_final.csv + skills.csv + job_skills.csv
    -> source records and exact duplicate groups
    -> normalized fields, skills provenance, category projection
    -> filtered job groups
    -> list totals/pagination and salary/skill/education aggregates
```

The field dictionary owns the input and projection shapes. The classification document owns the offline review columns, category vocabulary, status combinations and group resolution. Preparation, repository and API implementations now exist; these normative definitions do not imply that every implementation path has been verified against them.

## 3. Contracts

- Preserve all 21 input columns and original files; source IDs remain stable. Blank source cells become `null`; no linked skills become `[]`. Parse integral numeric strings such as `5.0` as validated numbers, not with direct string-to-integer conversion.
- Group on the original decoded strings in the 19 source columns other than `id` and `source_url`, before normalization or classification. Skills and review records are excluded from the key. Retain all source IDs and select the lexicographically smallest ID as representative.
- Merge skills by name while retaining distinct source/evidence pairs. Do not interpret a source tag equal to its evidence text as verified description evidence.
- Use one group-level category resolved under the classification contract. Rules and offline human/AI proposals remain separate; AI output does not imply confirmed review. Pending disagreements and conflicting confirmed reviews cannot be hidden by the representative row.
- Normalize explicit province aliases; never infer a city from a province. Keep original work location for traceability.
- Use finite positive closed salary intervals with ordered bounds to derive midpoints. Exclude known reversed display intervals; do not silently replace clean values with raw-cache values. Other unresolved salary-source differences remain disclosed.
- Filter final groups before pagination and aggregation. Salary medians, skill denominators and counts use those groups without multiplying records by skill links. Five salary-eligible groups is a display threshold, not a significance guarantee.
- Skill annotation ratio uses all matching groups as denominator; show annotation coverage. Education groups describe job requirements, not effects on individual earnings. Empty-set behavior and labels follow the methodology document.

## 4. Validation & Error Matrix

| Input / state | Required boundary behavior |
| --- | --- |
| Missing/duplicate source ID or dangling skill/review ID | Reject the proposed import/review batch; report file, row and ID; do not overwrite accepted data |
| Missing optional field / no skill links | Keep `null` / `[]`; do not invent zero or unrestricted requirements |
| Invalid numeric value | Report and preserve source evidence; do not coerce it into a usable statistical zero |
| Missing upper salary bound / reversed interval | Keep source display, exclude midpoint statistics |
| Unknown category or invalid review status | Reject review input; do not silently map to another class |
| Unresolved category disagreement | Leave final group category unset, retain evidence and require adjudication |
| Fewer than five eligible groups | Exclude that bucket from salary ranking, retain sample count/distribution context |
| No matching groups | No salary estimate; no fabricated percentage; use the methodology's empty-result contract |

The validation above remains normative. The original 2026-10-17 contract task was documentation-only; later application code and artifacts exist. The 2026-10-20 review used read-only source/data audits and document checks, and did not rerun importer, application or database tests.

## 5. Good / Base / Bad Cases

| Case | Expected result |
| --- | --- |
| Explicit software developer title, one unambiguous rule result | Rule-sourced category may be provisionally used; review remains unconfirmed |
| Generic campus recruitment title without clear duties | Final category `null`, displayed as unclassified |
| Two identical source records with different skill tags | One job group, skill union, one salary observation |
| Numeric salary bounds were swapped but display is `40-25K/月` | Retain display and evidence; exclude the group from midpoint statistics |
| Same group contains unresolved contradictory category proposals | No arbitrary category inherited from the smallest ID |

## 6. Tests Required

Importer/query tests must assert source-field retention, null handling, referential integrity, numeric parsing and source-ID stability. Group tests must cover skill union, conflicting reviews, grouping before normalization and stable representative IDs. Aggregate tests must cover identical list/chart scopes, skill-link expansion, missing/reversed salary bounds, sample sizes four/five, empty filters and zero skill coverage. Category tests must cover explicit titles, generic campus titles, multi-role titles, digital-chip design versus web frontend, pending disagreement and confirmed adjudication.

The historical 2026-10-18 preparation verification recorded `verify_contracts.py` checks against AC-1 through AC-8 (SHA-256 match, 2251 groups, null/float conversion, salary exclusions, review status transitions, and group-level category conflict propagation), plus Ruff and pyright with 0 errors. These are historical results, not checks rerun in the current documentation review; do not run legacy preparation scripts merely to refresh this wording.

## 7. Wrong vs Correct

```text
Wrong: join skills -> count expanded rows -> remove duplicates in the browser.
Correct: exact source groups -> merge skill evidence -> category projection
         -> shared filters -> independent group counts and aggregates -> page.

Wrong: city missing -> copy province; no tag -> no skill needed;
       higher salary on tagged jobs -> learning that skill causes a raise.
Correct: retain missing city, report tag coverage, describe sample associations.
```
