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
  - `setFilter(key, value)`
  - `resetFilters()`
  - `syncFromQuery(query)`: Hydrates state from Vue Router `to.query` on route transitions.

---

## Rules & Invariants

1. **URL as Ground Truth**: Any change in `GlobalSlicer` pushes a route replacement via `router.replace({ query })`, which ensures browser back/forward, page reload, and URL sharing remain consistent.
2. **Never Fabricate Data**: Pinia stores only active user filters; analytical data is never fabricated or cached in memory as dummy numbers.
3. **Empty-State Handling**: When filters return 0 records, ECharts instances must be explicitly cleared (`clear()`) to avoid stale canvas rendering.
