# Web Interface Reference

KLara's web interface is a PHP-based application built with the CodeIgniter framework.

## URL Structure

| URL | Description |
|-----|-------------|
| `http://your-server/klara/index.php` | Main entry point |
| `http://your-server/klara/` | With URL rewriting enabled |

## Application Architecture

- **Entry point**: `web/index.php`
- **Framework**: CodeIgniter (PHP MVC)
- **Views**: `web/application/views/` (dynamic PHP templates)
- **Controllers**: `web/application/controllers/`
- **Models**: `web/application/models/`

> **Note**: `index.html` files in subdirectories are security placeholders that prevent directory listing — they are not the actual web interface.

## Pages

| Page | URL | Access |
|------|-----|--------|
| Dashboard | `/index.php/jobs` | All users |
| Submit New Job | `/index.php/jobs/add` | All users |
| Job Details | `/index.php/jobs/view/[job_id]` | All users |
| Advanced Search | `/index.php/jobs/advanced_search` | Admin only |
| Admin Tools | `/index.php/admin_tools` | Admin only |

## Scan Repositories

Scan repositories are defined in the `scan_filesets` database table. This table controls which repositories users see when submitting a new job via `index.php/jobs/add`.

Every folder under a worker's `virus_collection` path must have a corresponding entry in `scan_filesets`, otherwise users cannot submit jobs for that repository.

**Example**: If a worker has `virus_collection` set to `/mnt/storage/vircol/` with subfolders `/vt_samples/`, `/virus_repository/`, and `/_clean/`, all three must be added to `scan_filesets`.

## User Groups

Groups control:

| Column | Purpose |
|--------|---------|
| `name` | Group name |
| `scan_filesets_list` | JSON list of allowed scan repository IDs |
| `jail_users` | `0` = can see other members' jobs; `1` = sees own jobs only |

> **Note**: Admin users always see all submitted jobs regardless of jail settings.

## Users

### Database Schema (`users` table)

| Column | Type | Description |
|--------|------|-------------|
| `username` | varchar(63) | Login handle |
| `pass` | string | BCRYPT password hash |
| `desc` | varchar(127) | User description |
| `auth` | int | Authorization level (see below) |
| `api_auth_code` | string | API authentication key |
| `api_perms` | JSON | Allowed API endpoints |
| `api_status` | int | `0` = API disabled |
| `group_cnt` | int | Group ID (one group per user) |
| `notify_email` | string | Notification email for job completion |
| `quota_searches` | int | Maximum searches per month |

### Authorization Levels

| Level | Role | Description |
|-------|------|-------------|
| 0 | disabled | Unauthenticated user |
| 1 | suspended | User suspended from system |
| 2 | registered | Can view/add jobs, quotas enforced |
| 4 | observer | Not used |
| 8 | poweruser | Can view/add jobs, quotas disabled |
| 16 | admin | Full access |

> **Recommendation**: For team members, use `poweruser` (level 8) in a group with `jail` set to `0`.

### User Management

There is no admin UI for user management. Use SQL statements directly, or use the admin helper tools:

- **Generate password**: `GET /index.php/admin_tools/gen_pass` — returns a random password with its BCRYPT hash. See [`KLsecurity` model](https://github.com/xdanx/open-klara/blob/master/web/application/models/Klsecurity.php) for password complexity settings.

- **Bulk create users**: `GET /index.php/admin_tools/generate_users` — generates username/password pairs and SQL statements from the `$users_emails` array in [`Admin_tools.php`](https://github.com/xdanx/open-klara/blob/master/web/application/controllers/Admin_tools.php#L43).

  ```php
  $users_emails = array('john@example.com', 'doe@example.com', 'nsa@example.com');
  ```

### Quotas

For users below `poweruser` level, quotas are enforced via three columns:

| Column | Purpose |
|--------|---------|
| `quota_searches` | Max jobs per month |
| `searches_curr_month` | Jobs submitted this month |
| `quota_curr_month` | Month the counter applies to |

Quotas reset automatically at the beginning of each month.

## Shareable Links

Job results can be shared across groups (including jailed users) via shareable links. These are generated automatically when a job is created and can be found on the job details page. Any authenticated KLara user with the link can view the results.

## REST API

KLara provides a REST API for automating web actions. Each user can be assigned an API key with endpoint-specific permissions configured via the `api_perms` JSON field in the `users` table.

See [Advanced Usage](../how-to/advanced-usage.md) for API configuration details.

