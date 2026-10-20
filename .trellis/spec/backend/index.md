# Backend Development Guidelines

> Best practices for backend development in this project.

---

## Overview

The FastAPI backend currently implements job search, detail reads and sample analytics through MongoDB and a local JSON fallback. The data contract below remains authoritative. Directory and database guides contain project-specific content; error, quality and logging guides remain scaffolding. See the [current project review](../../../docs/review/2026-10-20_203614_project-review.md) for implementation evidence and known differences from the contract, including Python percentile calculation and database verification limits.

## Pre-Development Checklist

- For import, classification, filtering or analytical work, read [Data Contract](./data-contract.md) and its linked field, review and statistical definitions first.
- The original data-contract task was documentation-only. Current application code exists under `backend/app/`; a completed historical task is not proof that a database, query plan or deployment was verified in the current environment.

## Quality Check

- Check data-related changes against the validation matrix and assertion points in [Data Contract](./data-contract.md).
- Do not treat source snapshot counts as constants or skip group-level consistency between list totals and analytics.

---

## Guidelines Index

| Guide | Description | Status |
|-------|-------------|--------|
| [Data Contract](./data-contract.md) | Approved input/projection boundaries, offline classification and statistical rules | Active contract; implementation differences documented in the current review |
| [Directory Structure](./directory-structure.md) | Module organization and file layout | Project guide present |
| [Database Guidelines](./database-guidelines.md) | MongoDB queries, indexes and fallback | Project guide present; runtime plans and imported data require separate verification |
| [Error Handling](./error-handling.md) | Error types, handling strategies | To fill |
| [Quality Guidelines](./quality-guidelines.md) | Code standards, forbidden patterns | To fill |
| [Logging Guidelines](./logging-guidelines.md) | Structured logging, log levels | To fill |

---

## How to Fill These Guidelines

For each guideline file:

1. Document your project's **actual conventions** (not ideals)
2. Include **code examples** from your codebase
3. List **forbidden patterns** and why
4. Add **common mistakes** your team has made

The goal is to help AI assistants and new team members understand how YOUR project works.

---

**Language**: All documentation should be written in **English**.
