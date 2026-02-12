# Open KLara

**Open KLara** is a community-driven fork of [KLara by Kaspersky Lab](https://github.com/KasperskyLab/klara) — a distributed system for scanning large malware collections with [Yara](https://github.com/VirusTotal/yara) rules.

> This project is maintained by the community and is not affiliated with Kaspersky Lab.

## Features

- **Web Interface** — Fire-and-forget Yara scans with email notifications ([docs](docs/reference/web-interface.md))
- **REST API** — Programmatic job submission and result retrieval ([docs](docs/reference/api.md))
- **Distributed Scanning** — Dispatcher-worker model that scales across commodity hardware ([architecture](docs/reference/architecture.md))

## Quick Start

See the [Quick Start Tutorial](docs/tutorials/quick-start.md) to get up and running.

For full installation instructions, see the [Installation Guide](docs/how-to/installation.md).

## Documentation

Full documentation lives in [`docs/`](docs/index.md), organized by the [Diátaxis framework](https://diataxis.fr/):

| Section | Description |
|---------|-------------|
| [Tutorials](docs/tutorials/) | Step-by-step guides for getting started |
| [How-To Guides](docs/how-to/) | Task-oriented guides (installation, advanced usage, process management) |
| [Reference](docs/reference/) | API, architecture, configuration, database schema |
| [Explanation](docs/explanation/) | Design decisions and performance concepts |

## Contributing

Contributions are welcome! Please open a PR or file an issue on [GitHub](https://github.com/xdanx/open-klara/issues).

- **Telegram**: [#open_klara](https://t.me/open_klara)
- **Issues**: [Report bugs](https://github.com/xdanx/open-klara/issues)
- **PRs**: [Contribute code](https://github.com/xdanx/open-klara/pulls)

## Credits

- **Original KLara**: [Kaspersky Lab's GReAT Team](https://github.com/KasperskyLab/klara) — Costin, Marco, Vitaly, Sergey, Alex@grep
- **Open KLara**: [xdanx](https://github.com/xdanx) (maintainer), [gajeshbhat](https://github.com/gajeshbhat) (maintainer)
- **Yara**: [VirusTotal](https://github.com/VirusTotal/yara)

## License

See [LICENSE](LICENSE) for details.

Happy hunting! 🎯
