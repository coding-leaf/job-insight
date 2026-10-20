# Frontend Development Guidelines

> Best practices for frontend development in this project.

---

## Overview

The Vue application currently has seven business routes, with browser-local candidate/skill state and API-driven exploration and analytics. Directory and state-management guides contain project-specific content; the other guideline files below remain scaffolding. Data-driven UI changes must follow the approved references. See the [current project review](../../../docs/review/2026-10-20_203614_project-review.md) for actual behavior and verification limits.

## Pre-Development Checklist

- Read the [Field Dictionary](../../../docs/data-dictionary.md) and [Statistical Methodology](../../../docs/statistical-methodology.md) before displaying job counts, filters, salary or skills.
- Follow the shared [Data Contract](../backend/data-contract.md); do not implement separate browser-only deduplication or invent missing values.

## Quality Check

- Salary charts show units and eligible group sample counts; skill charts show annotation coverage and use the specified denominator.
- Unclassified and missing values remain distinct from confirmed categories and zeroes. Verify empty-state behavior against the methodology document.
- Review and provenance metadata belongs to offline preparation, not an unrequested product review dashboard.

---

## Guidelines Index

| Guide | Description | Status |
|-------|-------------|--------|
| [Directory Structure](./directory-structure.md) | Module organization and file layout | Project guide present |
| [Component Guidelines](./component-guidelines.md) | Component patterns, props, composition | To fill |
| [Hook Guidelines](./hook-guidelines.md) | Custom hooks, data fetching patterns | To fill |
| [State Management](./state-management.md) | Local state, global state, server state | Project guide present; verify details against source and the current review |
| [Quality Guidelines](./quality-guidelines.md) | Code standards, forbidden patterns | To fill |
| [Type Safety](./type-safety.md) | Type patterns, validation | To fill |

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
