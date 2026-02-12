# Installation Guide

Complete installation instructions for Open KLara in a production environment.

> **Just want to try it out?** See the [Quick Start Guide](../tutorials/quick-start.md).

## Architecture Overview

```
                          +----------+          +----------------+
                          |          |          |                |
              +---------->+ Database +<--+      |     nginx      |
              |           |          |   |      |   (optional)   |
              |           +----------+   |      +-------+--------+
       +------+------+                   |              |
       |             |                   |              v
+----->|  Dispatcher | <---+             |      +-------+--------+
|      +------+------+     |             |      |                |
|             |            |             +------+   Web server   |
+--------+ +--+----+ +----+---+                |                |
| Worker | | Worker | | Worker |                +----------------+
+--------+ +-------+ +--------+
```

Workers connect to the Dispatcher via HTTP REST API. The Dispatcher and Web server connect to MariaDB via TCP. All components can run on separate machines.

## Requirements

- GNU/Linux (Ubuntu 22.04 LTS recommended)
- MariaDB
- Python 3.5+ with `python3-venv`
- Git
- Yara (on worker machines)

## Database Setup

Install MariaDB and create the KLara database:

```sql
CREATE DATABASE klara;
CREATE USER 'klara'@'127.0.0.1' IDENTIFIED BY 'YOUR_SECURE_PASSWORD';
GRANT USAGE ON *.* TO 'klara'@'127.0.0.1';
GRANT ALL PRIVILEGES ON `klara`.* TO 'klara'@'127.0.0.1';
GRANT ALL PRIVILEGES ON `klara`.* TO 'klara'@'localhost';
```

Import the schema:

```bash
mysql klara < install/db_patches/db_schema.sql
```

## System User Setup

Create a dedicated non-privileged user:

```bash
sudo apt -y install python3-venv git
sudo groupadd -g 500 projects
sudo useradd -m -u 500 -g projects projects
sudo mkdir -p /var/projects/klara/logs
sudo chown -R projects:projects /var/projects/
```

All remaining commands run as the `projects` user:

```bash
su - projects
git clone https://github.com/xdanx/open-klara.git ~/klara-github-repo
python3 -m venv ~/.virtualenvs/klara
source ~/.virtualenvs/klara/bin/activate
pip install -r ~/klara-github-repo/install/requirements.txt
```

## Dispatcher Installation

```bash
cp -R ~/klara-github-repo/dispatcher /var/projects/klara/dispatcher/
cd /var/projects/klara/dispatcher/
cp config-sample.py config.py
```

Edit `config.py` with your settings. See [Dispatcher Settings](../reference/configuration.md#dispatcher-settings) for all options.

Verify it starts:

```bash
source ~/.virtualenvs/klara/bin/activate
python3 ./klara-dispatcher
# Expected: "[...][INFO]  ###### Starting KLara Job Dispatcher ######"
```

## Worker Installation

### Create a Worker API Key

Each worker needs a unique API key in the `agents` database table:

```sql
INSERT INTO agents VALUES ('', 'Worker description', 'YOUR_API_KEY');
```

### Install the Worker

```bash
cp -R ~/klara-github-repo/worker /var/projects/klara/worker/
cd /var/projects/klara/worker/
cp config-sample.py config.py
```

Edit `config.py` with your API key and settings. See [Worker Settings](../reference/configuration.md#worker-settings) for all options.

Verify it starts:

```bash
source ~/.virtualenvs/klara/bin/activate
python3 ./klara-worker
# Expected: "[...][INFO]  ###### Starting KLara Worker ######"
```

## Installing Yara

Install build dependencies on each worker machine:

```bash
sudo apt -y install libtool automake libjansson-dev libmagic-dev libssl-dev build-essential pkg-config
```

Download the [latest stable release](https://github.com/virustotal/yara/releases) and build:

```bash
wget https://github.com/VirusTotal/yara/archive/v4.x.x.tar.gz
tar xzf v4.x.x.tar.gz && cd yara-4.x.x
./bootstrap.sh
./configure --prefix=/opt/yara-4.x.x --enable-dotnet --enable-macho --enable-dex
make -j4
sudo make install
```

Create a version-independent symlink so workers don't need reconfiguration on upgrades:

```bash
sudo ln -s /opt/yara-4.x.x /opt/yara-latest
```

## Web Interface

The web interface is a PHP application built with CodeIgniter.

### Prerequisites

```bash
sudo apt install php php7.4-{fpm,mysqli,curl,gd,intl,mbstring,xml}
```

> **Note**: For PHP 7.4 on newer systems, see https://tecadmin.net/how-to-install-php-on-debian-12/

### Copy and Configure

```bash
# Apache
sudo cp -R ~/klara-github-repo/web /var/www/html/klara
sudo chown -R www-data:www-data /var/www/html/klara

# Nginx
sudo cp -R ~/klara-github-repo/web /usr/share/nginx/html/klara
sudo chown -R www-data:www-data /usr/share/nginx/html/klara
```

Rename the sample config files:

```bash
cd /var/www/html/klara  # adjust path for Nginx
cp application/config/config.sample.php application/config/config.php
cp application/config/database.sample.php application/config/database.php
cp application/config/project_settings.sample.php application/config/project_settings.php
```

Edit each config file. See [Web Interface Settings](../reference/configuration.md#web-interface-settings) for details.

### Web Server Configuration

<details>
<summary>Apache virtual host</summary>

Create `/etc/apache2/sites-available/klara.conf`:

```apache
<VirtualHost *:80>
    ServerName your-server-ip
    DocumentRoot /var/www/html/klara
    <Directory /var/www/html/klara>
        AllowOverride All
        Require all granted
    </Directory>
</VirtualHost>
```

```bash
sudo a2enmod rewrite
sudo a2ensite klara
sudo systemctl restart apache2
```

</details>

<details>
<summary>Nginx server block</summary>

Create `/etc/nginx/sites-available/klara`:

```nginx
server {
    listen 80;
    server_name your-server-ip;
    root /usr/share/nginx/html/klara;
    index index.php;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/var/run/php/php7.4-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location ~ /\.ht { deny all; }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/klara /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx
```

</details>

### Default Credentials

| Username | Password | Auth Level | Group |
|----------|----------|------------|-------|
| admin | `super_s3cure_password` | Admin (16) | admins |
| john | `super_s3cure_password` | Observer (4) | main |

⚠️ **Change all default passwords immediately after first login.**

## Process Management

For production, run the Dispatcher and Workers as managed services using **supervisord** or **systemd**. See the [Process Management Guide](process-management.md) for complete configuration.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| 404 / blank page | Check web server is running; verify `index.php` exists; check file permissions and error logs |
| Database connection failed | Verify credentials in `database.php`; test with `mysql -h 127.0.0.1 -u klara -p klara`; check MariaDB is running |
| CodeIgniter routing broken | Apache: enable `mod_rewrite` + `.htaccess`; Nginx: check `try_files` directive; verify `base_url` in `config.php` |
| PHP errors | Verify PHP 7.4 with `php -v`; check extensions with `php -m` |

## Getting Help

- [GitHub Issues](https://github.com/xdanx/open-klara/issues) — Bug reports
- [Telegram #open_klara](https://t.me/open_klara) — Community chat
- [GitHub Discussions](https://github.com/xdanx/open-klara/discussions) — Questions
