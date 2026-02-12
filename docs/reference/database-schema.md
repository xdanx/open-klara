# Database Schema

Open KLara uses a MySQL database (default name: `kl-klara`) with InnoDB tables. The schema is defined in [`install/db_patches/db_schema.sql`](../../install/db_patches/db_schema.sql).

## Tables

### `users`

Stores user accounts for both web UI and API access.

| Column | Type | Description |
|--------|------|-------------|
| `cnt` | int (PK, auto-increment) | User ID |
| `username` | varchar(63), unique | Login username |
| `pass` | varchar(63) | Bcrypt password hash |
| `auth` | int, default 0 | Authorization level (see below) |
| `desc` | varchar(127) | User description |
| `api_auth_code` | varchar(127), unique, nullable | API authentication token |
| `api_perms` | varchar(511) | JSON array of allowed API methods |
| `api_status` | int, default 0 | API access enabled (1) or disabled (0) |
| `group_cnt` | int, default 1 | Foreign key to `users_groups.cnt` |
| `notify_email` | varchar(127) | Email for job notifications |
| `quota_searches` | int, default 0 | Monthly scan quota (0 = unlimited) |
| `quota_curr_month` | varchar(15) | Current month for quota tracking |
| `searches_curr_month` | int, default 0 | Scans used this month |
| `dateadded` | timestamp | Account creation date |
| `ip_last_login` | int unsigned, default 0 | Last login IP (as integer) |

**Auth levels:** 0 = disabled, 1 = suspended, 2 = registered, 4 = observer, 8 = power user, 16 = admin.

**Default users:**
- `admin` (auth=16, group=admins) — Administrator
- `john` (auth=4, group=main, quota=1000) — Regular user

### `users_groups`

Defines user groups that control which scan repositories are accessible.

| Column | Type | Description |
|--------|------|-------------|
| `cnt` | int (PK, auto-increment) | Group ID |
| `name` | varchar(63) | Group name |
| `scan_filesets_list` | varchar(128) | JSON array of allowed `scan_filesets.id` values |
| `jail_users` | int, default 1 | If 1, users can only see their own jobs |

**Default groups:**
- `main` (cnt=1) — Access to repositories [1, 2], no jail
- `admins` (cnt=2) — Access to repositories [1, 2], no jail

### `jobs`

Stores Yara scan jobs submitted by users.

| Column | Type | Description |
|--------|------|-------------|
| `id` | int (PK, auto-increment) | Job ID |
| `description` | varchar(1000) | JSON object with job metadata (fileset_scan, notify_email, execution_time, etc.) |
| `results` | mediumblob | Raw Yara scan output |
| `rules` | mediumblob | Yara rule(s) text |
| `status` | varchar(30), default `'new'` | Job status: `new`, `assigned`, `finished`, `yara_errors` |
| `matched_files` | int, default -1 | Number of files matched (-1 = not yet scanned) |
| `owner` | varchar(127) | Owner username (denormalized) |
| `owner_id` | int, default -1 | Foreign key to `users.cnt` |
| `owner_group_id` | int, default -1 | Owner's group at submission time |
| `agent_id` | int, default -1 | Foreign key to `agents.id` (worker that processed the job) |
| `start_time` | timestamp | Job submission time |
| `finish_time` | varchar(31) | Scan completion time |
| `share_key` | varchar(65), unique, nullable | Key for sharing job results via URL |

**Indexes:** Primary key on `id`, unique index on `share_key`.

### `jobs_hashes`

Stores MD5 hashes of files matched by completed scan jobs.

| Column | Type | Description |
|--------|------|-------------|
| `cnt` | int (PK, auto-increment) | Row ID |
| `job_id` | int | Foreign key to `jobs.id` |
| `hash_md5` | varchar(32) | MD5 hash of a matched file |

**Indexes:** Unique composite index on (`job_id`, `hash_md5`).

### `agents`

Stores worker (agent) authentication credentials.

| Column | Type | Description |
|--------|------|-------------|
| `id` | int (PK, auto-increment) | Agent ID |
| `description` | varchar(63) | Agent description |
| `auth` | varchar(63) | Authentication token used by the worker |

### `scan_filesets`

Defines the malware sample repositories available for scanning.

| Column | Type | Description |
|--------|------|-------------|
| `id` | int (PK, auto-increment) | Fileset ID |
| `entry` | varchar(127) | Repository path (e.g., `/virus_repository`) |

**Default entries:**
- ID 1: `/virus_repository`
- ID 2: `/_clean`

### `ci_sessions`

CodeIgniter session storage for the web interface.

| Column | Type | Description |
|--------|------|-------------|
| `id` | varchar(128) | Session ID |
| `ip_address` | varchar(45) | Client IP address |
| `timestamp` | int unsigned, default 0 | Last activity timestamp |
| `data` | blob | Serialized session data |

**Indexes:** Composite primary key on (`id`, `ip_address`), index on `timestamp`.

### `ci_logs`

Application audit log for the web interface.

| Column | Type | Description |
|--------|------|-------------|
| `cnt` | int (PK, auto-increment) | Log entry ID |
| `type` | varchar(63) | Log level: `info`, `alert`, `warn`, `error` |
| `module` | varchar(63) | Source module (e.g., `klsecurity`, `jobs/add`) |
| `data` | varchar(511) | Log message |
| `ip` | int unsigned | Client IP (as integer) |
| `user_id` | int | User who triggered the event |
| `date` | timestamp | Event timestamp |

## Entity Relationships

```
users ──────┐
  │         │ (owner_id)
  │         ▼
  │       jobs ──────── jobs_hashes
  │         │              (job_id → jobs.id)
  │         │ (agent_id)
  │         ▼
  │       agents
  │
  │ (group_cnt)
  ▼
users_groups ──── scan_filesets
           (scan_filesets_list references scan_filesets.id)
```

> **Note:** Foreign keys are enforced at the application level, not via database constraints.

