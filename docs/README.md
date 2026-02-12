# Open KLara Documentation

Welcome to the **Open KLara** documentation — your guide to deploying and operating a distributed Yara scanner for threat intelligence.

This documentation follows the [Diátaxis framework](https://diataxis.fr/), organizing content into four categories based on how you'll use it.

---

## Where to Start

**New to Open KLara?** Follow this path:

1. [Quick Start Guide](tutorials/quick-start.md) — Get a working setup in minutes
2. [Architecture Overview](reference/architecture.md) — Understand how the components fit together
3. [Installation Guide](how-to/installation.md) — Deploy in production

**Already using Open KLara?** Jump to what you need:

- [Configuration Reference](reference/configuration.md) — All settings for Dispatcher, Worker, and Web
- [REST API Reference](reference/api.md) — Automate job management
- [Advanced Usage](how-to/advanced-usage.md) — MD5 search, repository control files, Yara options
- [Process Management](how-to/process-management.md) — Run with supervisord or systemd

---

## Tutorials

> **Learning-oriented** — Step-by-step lessons that guide you from zero to a working setup.

Tutorials walk you through complete workflows, explaining concepts along the way. Start here if you're new.

- [Quick Start Guide](tutorials/quick-start.md) — Set up Open KLara and run your first scan

## How-To Guides

> **Problem-oriented** — Practical recipes for specific tasks.

How-to guides assume basic familiarity with Open KLara and focus on solving particular problems.

- [Installation Guide](how-to/installation.md) — Full production deployment (database, dispatcher, worker, web)
- [Advanced Usage](how-to/advanced-usage.md) — MD5 search, repository control files, Yara options
- [Process Management](how-to/process-management.md) — Run services with supervisord or systemd

## Reference

> **Information-oriented** — Precise technical descriptions to consult as needed.

Reference docs describe the system's components, APIs, and configuration. They are designed to be looked up, not read cover to cover.

- [Architecture](reference/architecture.md) — System components, data flow, and design
- [Configuration](reference/configuration.md) — All settings for Dispatcher, Worker, and Web Interface
- [REST API](reference/api.md) — Endpoints for jobs and users
- [Database Schema](reference/database-schema.md) — Tables, columns, and relationships
- [Web Interface](reference/web-interface.md) — Pages, URL structure, and scan repositories

## Explanation

> **Understanding-oriented** — Background, context, and design rationale.

Explanations help you understand *why* things work the way they do and make informed decisions about your deployment.

- [Performance & Filesystem Optimizations](explanation/performance.md) — SSD RAID, XFS tuning, and benchmarks

---

## Quick Links

- [GitHub Repository](https://github.com/xdanx/open-klara)
- [Report Issues](https://github.com/xdanx/open-klara/issues)
- [Telegram Community](https://t.me/open_klara)

