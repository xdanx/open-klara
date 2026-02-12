# Quick Start Guide

Get Open KLara running on a single machine in under 30 minutes.

## Prerequisites

- Ubuntu 22.04 LTS (or compatible GNU/Linux)
- MariaDB installed and running
- Python 3.5+
- Git

## 1. Set Up the Database

```bash
sudo mysql
```

```sql
CREATE DATABASE klara;
CREATE USER 'klara'@'127.0.0.1' IDENTIFIED BY 'CHANGE_ME';
GRANT ALL PRIVILEGES ON `klara`.* TO 'klara'@'127.0.0.1';
GRANT ALL PRIVILEGES ON `klara`.* TO 'klara'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Import the schema:

```bash
mysql klara < install/db_patches/db_schema.sql
```

## 2. Create a Service User

```bash
sudo groupadd -g 500 projects
sudo useradd -m -u 500 -g projects projects
sudo mkdir -p /var/projects/klara/logs
sudo chown -R projects:projects /var/projects/
```

## 3. Clone and Install

```bash
sudo su - projects
git clone https://github.com/xdanx/open-klara.git ~/klara-github-repo
python3 -m venv ~/.virtualenvs/klara
source ~/.virtualenvs/klara/bin/activate
pip install -r ~/klara-github-repo/install/requirements.txt
```

## 4. Start the Dispatcher

```bash
cp -R ~/klara-github-repo/dispatcher /var/projects/klara/dispatcher/
cd /var/projects/klara/dispatcher/
cp config-sample.py config.py
```

Edit `config.py` — set your database credentials (see [Configuration Reference](../reference/configuration.md#dispatcher-settings)):

```bash
python3 ./klara-dispatcher
```

You should see: `###### Starting KLara Job Dispatcher ######`

## 5. Start a Worker

Open a new terminal as the `projects` user:

```bash
source ~/.virtualenvs/klara/bin/activate
cp -R ~/klara-github-repo/worker /var/projects/klara/worker/
cd /var/projects/klara/worker/
cp config-sample.py config.py
```

First, create an API key for the worker:

```bash
mysql -u klara -p klara -e "INSERT INTO agents VALUES ('', 'Worker 1', 'my-api-key');"
```

Edit `config.py` — set `api_key = "my-api-key"` and your database credentials (see [Configuration Reference](../reference/configuration.md#worker-settings)):

```bash
python3 ./klara-worker
```

You should see: `###### Starting KLara Worker ######`

## 6. Set Up the Web Interface

See the full [Installation Guide](../how-to/installation.md#web-interface) for web server setup with Apache or Nginx.

## Next Steps

- [Installation Guide](../how-to/installation.md) — Production deployment, Yara setup, web server config
- [Configuration Reference](../reference/configuration.md) — All available options
