# API Reference

Open KLara provides a REST API for programmatic job management and user administration. All API endpoints accept **POST** requests and return JSON responses.

## Authentication

Every API request must include an `auth_code` POST parameter. This code is stored in the `users` table (`api_auth_code` column) and must have `api_status = 1` enabled.

Per-method access is controlled by the `api_perms` JSON array in the user record. Set it to `["all"]` to grant access to all endpoints, or list specific methods:

```json
["/api/jobs/get_all_jobs", "/api/jobs/status", "/api/jobs/add"]
```

## Response Format

All endpoints return JSON with this structure:

```json
{
  "status": "ok",
  "status_msg": "",
  "return_data": { ... }
}
```

On error:

```json
{
  "status": "error",
  "status_msg": "Error description"
}
```

## Jobs API

Base URL: `/api/jobs/`

### List All Jobs

**`POST /api/jobs/get_all_jobs`**

Returns jobs visible to the authenticated user, ordered by ID descending.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `auth_code` | string | Yes | — | API authentication code |
| `limit` | int | No | 100 | Max jobs to return (1–9999) |
| `detailed_info` | string | No | `"false"` | Set to `"true"` for full rules |

**Response** (`return_data`):

```json
[
  {
    "id": "42",
    "rules_first_line": "rule example_rule",
    "status": "finished",
    "start_time": "2025-01-15 10:30:00",
    "finish_time": "2025-01-15 10:45:00",
    "owner": "john"
  }
]
```

When `detailed_info=true`, the `rules_first_line` key is replaced with `rules` containing the full Yara rule text.

### Submit a Job

**`POST /api/jobs/add`**

Submits a new Yara scan job across one or more repositories.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `auth_code` | string | Yes | API authentication code |
| `rules` | string | Yes | Yara rule(s) text |
| `repositories` | string | Yes | JSON array of repository IDs |

**Example:**

```bash
curl -X POST http://your-server/api/jobs/add \
  -d "auth_code=YOUR_API_KEY" \
  -d "rules=rule test { strings: \$a = \"malware\" condition: \$a }" \
  -d 'repositories=[1,2]'
```

### Get Job Status

**`POST /api/jobs/status/{id}`**

Returns details for a specific job.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `auth_code` | string | Yes | — | API authentication code |
| `detailed_info` | string | No | `"false"` | Set to `"true"` for full details |

**Basic response** (`return_data`):

```json
{
  "id": "42",
  "status": "finished",
  "description": "{\"fileset_scan\":\"/virus_repository\", ...}",
  "agent_id": "1",
  "owner": "john"
}
```

**Detailed response** (when `detailed_info=true`) adds:

- `rules` — Full Yara rule text
- `matched_files` — Number of matched files
- `start_time` / `finish_time` — Timestamps
- `results` — Raw Yara output (only for `finished` / `yara_errors` status)
- `hashes` — Array of MD5 hashes of matched files

### Delete a Job

**`POST /api/jobs/delete/{id}`**

Deletes a job. Only the owner or an admin can delete. Assigned (in-progress) jobs cannot be deleted.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `auth_code` | string | Yes | API authentication code |

### Test Job Submission

**`POST /api/jobs/test_add`**

Validates rules and repositories without creating a job. Accepts the same parameters as `/api/jobs/add`.

### Get Allowed Repositories

**`POST /api/jobs/get_allowed_repos`**

Returns the list of scan repositories available to the authenticated user.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `auth_code` | string | Yes | API authentication code |

## Users API

Base URL: `/api/users/`

> **Note:** User management endpoints require admin-level API permissions.

### Add a User

**`POST /api/users/add`**

Creates a new user. The `auth` level cannot exceed power user (8).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `auth_code` | string | Yes | API authentication code |
| `username` | string | Yes | Unique username |
| `password` | string | Yes | Plain-text password (hashed with bcrypt) |
| `auth` | int | Yes | Auth level: 2 (registered), 4 (observer), 8 (power user) |
| `description` | string | Yes | User description |
| `group_cnt` | int | Yes | User group ID (must exist in `users_groups`) |
| `quota_searches` | int | Yes | Monthly scan quota |
| `notify_email` | string | Yes | Notification email address |

**Response** (`return_data`):

```json
{ "id": 3 }
```

### Disable a User

**`POST /api/users/disable`**

Suspends a user by setting their auth level to 1. Administrators cannot be disabled.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `auth_code` | string | Yes | API authentication code |
| `user_cnt` | int | Yes | User ID to disable |


## Dispatcher API (Internal)

The dispatcher exposes an internal API on port 8888 (configurable) for worker communication. These endpoints are **not** intended for end users.

All endpoints require an `auth` POST parameter matching a token in the `agents` database table.

### Fetch Available Jobs

**`POST /api/worker_fetch_available_jobs`**

Returns all jobs with status `new`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `auth` | string | Yes | Worker authentication token |

**Response** (`return_data`): JSON array of `{"id": int, "fileset_scan": string}`.

### Assign a Job

**`POST /api/worker_assign_job`**

Atomically assigns a job to the requesting worker using row-level locking (`SELECT FOR UPDATE`).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `auth` | string | Yes | Worker authentication token |
| `job_id` | int | Yes | Job ID to claim |

**Response** (`return_data`): `{"status": "accepted", "rules": "..."}` or `{"status": "rejected"}`.

### Save Results

**`POST /api/worker_save_results`**

Submits scan results. The dispatcher saves results to the database and sends email notifications.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `auth` | string | Yes | Worker authentication token |
| `results` | string | Yes | JSON-encoded results object |

**Results object fields:**

| Field | Type | Description |
|-------|------|-------------|
| `job_id` | int | Job ID |
| `finish_time` | string | Completion timestamp |
| `fileset_scan` | string | Repository path scanned |
| `execution_time` | int | Scan duration in seconds |
| `yara_errors` | string | `"true"` or `"false"` |
| `yara_warnings` | string | `"true"` or `"false"` |
| `matched_files` | int | Number of matched files |
| `md5_results` | string | JSON array of MD5 hashes |
| `yara_results` | string | Raw Yara output |