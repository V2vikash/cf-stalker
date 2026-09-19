# CF Stalker — Production Deployment Guide

This document outlines the requirements and procedures for deploying the **CF Stalker** application to production environments.

---

## 1. Environment Requirements & Prerequisites

- **Docker Engine**: 24.0+ & **Docker Compose**: v2.20+
- **Managed PostgreSQL**: Version 16+ (e.g. AWS RDS, DigitalOcean Managed Postgres, GCP Cloud SQL)
- **Managed Redis**: Version 7+ (e.g. AWS ElastiCache, Redis Enterprise)
- **SSL / TLS Termination**: Nginx, Cloudflare, or AWS ALB handling HTTPS.

---

## 2. Environment Variables Configuration

Copy `.env.example` to `.env` and configure production secrets:

```ini
# Production Environment Settings
APP_NAME="CF Stalker"
ENVIRONMENT="production"
DEBUG=False
SECRET_KEY="generate-a-cryptographically-secure-random-64-character-string"

# Production API & Origins
API_V1_STR="/api/v1"
ALLOWED_ORIGINS=["https://app.cfstalker.com"]

# Production Database (Managed PostgreSQL)
DATABASE_URL=postgresql+asyncpg://db_user:secure_password@postgres-prod-host:5432/cf_stalker

# Production Redis (Managed Redis / ElastiCache)
REDIS_URL=rediss://:redis_password@redis-prod-host:6379/0
CELERY_BROKER_URL=rediss://:redis_password@redis-prod-host:6379/0
CELERY_RESULT_BACKEND=rediss://:redis_password@redis-prod-host:6379/1

# Codeforces API Settings
CF_API_BASE_URL=https://codeforces.com/api
CF_API_RATE_LIMIT_DELAY=2.0

# LLM API Credentials
LLM_PROVIDER=openai
LLM_API_KEY=your-production-openai-key
LLM_MODEL=gpt-4o-mini
```

---

## 3. Database Migration

Run Alembic database migrations against the production database:

```bash
docker-compose run --rm backend alembic upgrade head
```

---

## 4. Launching Production Containers

Build and deploy production containers:

```bash
docker-compose -f docker-compose.yml up --build -d
```

Verify service status:

```bash
docker-compose ps
docker-compose logs -f backend
```

---

## 5. Health Checks & Verification

- **API Health Endpoint**: `GET https://app.cfstalker.com/api/v1/health`
- **Expected Response**: `{"status": "healthy", "database": "connected", "redis": "connected"}`
