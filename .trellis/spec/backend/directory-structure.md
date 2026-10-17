# Backend Directory Structure & Module Layout

## Overview

Backend is implemented using Python 3.11 with FastAPI (async ASGI), Motor (async MongoDB driver), and Pydantic v2. Business logic and aggregations live in `app/db/repository.py`, and endpoints are organized in `app/api/v1/endpoints/`.

---

## Directory Layout

```text
backend/
├── app/
│   ├── api/
│   │   ├── deps.py               # Shared Query filter dependency (FilterParams)
│   │   └── v1/
│   │       ├── api.py            # API router aggregator
│   │       └── endpoints/
│   │           ├── meta.py       # GET /api/v1/meta/options
│   │           ├── overview.py   # GET /api/v1/overview
│   │           ├── stats.py      # GET /api/v1/stats/* (salary, region, skills)
│   │           └── jobs.py       # GET /api/v1/jobs & /api/v1/jobs/{id}
│   ├── core/
│   │   └── config.py             # Pydantic BaseSettings loading .env
│   ├── db/
│   │   ├── mongodb.py            # Motor AsyncIOMotorClient lifespan management
│   │   ├── repository.py         # Async query repository with native pipelines & offline fallback
│   │   └── seed.py               # Database seeding and index creation script
│   ├── schemas/
│   │   ├── response.py           # Unified ResponseModel[T] ({ code, message, data })
│   │   └── job.py                # Job, Stats, and Filter Pydantic models
│   └── main.py                   # FastAPI app entrypoint, CORS, exception handlers
├── tests/
│   ├── conftest.py               # Async test fixtures
│   └── test_api.py               # AC verification tests
├── requirements.txt              # Pinned backend dependencies
└── .env.example                  # Environment template
```

---

## API & Response Conventions

1. **Unified Envelope**: All API endpoints return `ResponseModel[T]` (`{ "code": 200, "message": "success", "data": ... }`).
2. **Global Slicing Support**: All `/stats/*` and `/jobs` endpoints inject `FilterParams` (`category`, `province`, `education`).
3. **Async Non-blocking**: Endpoints are defined with `async def` and invoke asynchronous methods on the repository.
