# CF Stalker — System Architecture Specification

## Overview
CF Stalker is designed as a **Modular Monolith** using FastAPI for high-concurrency API performance, PostgreSQL for normalized relational data storage, Redis for multi-tier caching and task broker management, and Celery for asynchronous background job execution.

```mermaid
graph TD
    Client["React 18 + Vite + TS UI"] -->|HTTP/REST| API["FastAPI Application"]
    API --> Auth["JWT & Rate-Limit Middleware"]
    Auth --> ServiceLayer["Service Layer (Analytics, Recommendations, AI Coach)"]
    ServiceLayer --> Postgres[(PostgreSQL 16)]
    ServiceLayer --> Redis[(Redis 7 Cache)]
    API -->|Async Task Trigger| CeleryWorker["Celery Worker Queue"]
    CeleryWorker --> CFAPI["Codeforces REST API"]
    CeleryWorker --> Postgres
```

## Architectural Design Principles
1. **Separation of Concerns**: Clean isolation between API layer (FastAPI routes), domain validation (Pydantic schemas), database layer (SQLAlchemy ORM), business logic (Services), and background workers (Celery).
2. **Asynchronous Non-Blocking API**: Fast HTTP responses by delegating long-running data syncs to background workers.
3. **Resilient Third-Party Integration**: Codeforces API calls are strictly rate-limited using a Redis Token-Bucket algorithm (max 1 request per 2 seconds).
4. **Contextual LLM AI Coach**: Rather than generic chat, the AI coach receives a computed statistical metric payload and responds in structured JSON.
