# Frontend State Management Guidelines

## Overview

State management is centered around Pinia (`useFilterStore`) with bidirectional synchronization to Vue Router's URL Query parameters.

---

## Global Slicing Store (`useFilterStore`)

- **State**:
  - `category`: `string | undefined`
  - `province`: `string | undefined`
  - `education`: `string | undefined`
- **Actions**:
  - `setCategory(value)` / `setProvince(value)` / `setEducation(value)`
  - `resetFilters()`
  - `syncFromQuery(query)`: Hydrates state from Vue Router `to.query` on route transitions.

---

## User Workspace Store (`useWorkspaceStore`)

- **Storage Key**: `jobinsight:workspace:v1` (localStorage, `version: 1`).
- **State**:
  - `savedJobIds`: `string[]` (candidate shortlist IDs, unshifted, unique, server-canonical representative IDs).
  - `knownSkills`: `string[] | null` (`null` = not configured; `[]` = user explicitly mastered none; `string[]` = selected tags).
  - `compareJobIds`: `string[]` (active comparison IDs, max 3, memory-only, synchronized with `/compare?ids=...`).
  - `canPersist`: `boolean` (reflects whether localStorage write is permitted).
- **Invariants**:
  - `localStorage.clear()` is strictly forbidden; corrupt or unknown version degrades to session mode without touching other keys.
  - Candidate shortlist and compare selections are completely decoupled: removing from shortlist does not clear comparison.

---

## Rules & Invariants

1. **URL as Ground Truth**: Any change in `GlobalSlicer` or `/jobs` query pushes a route replacement via `router.replace({ query })`, which ensures browser back/forward, page reload, and URL sharing remain consistent.
2. **Never Fabricate Data**: Pinia stores only active user filters and candidate IDs; analytical and job data is never fabricated or cached in memory as dummy numbers.
3. **Empty-State Handling**: When filters return 0 records, ECharts instances must be explicitly cleared (`clear()`) to avoid stale canvas rendering.
