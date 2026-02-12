# Configuration Reference

All configurable options for Open KLara components.

## Dispatcher Settings

File: `dispatcher/config.py` (copy from `config-sample.py`)

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `logging_level` | string | `"debug"` | Log verbosity: `"debug"`, `"info"`, `"warning"`, `"error"` |
| `listen_port` | int | `8888` | Port for the Dispatcher REST API |
| `notification_email_enabled` | bool | `True` | Enable email notifications for scan results |
| `notification_email_from` | string | `"klara-notify@example.com"` | Sender address for notification emails |
| `notification_email_smtp_srv` | string | `"127.0.0.1"` | SMTP server address |
| `mysql_host` | string | `"127.0.0.1"` | MariaDB/MySQL server hostname |
| `mysql_database` | string | `"kl-klara"` | Database name |
| `mysql_user` | string | `"root"` | Database username |
| `mysql_password` | string | `""` | Database password |

## Worker Settings

File: `worker/config.py` (copy from `config-sample.py`)

### Connection

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `logging_level` | string | `"debug"` | Log verbosity: `"debug"`, `"info"`, `"warning"`, `"error"` |
| `api_location` | string | `"http://127.0.0.1:8888/api"` | Dispatcher API URL. **No trailing slash.** |
| `api_key` | string | `"test"` | Worker API key (must match an entry in the `agents` DB table) |
| `refresh_new_jobs` | int | `60` | Seconds between polling the Dispatcher for new jobs |

### Yara

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `yara_path` | string | `"/opt/yara-latest/bin/yara"` | Path to the Yara binary |
| `yara_extra_args` | string | `"-p 8 -r"` | Extra arguments passed to Yara (`-p` = threads, `-r` = recursive) |
| `yara_temp_dir` | string | `"/tmp/"` | Directory for temporary Yara result files |

### External Tools

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `md5sum_path` | string | `"/usr/bin/md5sum"` | Path to the `md5sum` binary |
| `head_path_and_args` | list | `["/usr/bin/head", "-1000"]` | Command and args to truncate results (first 1000 lines) |

### Scan Repositories

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `virus_collection` | string | `"/var/projects/klara/repository"` | Root path for scan repositories. **No trailing slash.** |
| `virus_collection_control_file` | string | `"repository_control.txt"` | Filename that marks a directory as a valid scan repository |

#### How Scan Repositories Work

When a job targets a scan repository (e.g., `/mach-o_collection`), the Worker checks:

```
{virus_collection}/{repository_name}/{virus_collection_control_file}
```

For example, with these settings:
```python
virus_collection = "/mnt/nas/klara/repository"
virus_collection_control_file = "repo_ctrl.txt"
```

The Worker looks for `/mnt/nas/klara/repository/mach-o_collection/repo_ctrl.txt`. If found, the Worker accepts the job.

#### Repository Control File Format

The control file must contain valid JSON. Minimal:

```json
{}
```

Optional metadata:

```json
{"owner": "John Doe", "files_type": "elf", "repository_type": "APT"}
```

#### Example Repository Layout

```
/mnt/nas/klara/repository/
├── clean/repo_ctrl.txt
├── mz/repo_ctrl.txt
├── elf/repo_ctrl.txt
├── mach-o/repo_ctrl.txt
├── vt/repo_ctrl.txt
└── unknown/repo_ctrl.txt
```

## Web Interface Settings

### Application Config

File: `web/application/config/config.php` (copy from `config.sample.php`)

Key settings to change:

| Setting | Default | Description |
|---------|---------|-------------|
| `base_url` | `''` | Full URL to your KLara installation (e.g., `http://your-server/klara/`) |
| `encryption_key` | `''` | **Required.** 32-character random key. Generate with: `openssl rand -hex 16` |
| `sess_driver` | `'database'` | Session storage driver |
| `sess_expiration` | `7200` | Session timeout in seconds |
| `sess_match_ip` | `TRUE` | Bind sessions to client IP |

> Most other settings in `config.php` are CodeIgniter framework defaults and rarely need changes.

### Database Config

File: `web/application/config/database.php` (copy from `database.sample.php`)

| Setting | Default | Description |
|---------|---------|-------------|
| `hostname` | `'localhost'` | Database server address |
| `username` | `'root'` | Database username |
| `password` | `''` | Database password |
| `database` | `''` | Database name (use `klara`) |
| `dbdriver` | `'mysqli'` | Database driver (keep as `mysqli`) |
| `char_set` | `'utf8'` | Character set |
| `dbcollat` | `'utf8_general_ci'` | Collation |

### Project Settings

File: `web/application/config/project_settings.php` (copy from `project_settings.sample.php`)

| Setting | Default | Description |
|---------|---------|-------------|
| `project_title` | `"GReAT KLara"` | Title displayed in the web interface |
| `search_md5s_limit` | `11000` | Maximum number of MD5 hashes a user can search for |

## Database Tables

### Default Users

| Username | Password | Auth Level | Group |
|----------|----------|------------|-------|
| `admin` | `super_s3cure_password` | `16` (Admin) | admins |
| `john` | `super_s3cure_password` | `4` (Observer) | main |

⚠️ **Change all default passwords immediately.**

### Default Groups

| Group | Scan Repositories | Jail Status |
|-------|-------------------|-------------|
| main | `[1,2]` | OFF |
| admins | `[1,2]` | OFF |

### Default Scan Repositories

| ID | Path |
|----|------|
| 1 | `/virus_repository` |
| 2 | `/_clean` |

