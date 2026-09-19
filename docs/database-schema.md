# Database ER Schema Specification

## PostgreSQL Normalized Entities

### 1. `users`
- `id`: `UUID` (Primary Key)
- `email`: `VARCHAR(255)` (Unique, Indexed)
- `hashed_password`: `VARCHAR(255)`
- `is_active`: `BOOLEAN`
- `created_at`: `TIMESTAMPTZ`

### 2. `cf_profiles`
- `id`: `UUID` (Primary Key)
- `user_id`: `UUID` (Foreign Key -> `users.id`)
- `handle`: `VARCHAR(100)` (Unique, Indexed)
- `rating`: `INTEGER`
- `max_rating`: `INTEGER`
- `rank`: `VARCHAR(100)`
- `avatar`: `VARCHAR(500)`
- `last_synced_at`: `TIMESTAMPTZ`

### 3. `problems`
- `id`: `VARCHAR(100)` (Primary Key, format: `contestId_index`)
- `contest_id`: `INTEGER` (Indexed)
- `index`: `VARCHAR(10)`
- `name`: `VARCHAR(255)`
- `rating`: `INTEGER` (Indexed)
- `points`: `FLOAT`

### 4. `problem_tags`
- `id`: `UUID` (Primary Key)
- `problem_id`: `VARCHAR(100)` (Foreign Key -> `problems.id`)
- `tag`: `VARCHAR(100)` (Indexed)

### 5. `submissions`
- `id`: `BIGINT` (Primary Key, Codeforces Submission ID)
- `cf_profile_id`: `UUID` (Foreign Key -> `cf_profiles.id`)
- `problem_id`: `VARCHAR(100)` (Foreign Key -> `problems.id`)
- `creation_time`: `TIMESTAMPTZ` (Indexed)
- `verdict`: `VARCHAR(50)`
- `pass_test_count`: `INTEGER`
- `time_consumed_ms`: `INTEGER`
- `memory_consumed_bytes`: `BIGINT`

### 6. `user_topic_stats`
- `id`: `UUID` (Primary Key)
- `cf_profile_id`: `UUID` (Foreign Key -> `cf_profiles.id`)
- `tag`: `VARCHAR(100)`
- `solved_count`: `INTEGER`
- `attempted_count`: `INTEGER`
- `max_rating_solved`: `INTEGER`
- `accuracy`: `FLOAT`

### 7. `sync_jobs`
- `id`: `UUID` (Primary Key)
- `cf_profile_id`: `UUID` (Foreign Key -> `cf_profiles.id`)
- `job_type`: `VARCHAR(50)`
- `status`: `VARCHAR(50)` (PENDING, RUNNING, COMPLETED, FAILED)
- `error_message`: `TEXT`
- `created_at`: `TIMESTAMPTZ`
