# Functional feasibility assessment

Assessment date: 2026-10-20. This document evaluates candidates; it does not approve their product scope or authorize implementation.

## Evidence and verification

- Recomputed counts from `data/processed/jobs_cleaned_grouped.json`; machine-readable results: `data-capability-audit.json`.
- Reviewed `backend/app/db/repository.py`, `api/deps.py`, `api/v1/endpoints/jobs.py`, `schemas/job.py`, the existing job detail UI, and field/statistical contracts.
- Executed `backend/.venv/Scripts/python.exe -m pytest backend/tests/test_api.py -q`: **12 passed**. Tests use the real local dataset through the in-memory repository path. MongoDB lifecycle is not exercised by the ASGITransport fixture; this is not evidence of a live MongoDB integration or browser check.
- No Docker startup, database writes, new crawling, product code changes or live source validation were performed.

## Actual data coverage

| Field / property | Nonempty / eligible groups | Implication |
| --- | ---: | --- |
| Total groups / unique representative IDs | 2251 / 2251 | Sufficient to explore candidates and reference saved jobs |
| Title, company, education, source URL, publish date | 2251 each | Supports basic comparison and source links |
| Valid salary intervals | 2194 | Supports interval filtering and factual salary comparison |
| Province | 2016 | Primary regional selector; preserve missing values |
| City | 486 | Insufficient for broad city-based matching |
| Description | 1340 | Detail view can be useful; 911 groups lack body text |
| Skills | 833 (24 distinct names) | Partial tag comparison; 1418 groups lack tags |
| Major requirement | 1416 | Show original text, without claiming normalized major eligibility |
| Explicit minimum experience years | 17 | Cannot support robust experience-based eligibility or ranking |

All groups have source URLs on `job.ncss.cn`. Publish dates range from 2025-10-21 to 2026-10-16. The dataset has no verified live vacancy status or application outcome. Recompute counts when inputs change.

## Candidate features and present support

| Candidate | Feasibility / required work | Supported promise |
| --- | --- | --- |
| Job exploration | Existing category, province, keyword, salary-overlap, education-label filters, pagination and details | Find records meeting explicit conditions within this snapshot |
| Personal education eligibility | Minimum education codes exist, but current API matches `education_requirement` exactly | Needs a separately defined eligibility filter; preserve existing exact-label analytics semantics |
| Save candidate jobs | Stable IDs and detail endpoint exist; persistence has not been implemented | A browser-local shortlist is a small extension; cross-device synchronization needs additional product/storage decisions |
| Side-by-side comparison | Existing details contain salary, province, education, experience text and tags | Compare selected records; display missing information explicitly |
| Explain matching | Conditions can be shown directly alongside record facts | Explain selected filters and known facts; do not call this a verified overall suitability assessment |
| Skill checklist | Compare self-declared skills against explicit existing tags; no current user-skill state or checklist implementation | Known tag overlap and tags to review; source tags do not establish required proficiency or essential requirements |
| Complete skill-gap assessment / learning plan | Coverage and evidence are incomplete; no proficiency labels, course corpus or validated learning outcomes | Insufficient evidence for a reliable complete assessment |
| Personalized salary / hiring-probability prediction | No individual skill proficiency, offer outcomes, employment history or outcome labels | Insufficient evidence; observed salary differences are descriptive |
| Live recruiting / submission tracking | Current snapshot lacks vacancy status and application integration | Source navigation is feasible; applications and current availability are not established |

## Recommended first release (proposal)

Core workflow: set explicit search conditions → inspect jobs → save candidates → compare → review original source. Existing market analytics support these decisions. Add partial skill-tag checking as an auxiliary feature if desired, with clear unknown states.

This is a functional decision-support system with realistic data requirements. It does not require predictive modeling or a complete personal competency assessment. Its engineering work still includes shortlist persistence, comparison UI, error/empty states and any approved eligibility-filter contract changes.

The user subsequently approved this core direction and requested documentation-only handoff to another implementation agent. The converged PRD defines browser-local persistence and auxiliary tag checking; design.md and implement.md define implementation defaults and acceptance. Final plan review is still required before task.py start. Earlier proposals in this assessment are evidence, not a second source of requirements.
