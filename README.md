# CF Stalker — Competitive Programming Intelligence Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React_18-61DAFB.svg)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL_16-336791.svg)](https://www.postgresql.org/)
[![Celery](https://img.shields.io/badge/Async_Queue-Celery-37814A.svg)](https://docs.celeryq.dev/)

> **CF Stalker** is an advanced Competitive Programming Intelligence and Performance Analytics platform. Built with FastAPI, React, PostgreSQL, Redis, Celery, and LLMs, it transforms raw Codeforces submissions and contest histories into deep actionable insights, statistical skill-gap matrixes, sweet-spot problem recommendations, and personalized AI performance coaching.

---

## Key Features

- **Profile & Rating Intelligence**: Real-time trajectory tracking, rating volatility metrics, and rank progression analytics.
- **Contest Performance Engine**: Post-contest tactical breakdown, rank vs expected rank delta, penalty impact, and unsolved opportunity costs.
- **Statistical Skill-Gap Matrix**: Tag-wise rating disparity analysis evaluating topic proficiency relative to overall user rating.
- **Algorithmic Problem Recommendations**: Dynamic recommendation engine delivering:
  - *Sweet Spot Problems* ($\text{Rating} + 100 \text{ to } + 200$)
  - *Weak-Tag Remedial Drills*
  - *Contest Upsolving Opportunities*
- **LLM-Powered AI Performance Coach**: Context-aware AI coach analyzing actual statistical performance payloads to generate weekly action plans and tactical advice.
- **Asynchronous Ingestion Pipeline**: Asynchronous background synchronization via Celery workers with strict Codeforces API rate limiting (1 req/2s token bucket).

---

## Tech Stack & Architecture

- **Frontend**: React 18, TypeScript, Tailwind CSS, Recharts, TanStack Query (React Query v5), Zustand.
- **Backend**: FastAPI (Python 3.11+), Pydantic v2, SQLAlchemy 2.0 (Async ORM), Alembic.
- **Database & Cache**: PostgreSQL 16 (Relational Normalized Storage), Redis 7 (Caching & Celery Broker).
- **Asynchronous Processing**: Celery 5 (Workers + Celery Beat Scheduler).
- **AI / LLM**: Context-driven LLM integration (OpenAI / Gemini / Anthropic) returning structured JSON.
- **DevOps & Infrastructure**: Docker, Docker Compose, GitHub Actions CI/CD.

---

## Repository Architecture

```
cf-stalker/
├── backend/            # FastAPI application & Celery task handlers
├── frontend/           # React 18 + TypeScript + Tailwind CSS application
├── docs/               # Architecture, API, database, and deployment specifications
├── infrastructure/     # Nginx & production deployment configurations
├── tests/              # Pytest (Backend) & Vitest (Frontend) test suites
├── docker-compose.yml  # Local multi-container development environment
├── .env.example        # Environment variable template
├── LICENSE             # MIT License
└── README.md
```

---

## Quick Start (Docker)

### Prerequisites
- Docker Engine 24.0+
- Docker Compose v2.20+

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/cf-stalker.git
   cd cf-stalker
   ```

2. Configure environment variables:
   ```bash
   cp .env.example .env
   ```

3. Launch the full stack using Docker Compose:
   ```bash
   docker-compose up --build
   ```

4. Access services:
   - **Frontend Dashboard**: `http://localhost:5173`
   - **Backend REST API**: `http://localhost:8000`
   - **API Interactive Swagger Docs**: `http://localhost:8000/docs`
   - **Health Check**: `http://localhost:8000/api/v1/health`

---

## Manual Local Development Setup

### Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## Documentation

Detailed architecture specifications are available in the [`/docs`](docs/) directory:
- [System Architecture](docs/architecture.md)
- [Database ER Schema](docs/database-schema.md)
- [API Documentation](docs/api-docs.md)
- [Deployment Guide](docs/deployment.md)

---

## License

This project is licensed under the [MIT License](LICENSE).
