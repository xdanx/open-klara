# Advanced Usage

## Search for MD5 Hashes Across Jobs

Administrators can use the **Advanced Search** page to check how many KLara jobs matched a particular MD5 or list of MD5s. This is useful for identifying rules that generate similar results.

Access: `GET /index.php/jobs/advanced_search` (admin only)

## Configure Virus Collection Control Files

Each scan repository can contain a `repository_control.txt` file that modifies Yara scan behavior. The file uses JSON format with the following optional fields.

### `redirect_paths`

Redirects scanning to an alternative directory instead of the actual repository folder.

**Example**: If the control file is at `/mnt/storage/vircol/vt_samples/repository_control.txt` with:

```json
{
  "owner": "John Doe",
  "files_type": "elf",
  "repository_type": "APT",
  "redirect_paths": ["/mnt/nas/klara_bigger_collection/"]
}
```

KLara will scan `/mnt/nas/klara_bigger_collection/` instead of `/mnt/storage/vircol/vt_samples/`.

> **Note**: Only the first entry in `redirect_paths` is currently used. Multiple paths are reserved for future expansion.

### `results_path_replace_pattern` and `results_path_replace_with`

Controls how file paths appear in scan results. By default, results show full absolute paths. Use these fields to apply a `re.sub` pattern to simplify displayed paths.

The pattern is automatically prefixed with the scan repository's absolute path. Be careful with trailing slashes.

**Pattern examples** (assuming `virus_collection` = `/mnt/storage/vircol/`, repository = `/vt_samples`):

| Pattern | Generated `re.sub` | Effect |
|---------|-------------------|--------|
| `.*/` | `/mnt/storage/vircol/vt_samples.*/` | Strips full path, keeps filename |
| `/test/*` | `/mnt/storage/vircol/vt_samples/test/*` | Replaces only `/test/` subdirectory |
| `/` | `/mnt/storage/vircol/vt_samples/` | Strips prefix up to repository |
| `` (empty) | `/mnt/storage/vircol/vt_samples` | Same as above (no trailing slash) |

**Example control file**:

```json
{
  "owner": "John Doe",
  "files_type": "mixed",
  "repository_type": "APT",
  "results_path_replace_pattern": "/",
  "results_path_replace_with": "[KLara repository] => "
}
```

**Result output**:

```
apt_ZZ_unknown_rule [KLara repository] => 1.exe
apt_ZZ_unknown_rule [KLara repository] => 2.bin
apt_ZZ_unknown_rule [KLara repository] => 3.dll
```

> **Note**: `redirect_paths` takes precedence over `results_path_replace_pattern`. Only one `results_path_replace_pattern` can be defined per repository.

For implementation details, see the [Worker source code](https://github.com/KasperskyLab/klara/blob/master/worker/klara-worker#L120).

## Configure API Access

KLara provides a REST API for automating web actions. To configure API access for a user:

1. Set `api_status` to `1` in the `users` table
2. Assign an `api_auth_code` (API key)
3. Configure `api_perms` with a JSON list of allowed endpoints

See the [Web Interface Reference](../reference/web-interface.md) for the full `users` table schema.

