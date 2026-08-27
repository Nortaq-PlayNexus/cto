<div align="center">

# CTO Dashboard

**Engineering leadership visibility for GitHub organizations — repo health, team metrics, and tech stack oversight.**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-%3E%3D3.10-3776AB?logo=python&logoColor=white)](https://python.org)
[![Rich](https://img.shields.io/badge/Rich-13+-E91E63?logo=rich&logoColor=white)](https://github.com/Textualize/rich)

</div>

---

**CTO Dashboard** is a CLI tool that gives engineering leaders a real-time view into their GitHub organization. It scores repository health, tracks contributor activity, maps the tech stack, and flags stale projects — all from the terminal.

No SaaS. No dashboards to deploy. Just run `cto overview`.

---

## Features

### Repository health scoring

Every repo gets a 0–100 health score based on 15 weighted checks:

- Has README, LICENSE, CONTRIBUTING, SECURITY, CHANGELOG
- Has CI/CD workflows
- Has description and topics
- Recent push activity
- Open issue and PR load
- Has Docker support

Repos are ranked worst-first so you know where to focus.

### Team activity metrics

- Commits per contributor over a configurable lookback window (default: 30 days)
- Which repos each contributor is active in
- Per-repo commit counts
- Contributor leaderboard

### Tech stack analysis

- Language distribution across the entire organization (by bytes of code)
- Per-repository language breakdown
- Topic frequency analysis

### Stale repository detection

- Finds repos with no commits in N days (default: 90)
- Excludes archived repos automatically
- Sorted by inactivity duration

---

## Screenshots

| Preview | Description |
|---------|-------------|
| Terminal output screenshots coming soon | |

---

## Quick start

**Requirements:** Python 3.10+ and a GitHub token (optional, but recommended for rate limits).

```bash
# Install
pip install -e .

# Or just install dependencies
pip install -r requirements.txt

# Set your GitHub token (optional — enables higher rate limits)
export GITHUB_TOKEN=ghp_xxxxxxxxxxxx

# Run
cto overview --org Nortaq-PlayNexus
```

---

## Commands

### `cto overview` — Organization overview

```bash
cto overview --org Nortaq-PlayNexus
cto overview --org my-org --format json
```

Shows all repositories ranked by health score with a visual health bar.

### `cto repo <name>` — Deep-dive into a repository

```bash
cto repo military-anomaly-scanner --org Nortaq-PlayNexus
```

Shows full repo info: metadata, health checks, top contributors, and language breakdown.

### `cto team` — Contributor activity

```bash
cto team --org Nortaq-PlayNexus --days 30
```

Shows commit activity per contributor and per repo over the lookback window.

### `cto tech` — Tech stack

```bash
cto tech --org Nortaq-PlayNexus
```

Shows language distribution, topic frequency, and per-repo languages.

### `cto health` — Health report

```bash
cto health --org Nortaq-PlayNexus
cto health --org my-org --min-score 50
```

Detailed health report with failed checks flagged. Use `--min-score` to filter.

### `cto stale` — Stale repos

```bash
cto stale --org Nortaq-PlayNexus --days 90
```

Finds repos with no activity in the specified period.

---

## Configuration

CTO Dashboard looks for config in three places (later overrides earlier):

1. `config/default.json` — shipped with the project
2. `~/.config/cto-dashboard/config.json` — user-level overrides
3. `CTO_DASHBOARD_GITHUB_TOKEN` or `GITHUB_TOKEN` environment variables

### `config/default.json`

```json
{
  "default_org": "Nortaq-PlayNexus",
  "github_token": null
}
```

Set `default_org` to skip `--org` on every command.

---

## How health scoring works

Each repository is evaluated against 15 checks. Each check contributes a weighted score:

| Check | Points | What it looks for |
|---|---|---|
| Has CI | 15 | GitHub Actions workflows present |
| Recent activity | 15 | Push within 7/30/90/180 days |
| Has README | 10 | README.md in default branch |
| Low open issues | 10 | 0–5 issues = full marks |
| Has LICENSE | 8 | License field set on repo |
| Open PRs low | 7 | Fewer open PRs = better |
| Has description | 5 | Non-empty description |
| Has CONTRIBUTING | 5 | CONTRIBUTING.md present |
| Has issues enabled | 5 | Issues tab active |
| Has topics | 4 | Up to 5 topics counted |
| Has security policy | 4 | SECURITY.md present |
| Has wiki | 3 | Wiki enabled |
| Has CHANGELOG | 3 | CHANGELOG.md present |
| Has Docker | 3 | Dockerfile or docker-compose |
| Has CODE_OF_CONDUCT | 3 | CODE_OF_CONDUCT.md present |

Scores map to labels: **HEALTHY** (80+), **FAIR** (60–79), **AT RISK** (40–59), **CRITICAL** (<40).

---

## Requirements

- Python 3.10+
- `requests` — GitHub API calls
- `rich` — Terminal UI rendering
- GitHub account (token optional but recommended)

---

## Contributing

We welcome contributions! Please see:

- [Contributing Guide](CONTRIBUTING.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security Policy](SECURITY.md)

---

## License

[MIT](LICENSE) — PlayNexus
