# Backend Development Guidelines

> Best practices for backend development in this project.

---

## Overview

This directory contains guidelines for backend development. The approved data contract below is documentation for future implementation; the remaining application guidelines are scaffolding and still need project-specific conventions.

## Pre-Development Checklist

- For import, classification, filtering or analytical work, read [Data Contract](./data-contract.md) and its linked field, review and statistical definitions first.
- No application modules, endpoints or database collections have been implemented by the data-contract task.

## Quality Check

- Check data-related changes against the validation matrix and assertion points in [Data Contract](./data-contract.md).
- Do not treat source snapshot counts as constants or skip group-level consistency between list totals and analytics.

---

## Guidelines Index

| Guide | Description | Status |
|-------|-------------|--------|
| [Data Contract](./data-contract.md) | Approved input/projection boundaries, offline classification and statistical rules | Approved contract; implementation pending |
| [Directory Structure](./directory-structure.md) | Module organization and file layout | To fill |
| [Database Guidelines](./database-guidelines.md) | ORM patterns, queries, migrations | To fill |
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
