# Architecture

Open KLara uses a **dispatcher-worker** model to distribute Yara scans across multiple servers, enabling efficient scanning of large malware sample collections (10TB+ in ~30 minutes).

## System Overview

```
┌─────────────┐       ┌──────────────────┐       ┌──────────────┐
│  Web UI /    │       │                  │       │   Worker 1   │
│  REST API    │──────▶│   Dispatcher     │◀──────│  (Yara scan) │
│  (PHP/CI)    │       │  (Python/Tornado)│       └──────────────┘
└─────────────┘       │                  │       ┌──────────────┐
      │                │   Port 8888      │◀──────│   Worker 2   │
      │                └──────────────────┘       │  (Yara scan) │
      │                        │                  └──────────────┘
      │                        │                        ...
      ▼                        ▼
┌──────────────────────────────────────────┐
│              MySQL Database              │
│            (kl-klara schema)             │
└──────────────────────────────────────────┘
```

## Components

### Web Interface (`web/`)

- **Framework**: PHP with CodeIgniter
- **Entry point**: `web/index.php`
- **Purpose**: User-facing interface for submitting Yara rules, viewing results, and managing jobs
- **Controllers**:
  - `Login` — Authentication (session-based)
  - `Jobs` — Submit, view, restart, and delete scan jobs
  - `Profile` — User profile management
  - `Admin_tools` — Admin-only system management
  - `Advanced_search` — Admin-only MD5 hash search across jobs
  - `api/Jobs` — REST API for job management
  - `api/Users` — REST API for user management
- **Authentication**: Session-based for web UI; API key (`auth_code`) for REST API

### Dispatcher (`dispatcher/`)

- **Framework**: Python with Tornado (async HTTP server)
- **Entry point**: `dispatcher/klara-dispatcher`
- **Default port**: 8888 (configurable)
- **Purpose**: Central coordinator that manages job queues and worker communication
- **Internal API endpoints** (worker-facing, POST with `auth` parameter):
  - `/api/worker_fetch_available_jobs` — Returns jobs with status `new`
  - `/api/worker_assign_job` — Atomically assigns a job to a requesting worker (uses `SELECT FOR UPDATE`)
  - `/api/worker_save_results` — Receives scan results, updates database, sends email notifications
- **Database**: Connects to MySQL via PyMySQL
- **Notifications**: Sends email via SMTP when scan results are ready

### Worker (`worker/`)

- **Language**: Python
- **Entry point**: `worker/klara-worker`
- **Purpose**: Polls the dispatcher for available jobs, runs Yara scans, and returns results
- **Workflow**:
  1. Poll dispatcher for available jobs (`worker_fetch_available_jobs`)
  2. Check if the required scan repository exists on local filesystem
  3. Request job assignment (`worker_assign_job`)
  4. Write Yara rules to a temp file and validate them against `/dev/null`
  5. Execute Yara scan on the sample repository (multi-threaded, recursive)
  6. Pipe results through `head` to limit output (default: 1000 lines)
  7. Compute MD5 hashes for matched files
  8. Push results back to dispatcher (`worker_save_results`)
- **Configuration**: API key, dispatcher URL, Yara binary path, scan repository path, refresh interval

### Database

- **Engine**: MySQL (InnoDB)
- **Schema**: See [Database Schema](database-schema.md)
- **Shared by**: Web interface (via CodeIgniter) and Dispatcher (via PyMySQL)

## Data Flow

### Job Submission

1. User submits Yara rules via **web UI** or **REST API**
2. Web interface inserts a new row in `jobs` table with status `new`
3. Job description (JSON) includes the target `fileset_scan` path and `notify_email`

### Job Execution

1. **Worker** polls dispatcher at a configurable interval (default: 60s)
2. Dispatcher returns all jobs with status `new`
3. Worker checks if the requested repository path exists on its local filesystem
4. Worker requests job assignment — dispatcher atomically sets status to `assigned` using row-level locking
5. Worker receives the Yara rules and executes the scan
6. Worker pushes results (matches, MD5 hashes, execution time, errors/warnings) to dispatcher
7. Dispatcher saves results to database and sets status to `finished` or `yara_errors`
8. Dispatcher sends email notification to the job owner (if configured)

### Job Statuses

| Status | Description |
|--------|-------------|
| `new` | Job submitted, waiting for a worker |
| `assigned` | Job claimed by a worker, scan in progress |
| `finished` | Scan completed successfully |
| `yara_errors` | Scan completed with Yara errors |

## Security Model

### Web Authentication

| Level | Value | Description |
|-------|-------|-------------|
| Disabled | 0 | Unauthenticated user |
| Suspended | 1 | User suspended from system |
| Registered | 2 | Can view/add jobs, quotas enforced |
| Observer | 4 | Reserved (not used) |
| Power User | 8 | Can view/add jobs, quotas disabled |
| Admin | 16 | Full access |

### API Authentication

REST API requests authenticate via `auth_code` (POST parameter) matched against the `users.api_auth_code` column. Per-method permissions are stored in `users.api_perms` as a JSON array.

### Worker Authentication

Workers authenticate to the dispatcher using an `auth` token matched against the `agents` table.

## Filesystem Requirements

Each worker needs local access to the malware sample repositories. Repository paths are defined in the `scan_filesets` table and must exist on the worker's filesystem at `{virus_collection}/{fileset_scan}`.

A `repository_control.txt` file in each repository directory can optionally:
- **Redirect** the scan to an alternate path (`redirect_paths`)
- **Rewrite** result paths for display (`results_path_replace_pattern` / `results_path_replace_with`)

## Configuration Files

| Component | Config File | Key Settings |
|-----------|-------------|--------------|
| Dispatcher | `dispatcher/config.py` | `listen_port`, MySQL credentials, SMTP settings |
| Worker | `worker/config.py` | `api_location`, `api_key`, `yara_path`, `virus_collection` |
| Web | `web/application/config/database.php` | MySQL credentials |
| Web | `web/application/config/project_settings.php` | Project title, search limits |

