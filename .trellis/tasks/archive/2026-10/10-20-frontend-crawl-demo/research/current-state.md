# Current-state inspection (2026-10-20)

## Frontend

- `frontend/src/router/index.ts` and the four view files provide existing analytics pages; page code calls the existing API modules.
- `frontend/vite.config.ts` proxies /api to 127.0.0.1:8000 and configures port 5173.
- `frontend/src/components/GlobalHeader.vue:55` contains a hardcoded 2,251 baseline. `OverviewView.vue:350` contains static 833/2,251 explanatory figures. Verify these against dynamic API semantics during implementation.
- `SkillsView.vue:459` uses 60%/40% grid columns alongside a 20px gap. Check overflow in the actual browser before deciding the layout fix.
- Each view has a catch handler; inspect actual Axios notifications and browser behavior before specifying error-state changes.
- No build, browser checks or service startup have been performed in this planning pass.

## Existing crawler

- Read-only inspected sibling directory `../final-homeworkwork/`, including README, collection notes, AppConfig, MohrssSource and CiicSource.
- Java 17/Maven project; README documents CSV, JSONL, raw snapshots, errors, summary and checkpoints.
- AppConfig supports source, target, output path, delay, timeout and page limits.
- MohrssSource reads a public list URL; CiicSource reads a featured API. Historical README statements do not establish current endpoint availability.
- Existing target.jar availability, Java runtime and current external accessibility remain unverified. Verify selected source online before live collection.
- Avoid --fresh on existing outputs. Use a new directory inside job-insight for every demonstration run; keep new samples separate from processed baseline data.

## Initial proposal (superseded by the final PRD)

The initial inspection proposed polishing the four pages and running a small crawler demo. The user subsequently clarified that the goal is a functional system and approved job exploration, local shortlisting and comparison, with partial skill-tag checking as an auxiliary feature. The final scope is in ../prd.md; crawling is deferred. This file preserves inspection evidence, not the current implementation requirements.
