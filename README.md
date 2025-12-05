# Open KLara   

**Open KLara** is a community-driven fork of the original [KLara project by Kaspersky Lab](https://github.com/KasperskyLab/klara), aimed at helping Threat Intelligence researchers hunt for new malware using [Yara](https://github.com/VirusTotal/yara).

> **Note**: This project is maintained by the community and in no way affiliated with Kaspersky Lab. For the original project, see [KasperskyLab/klara](https://github.com/KasperskyLab/klara).

In order to hunt efficiently for malware, one needs a large collection of samples to search over. 
Researchers usually need to fire a Yara rule over a collection / set of malicious files and then get the results back. 
In some cases, the rule needs adjusting. Unfortunately, scanning a large collection of files takes time. 
Instead, if a custom architecture is used, scanning 10TB of files can take around 30 minutes.

Open KLara is a distributed system written in Python & PHP, allows researchers to scan one or more Yara rules
over collections with samples, getting notifications by e-mail as well as the web interface when scan results are ready.

# Features

- Modern web interface, allowing researchers to "fire and forget" their rules, getting back results by [e-mail / API](/install/features_web.md)
- Powerful API, allowing for automatic Yara jobs submissions, checking their status and getting back results. API Documentation will be released soon.
- Distributed system, running on commodity hardware, easy to deploy and implement.

# Architecture

Open KLara leverages Yara's power, distributing scans using a dispatcher-worker model. Each worker server connects to a dispatcher
trying to check if new jobs are available. If a new job is indeed available, it checks to see if the required scan repository is
available on its own filesystem and, if it is, it will start the Yara scan with the rules submitted by the researcher 

The main issue Open KLara tries to solve is running Yara jobs over a large collection of malware samples ( > 1TB) in a reasonable amount of time.

# Installing Open KLara

Please refer to the comprehensive installation instructions outlined [here](/install/README.md).

## Quick Start - Accessing the Web Interface

After installation, the Open KLara web interface can be accessed through your web browser:

1. **Default URL**: `http://your-server-ip/` or `http://your-server-ip/index.php`
2. **Default Credentials**:
   - **Admin User**: `admin` / `super_s3cure_password`
   - **Regular User**: `john` / `super_s3cure_password`

   ⚠️ **Important**: Change these default passwords immediately after first login!

3. **Web Interface Structure**:
   - The web interface is built with **PHP** and the **CodeIgniter framework**
   - Entry point: `web/index.php` (not a static HTML file)
   - Requires a web server (Apache/Nginx) with PHP 7.4+ support

For detailed installation and configuration instructions, see the [Web Interface Installation](/install/README.md#web-interface-installation) section.



If you have any issues with installing this software, please create an issue on GitHub.

# Contributing and Reporting Issues

Anyone is welcome to contribute to **Open KLara**! Please submit a PR and we will review it.

## Community Resources

- **Telegram Channel**: [#open_klara](https://t.me/open_klara) - Join our community discussions
- **GitHub Issues**: [Report bugs and request features](https://github.com/xdanx/open-klara/issues)
- **GitHub Discussions**: Share ideas and ask questions
- **Pull Requests**: [Contribute code improvements](https://github.com/xdanx/open-klara/pulls)

## How to Contribute

1. Fork the repository: `https://github.com/xdanx/open-klara`
2. Create a feature branch following the naming convention (see repository contribution rules)
3. Make your changes with clear, descriptive commit messages
4. Submit a pull request with a detailed description of your changes
5. Participate in the code review process

For bug reports, please use GitHub's Issues feature and include:
- Your environment (OS, Python version, PHP version)
- Steps to reproduce the issue
- Expected vs actual behavior
- Relevant logs or error messages

# Credits

The **Open KLara** project would like to thank:

## Original KLara Project
- **Kaspersky Lab's GReAT Team** - For creating the original KLara project
- Costin, Marco, Vitaly, Sergey
- Current, former and future GReAT members
- Alex@grep

## Open KLara Community
- **xdanx** - Project maintainer
- **gajeshbhat** - Co-maintainer

## Special Thanks
- [VirusTotal](https://github.com/VirusTotal/yara) - For the amazing Yara project
- The open-source community for their continued support and contributions

Happy hunting! 🎯
