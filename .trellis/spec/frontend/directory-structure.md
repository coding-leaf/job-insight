# Frontend Directory Structure & Module Layout

## Overview

Frontend is built using Vite, Vue 3 (<script setup lang="ts">), TypeScript, Element Plus, Apache ECharts, Pinia, and Vue Router. It follows a multi-page analytical workbench architecture with persistent global slicing.

---

## Directory Layout

```text
frontend/
├── src/
│   ├── api/                      # Unified API client & endpoint functions
│   │   ├── client.ts             # Axios instance with unwrap interceptor & error toast
│   │   ├── meta.ts               # Options & metadata endpoint
│   │   ├── overview.ts           # Overview KPI & distribution endpoint
│   │   ├── stats.ts              # Salary & skills aggregation endpoints
│   │   └── jobs.ts               # Job search & detail endpoints
│   ├── composables/              # Deep functions / composables
│   │   └── useECharts.ts         # Chart lifecycle, resize observer, disposal
│   ├── stores/                   # Pinia state
│   │   └── filter.ts             # useFilterStore (global slicing scope + URL query sync)
│   ├── types/                    # Strict TypeScript data contracts
│   │   ├── api.ts                # ResponseModel<T>
│   │   └── job.ts                # Domain models matching backend Pydantic schemas
│   ├── components/               # Deep components
│   │   ├── GlobalHeader.vue      # Top navigation header & baseline indicators
│   │   ├── GlobalSlicer.vue      # Sticky sub-header filter bar (syncs with URL query)
│   │   └── JobDetailDrawer.vue   # Deep drawer showing 19-column raw data & skill provenance
│   ├── views/                    # 4 Core Business Pages
│   │   ├── OverviewView.vue      # Macro overview dashboard
│   │   ├── SalaryView.vue        # Salary rankings, regional gradient & scale breakdown
│   │   ├── SkillsView.vue        # Skill penetration (dual denominators) & radar profile
│   │   └── JobsView.vue          # High-density job explorer & raw data table
│   ├── router/
│   │   └── index.ts              # Vue Router 4 routes with query preservation
│   ├── App.vue                   # Root layout component
│   └── main.ts                   # Application entrypoint
├── index.html
├── vite.config.ts                # Proxy /api to 127.0.0.1:8000 & path alias @
├── tsconfig.json
└── package.json
```

---

## Routing & Navigation Rules

1. **4 Core Routes**: `/overview`, `/salary`, `/skills`, `/jobs`. Route `/` automatically redirects to `/overview`.
2. **Query Preservation**: Navigating between routes must preserve the active slicing query parameters (`?category=...&province=...&education=...`).
