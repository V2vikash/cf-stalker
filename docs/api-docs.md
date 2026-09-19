# CF Stalker — REST API Reference Documentation

The **CF Stalker** API provides endpoints for Codeforces profile sync, competitive programming analytics, skill-gap calculations, recommended problem discovery, and AI performance coaching.

Base Path: `/api/v1`

---

## 1. Health

### `GET /health`
Returns the status of the FastAPI backend, PostgreSQL database connection, and Redis cache.
- **Response**: `200 OK`
```json
{
  "status": "healthy",
  "app_name": "CF Stalker",
  "environment": "production",
  "database": "connected",
  "redis": "connected"
}
```

---

## 2. Authentication

### `POST /auth/register`
Register a new user account.
- **Request Body**: `{"email": "user@example.com", "password": "SecurePassword123!"}`
- **Response**: `201 Created`

### `POST /auth/login`
Authenticate user credentials and receive JWT access/refresh tokens.
- **Request Body**: `{"email": "user@example.com", "password": "SecurePassword123!"}`
- **Response**: `200 OK`
```json
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "eyJhbGciOi...",
  "token_type": "bearer"
}
```

---

## 3. Codeforces Profile & Data Sync

### `POST /cf/profile/{handle}`
Initiate background ingestion and analysis for a Codeforces handle.
- **Response**: `200 OK`
```json
{
  "handle": "tourist",
  "status": "PENDING",
  "sync_job_id": "uuid-v4-string"
}
```

### `GET /cf/sync-status/{job_id}`
Poll sync status for an ongoing background sync job.
- **Response**: `200 OK`

---

## 4. Analytics

### `GET /analytics/overview/{handle}`
Retrieve rating stats, volatility (standard deviation), solved totals, and overall accuracy.

### `GET /analytics/contests/{handle}`
Retrieve contest trajectory, rating delta metrics, and rank performance.

### `GET /analytics/topics/{handle}`
Retrieve tag-wise performance metrics and problem rating difficulty distribution.

---

## 5. Skill Gap Matrix

### `GET /skill-gap/matrix/{handle}`
Get tag-wise skill gap analysis classifying topics into `WEAKNESS`, `BALANCED`, or `STRENGTH`.

---

## 6. Recommendations

### `GET /recommendations/daily/{handle}`
Get personalized daily problem recommendations (`SWEET_SPOT` & `WEAK_TAG_DRILL`).

---

## 7. AI Performance Coach

### `POST /ai-coach/review/{handle}`
Generate a structured AI performance coaching review and tactical action plan.
