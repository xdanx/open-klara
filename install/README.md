# Installing Open KLara

This guide covers the installation of **Open KLara**, a community-driven fork of the original Kaspersky Lab KLara project.

## Requirements for running Open KLara:

- GNU/Linux (we recommend `Ubuntu 22.04.3` or latest LTS)
- DB Server: MariaDB
- Python 3.5+
- Python virtualenv package
- Yara (installed on workers)

Installing Klara consists of 4 parts:

- Database installation
- Worker installation
- Dispatcher installation
- Web interface installation

Components are connected between themselves as follows:

```
                              +----------+          +----------------+
                              |          |          |                |
                  +---------->+ Database +<--+      |     nginx      |
                  |           |          |   |      |   (optional)   |
                  |           +----------+   |      |                |   
           +------+------+                   |      +-------+--------+   
           |             |                   |              |             
    +----->|  Dispatcher | <---+             |              |            
    |      |             |     |             |              |            
    |      +------+------+     |             |              v            
    |             |            |             |      +-------+--------+
    |             |            |             |      |                |
    |             |            |             |      |                |
+---+----+   +----+---+   +----+---+         ^------+   Web server   |
|        |   |        |   |        |                |                |
| Worker |   | Worker |   | Worker |                |                |
|        |   |        |   |        |                +----------------+
+--------+   +--------+   +--------+


```
Workers connect to Dispatcher using a simple `HTTP REST API`. Dispatcher and the Web server 
connect the MySQL / MariaDB Database using TCP connections. Because of this, components can be installed on 
separated machines / VMs. The only requirements is that TCP connections are allowed between them.

# Installing on Windows

Since entire project is written in Python, Dispatcher and Workers can be set up to run in an Windows environment. Unfortunately, as we only support Ubuntu, instructions will be provided for this platforms, but other GNU/Linux flavors should be able to easily install Klara as well.

## Database installation

Please install a SQL database (we recommend MariaDB) and make it accessible for Dispatcher and Web Interface.

To create a new DB user, allowing access to `klara` database, for any hosts, identified by password `pass12345` use the following command:

```
##### For `klara` DB #####
# Please use random/secure password for user 'klara' on DB 'klara'
CREATE DATABASE klara;
CREATE USER 'klara'@'127.0.0.1' IDENTIFIED BY 'pass12345';
GRANT USAGE ON *.* TO 'klara'@'127.0.0.1' IDENTIFIED BY 'pass12345' WITH MAX_QUERIES_PER_HOUR 0 MAX_CONNECTIONS_PER_HOUR 0 MAX_UPDATES_PER_HOUR 0 MAX_USER_CONNECTIONS 0;
GRANT ALL PRIVILEGES ON `klara`.* TO 'klara'@'127.0.0.1';
GRANT ALL PRIVILEGES ON `klara`.* TO 'klara'@'localhost';
```

Once Dispatcher and Web Interfaces are set-up and configured to point to DB, the SQL DB needs to be created. Please run the SQL statements from [db_patches/db_schema.sql](db_patches/db_schema.sql) location:

```
mysql klara < db_schema.sql
```

## Dispatcher installation

Install the packages needed to run Dispatcher:
```
sudo apt -y install python3-venv git
```

We recommend running dispatcher on a non-privileged user. Create an user which will be responsible to run Worker as well as Dispatcher:

```
sudo groupadd -g 500 projects
sudo useradd -m -u 500 -g projects projects
```

Create a folder needed to store all Klara project files:

```
sudo mkdir /var/projects/
sudo chown projects:projects /var/projects/
```

Substitute to projects user and create the virtual env + folders needed to run the Dispatcher:

**Note**: From now on, all commands will be executed under `projects` user

```
su projects
mkdir /var/projects/klara/ -p
mkdir /var/projects/klara/logs/
# Create the virtual-env
python3 -m venv ~/.virtualenvs/klara
```

Clone the repository:

```bash
git clone https://github.com/xdanx/open-klara.git ~/klara-github-repo
```

Copy Dispatcher's files and install python dependencies:
```
cp -R ~/klara-github-repo/dispatcher /var/projects/klara/dispatcher/
cd /var/projects/klara/dispatcher/
cp config-sample.py config.py
source ~/.virtualenvs/klara/bin/activate
pip install -r ~/klara-github-repo/install/requirements.txt
```

Now fill in the settings in config.py:

```
# Setup the loglevel
logging_level  = "debug"

# What port should Dispatchers's REST API should listen to
listen_port = 8888

# Main settings for the master
# Set debug lvl
logging_level  = "debug"

# What port should the server listen to
listen_port = 8888

# Notification settings
# Do we want to sent out notification e-mails or not?
notification_email_enabled  = True
# FROM SMTP header settings
notification_email_from     = "klara-notify@example.com"
# SMTP server address
notification_email_smtp_srv = "127.0.0.1"

# MySQL / MariaDB settings for the Dispatcher to connect to the DB
mysql_host      = "127.0.0.1"
mysql_database  = "klara"
mysql_user      = "root"
mysql_password  = ""
```
Once settings are set, you can check Dispatcher is working by running the following commands:
```
sudo su projects
# We want to enable the virtualenv
source  source ~/venvs/klara/bin/activate
cd /var/projects/klara/dispatcher/
python3 ./klara-dispatcher
```
If everything went well, you should see:
```
[01/01/1977 13:37:00 AM][INFO]  ###### Starting KLara Job Dispatcher ######
```

In order to start Dispatcher automatically at boot, please check [Supervisor installation](supervisor.md)

Next step would be starting Dispatcher using `supervisorctl`:
```
sudo supervisorctl update
sudo supervisorctl start klara_dispatcher
```


# Worker installation

## Setting up an API key to be used by Workers

Each worker should have its own unique assigned API key. This helps maintaining strict access controls.

In order to insert a new API key to be used by a KLara worker, a new row needs to be inserted into DB table `agents` with the following entries:

* `description` - Short description for the worker (up to 63 chars)
* `auth` - API auth code (up to 63 chars)

```
mysql > use klara;
mysql > INSERT INTO agents value ("", "KLara worker description here", "API auth code here");
```

## Installing the Worker agent

Install the packages needed to run Worker:
```
sudo apt -y install python3-venv git
```

We recommend running Worker using a non-privileged user. Create an user which will be responsible to run Worker as well as Dispatcher:

```
sudo groupadd -g 500 projects
sudo useradd -m -u 500 -g projects projects
```

Create a folder needed to store all Klara project files:

```
sudo mkdir /var/projects/
sudo chown projects:projects /var/projects/
```

Substitute to projects user and create the virtual env + folders needed to run the Worker:

**Note**: From now on, all commands will be executed under `projects` user

```
su projects
mkdir /var/projects/klara/ -p
mkdir /var/projects/klara/logs/
# Create the virtual-env
python3 -m venv ~/.virtualenvs/klara
```

Clone the repository:

```bash
git clone https://github.com/xdanx/open-klara.git ~/klara-github-repo
```

Copy Worker's files to the newly created folder and install python dependencies:
```
cp -R ~/klara-github-repo/worker /var/projects/klara/worker/
cd /var/projects/klara/worker/
cp config-sample.py config.py
source ~/.virtualenvs/klara/bin/activate
pip install -r ~/klara-github-repo/install/requirements.txt
```

Now fill in the settings in config.py:

**Note**: use the API key you just inserted in table `agents` above;  
**Note**: Check [Worker Settings](#setting-up-workers-scan-repositories-and-virus-collection) to understand how to change settings
`virus_collection` and `virus_collection_control_file`

```
# Setup the loglevel
logging_level  = "debug"

# Api location for Dispatcher. No trailing slash !!
# Dispatcher is exposing the API at "/api/" location
api_location = "http://127.0.0.1:8888/api"
# The API key set up in the `agents` SQL table
api_key      = "test"

# Specify worker refresh time in seconds
refresh_new_jobs    = 60

# Yara settings
# Set-up path for Yara binary
yara_path           = "/opt/yara-latest/bin/yara"
# Use 8 threads to scan and scan dirs recursively
yara_extra_args     = "-p 8 -r"
# Where to store Yara temp results file
yara_temp_dir       = "/tmp/"

# md5sum settings
# binary location
md5sum_path         = "/usr/bin/md5sum"

# tail settings
# We only want the first 1k results
head_path_and_args  = ["/usr/bin/head", "-1000"]

# Virus collection should NOT have a trailing slash !!
virus_collection                = "/var/projects/klara/repository"
virus_collection_control_file   = "repository_control.txt"
```
Once the settings are set, you can check Worker is working by running the following commands:
```
sudo su projects
# We want to enable the virtualenv
source ~/.virtualenvs/klara/bin/activate
cd /var/projects/klara/worker/
python3 ./klara-worker
```

If everything went well, you should see:
```
[01/01/1977 13:37:00 AM][INFO]  ###### Starting KLara Worker ######
```

In order to start Worker automatically at boot, please check [Supervisor installation](supervisor.md)

Next step would be starting Worker using `supervisorctl`:
```
sudo supervisorctl update
sudo supervisorctl start klara_worker 
```
## Installing Yara on worker machines

Install the required dependencies:
```
sudo apt -y install libtool automake libjansson-dev libmagic-dev libssl-dev build-essential pkg-config

#
# Get the latest stable version of yara from https://github.com/virustotal/yara/releases
# Usually it's good practice to check the hash of the archive you download, but here we can't, since it's from GH
#

wget https://github.com/VirusTotal/yara/archive/vx.x.x.tar.gz
cd yara-3.x.x
./bootstrap.sh

./configure --prefix=/opt/yara-x.x.x --enable-address-sanitizer --enable-dotnet --enable-macho --enable-dex
make -j4
sudo make install
```

Now you should have Yara version installed on `/opt/yara-x.x.x/`

Create a symlink to the latest version, so when we update it, workers don't have to be reconfigured / restarted:
```
# Symlink to the actual folder
cd /opt/
ln -s yara-3.x.x/ yara-latest
```

## Setting up worker's scan repositories and virus collection

Each time workers contact Dispatcher in order to check for new jobs, will verify first if they can execute them. Klara was designed such as:
* each worker agent has a (root) virus collection where all the scan repositories should exist (setting `virus_collection` from `config.py`)
* multiple `scan repositories` will be checked by KLara workers when trying to accept a job. (for example, if one user wants to scan `/clean` repository, a Worker agent will try to check if it's capable of scanning it, by checking its `virus_collection` folder )
* in order to check if it's capable of scanning a particular `scan repository`, Worker checks if the collection control file exists (setting `virus_collection_control_file` from `config.py`) at location: `virus_collection` + `scan repository` + / + `virus_collection_control_file`.

Basically, if a new job to scan `/mach-o_collection` is to be picked up by a free Worker with the following `config.py` settings:

```
virus_collection                = "/mnt/nas/klara/repository"
virus_collection_control_file   = "repo_ctrl.txt"
``` 
then that Worker will check if it has the following file and folders structures:
```
/mnt/nas/klara/repository/mach-o_collection/repo_ctrl.txt
```

If this file exists at this particular path, then the Worker will accept the job and start the Yara scan with the specified job rules, searching files in `/var/projects/klara/repository/mach-o_collection/`

It is entirely up to you how to organize your scan repositories. An example of organizing directory `/mnt/nas/klara/repository` is as follows:

* `/clean`
* `/mz`
* `/elf`
* `/mach-o`
* `/vt`
* `/unknown`

## Filesystem optimisation

Running Klara (or Yara) on a fast enough machine is very important for stability and getting back results fast enough. Please check some tips and tricks for [filesystem optimisations](features_fs_optimisations.md)

## Repository control

KLara Workers check only if the repository control file exists in order to prepare the Yara scan. Contents of the file should only be an empty JSON string:

```
{}
```

Optionally, just for usability, you should write some info about the repository:

```
{"owner": "John Doe", "files_type": "elf", "repository_type": "APT"}
```

Scan Repository control file also has some interesting modifiers that can be used to manipulate Yara scans or results. For further info, please check [Advanced usage](features_advanced.md)

# Web interface installation

The KLara web interface is a **PHP-based application** built with the **CodeIgniter framework**. It provides a modern web UI for submitting Yara scan jobs, viewing results, and managing users.

## Prerequisites

Requirements for installing the web interface:

- **Web server**: Apache 2.4+ or Nginx 1.18+
- **PHP**: Version 7.4 (PHP 8 is not yet supported)
- **Database**: MariaDB/MySQL (already configured in previous steps)
- **Required PHP extensions**:

```bash
sudo apt install php php7.4-{fpm,mysqli,curl,gd,intl,pear,imagick,imap,memcache,pspell,sqlite3,tidy,xmlrpc,xsl,mbstring,apcu}
```

**Note**: If you need to install PHP 7.4 on newer systems, refer to: https://tecadmin.net/how-to-install-php-on-debian-12/

## Installation Steps

### 1. Copy Web Files

Copy the `/web/` folder from the cloned repository to your HTTP server document root:

```bash
# For Apache (default document root)
sudo cp -R ~/klara-github-repo/web /var/www/html/klara

# For Nginx (common document root)
sudo cp -R ~/klara-github-repo/web /usr/share/nginx/html/klara

# Set appropriate permissions
sudo chown -R www-data:www-data /var/www/html/klara  # Apache
# OR
sudo chown -R www-data:www-data /usr/share/nginx/html/klara  # Nginx
```

### 2. Configure the Application

Navigate to the web directory and rename the sample configuration files:

```bash
cd /var/www/html/klara  # Adjust path as needed

# Rename configuration files
cp application/config/config.sample.php application/config/config.php
cp application/config/database.sample.php application/config/database.php
cp application/config/project_settings.sample.php application/config/project_settings.php
```

### 3. Update Configuration Files

**a) Edit `application/config/config.php`:**

```php
// Set your base URL (important!)
$config['base_url'] = 'http://your-server-ip/klara/';  // Adjust to your setup

// Generate and set encryption key (required for sessions)
// Generate a random 32-character key: openssl rand -hex 16
$config['encryption_key'] = 'your-32-character-encryption-key-here';
```

**b) Edit `application/config/database.php`:**

```php
$db['default'] = array(
    'hostname' => '127.0.0.1',
    'username' => 'klara',
    'password' => 'pass12345',  // Use the password you set during DB installation
    'database' => 'klara',
    'dbdriver' => 'mysqli',
    // ... other settings remain as default
);
```

**c) Edit `application/config/project_settings.php`:**

Configure project-specific settings like email notifications, project title, etc.

### 4. Web Server Configuration

**For Apache:**

Create a virtual host configuration file `/etc/apache2/sites-available/klara.conf`:

```apache
<VirtualHost *:80>
    ServerName your-server-ip
    DocumentRoot /var/www/html/klara

    <Directory /var/www/html/klara>
        Options Indexes FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/klara_error.log
    CustomLog ${APACHE_LOG_DIR}/klara_access.log combined
</VirtualHost>
```

Enable the site and required modules:

```bash
sudo a2enmod rewrite
sudo a2ensite klara
sudo systemctl restart apache2
```

**For Nginx:**

Create a server block configuration file `/etc/nginx/sites-available/klara`:

```nginx
server {
    listen 80;
    server_name your-server-ip;
    root /usr/share/nginx/html/klara;
    index index.php index.html;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/var/run/php/php7.4-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location ~ /\.ht {
        deny all;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/klara /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**Important**: For proper CodeIgniter routing, refer to:
- https://www.nginx.com/resources/wiki/start/topics/recipes/codeigniter/
- https://www.codeigniter.com/user_guide/installation/upgrade_303.html
- https://codeigniter.com/user_guide/libraries/encryption.html
- https://www.codeigniter.com/user_guide/database/configuration.html

## Accessing the Web Interface

Once installation is complete, you can access the KLara web interface:

### 1. Open Your Browser

Navigate to one of the following URLs (depending on your configuration):

- `http://your-server-ip/klara/` (if installed in a subdirectory)
- `http://your-server-ip/klara/index.php` (explicit entry point)
- `http://your-server-ip/` (if configured as the default site)

### 2. Login with Default Credentials

For your convenience, 2 `users`, 2 `groups` and 2 `scan repositories` have been created:

* Users (`users` DB table):

| Username      | Password                | Auth level     | Group ID     | Quota |
| ------------- |:-------------:          | :----------    | ---------    | :---- |
| admin         | `super_s3cure_password` | `16` (Admin)   | `2` (admins) | N/A (Admins don't have quota) |
| john          | `super_s3cure_password` | `4` (Observer) | `1` (main)   | 1000 scans / month |

* Groups (`users_groups` DB table):

| Group name    | `scan_filesets_list` (scan repositories) | Jail status |
| ------------- | :-------------                           | ----------- |
| main          | `[1,2]`                                  | 0 (OFF - Users are not jailed) |
| admins        | `[1,2]`                                  | 0 (OFF - Users are not jailed) |

* Scan Repositories (`scan_filesets` DB table):

| Scan Repository   |
| -------------     |
| /virus_repository |
| /_clean           |

### 3. Important Security Notes

⚠️ **CRITICAL**: After your first login, you **MUST**:

1. **Change all default passwords immediately**
2. **Delete or disable unused default accounts**
3. **Update the encryption key** in `config.php` to a secure random value
4. **Configure HTTPS** for production environments (not covered in this guide)
5. **Restrict database access** to only necessary hosts

### 4. Troubleshooting Web Interface Issues

**Problem: "404 Not Found" or blank page**
- Verify web server is running: `sudo systemctl status apache2` or `sudo systemctl status nginx`
- Check that `index.php` exists in the web root directory
- Verify file permissions: `ls -la /var/www/html/klara/index.php`
- Check web server error logs: `/var/log/apache2/error.log` or `/var/log/nginx/error.log`

**Problem: "Database connection failed"**
- Verify database credentials in `application/config/database.php`
- Test database connection: `mysql -h 127.0.0.1 -u klara -p klara`
- Ensure MariaDB/MySQL is running: `sudo systemctl status mariadb`

**Problem: "The application environment is not set correctly"**
- Check PHP version: `php -v` (must be 7.4)
- Verify all required PHP extensions are installed: `php -m`
- Check file permissions on the `application` directory

**Problem: CodeIgniter routing not working (URLs like `/index.php/jobs` fail)**
- For Apache: Ensure `mod_rewrite` is enabled and `.htaccess` is present
- For Nginx: Verify the `try_files` directive in your server block configuration
- Check the `base_url` setting in `application/config/config.php`

**Problem: "There is no index.html file"**
- This is **expected behavior**! KLara uses `index.php` (CodeIgniter framework), not static HTML files
- The `index.html` files in subdirectories are security placeholders to prevent directory listing
- Always access the application via `index.php` or through proper routing

For more info about Web features (creating / deleting users, user quotas, groups, auth levels, etc..), please check dedicated page [Web Features](features_web.md)

--------

## Getting Help

That's it! If you have any issues with installing this software:

- **Submit a bug report**: [GitHub Issues](https://github.com/xdanx/open-klara/issues)
- **Join our community**: [Telegram channel #open_klara](https://t.me/open_klara)
- **Ask questions**: [GitHub Discussions](https://github.com/xdanx/open-klara/discussions)
- **Contribute**: [Submit a Pull Request](https://github.com/xdanx/open-klara/pulls)

Happy hunting! 🎯


