# Process Management

KLara's Dispatcher and Worker scripts need to run as managed services. You can use either **supervisord** or **systemd** to automate starting, stopping, and restarting them.

## Option 1: supervisord

[supervisord](http://supervisord.org) is a process control system. Install it following the [official instructions](http://supervisord.org/installing.html).

Place the following configuration in your supervisord config directory (usually `/etc/supervisor/conf.d/klara.conf`):

### Dispatcher

```ini
[program:klara_dispatcher]
command=/home/projects/.virtualenvs/klara/bin/python klara-dispatcher
directory=/var/projects/klara/dispatcher
user=projects
autostart=true
autorestart=true
stdout_logfile=/var/projects/klara/logs/dispatcher.log
stderr_logfile=/var/projects/klara/logs/dispatcher.err
```

### Worker

```ini
[program:klara_worker1]
command=/home/projects/.virtualenvs/klara/bin/python klara-worker
directory=/var/projects/klara/worker
user=projects
autostart=true
autorestart=true
stdout_logfile=/var/projects/klara/logs/worker1.log
stderr_logfile=/var/projects/klara/logs/worker1.err
```

> **Tip**: To run multiple workers on the same machine, add additional `[program:]` sections with unique names and log files (e.g., `klara_worker2`, `klara_worker3`).

### Apply Changes

```bash
sudo supervisorctl update
sudo supervisorctl start all
```

## Option 2: systemd

[systemd](https://www.freedesktop.org/wiki/Software/systemd/) comes preinstalled on most modern Linux distributions (Ubuntu, Debian, Fedora, etc.).

Place service files in `/etc/systemd/system/`.

### Dispatcher (`klara_dispatcher.service`)

```ini
[Unit]
Description=KLara dispatcher

[Service]
ExecStart=/home/projects/.virtualenvs/klara/bin/python /var/projects/klara/dispatcher/klara-dispatcher
User=projects
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Worker (`klara_worker.service`)

```ini
[Unit]
Description=KLara worker

[Service]
ExecStart=/home/projects/.virtualenvs/klara/bin/python /var/projects/klara/worker/klara-worker
User=projects
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

> **Note**: `ExecStart` uses the Python binary from the virtual environment configured during installation. Ensure the `projects` user has execute permissions on the virtualenv's Python binary.

### Enable and Start Services

```bash
# Enable services to start on boot
sudo systemctl enable klara_worker.service klara_dispatcher.service

# Check service status
sudo systemctl status klara_worker.service
sudo systemctl status klara_dispatcher.service

# Start/stop/restart
sudo systemctl start klara_worker.service
sudo systemctl stop klara_worker.service
sudo systemctl restart klara_worker.service
```

