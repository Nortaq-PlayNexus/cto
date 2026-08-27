# Contributing to CTO Dashboard

Thank you for your interest in contributing! CTO Dashboard is an open-source CLI tool for engineering leadership.

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) — participation is governed by it.

## Ways to Contribute

- **Report bugs** — open an issue with a clear reproduction.
- **Suggest features** — open an issue using the feature request template.
- **Improve documentation** — typos, missing examples, better guides.
- **Add health checks** — extend the scoring model with new checks.
- **Add tests** — improve coverage.

## Development Setup

```bash
git clone https://github.com/your-org/cto-dashboard.git
cd cto-dashboard
pip install -e .
cto overview --org my-org
```

## Code Standards

- **Python 3.10+** — type hints required.
- **Rich** for terminal output.
- Run tests before submitting PRs.

## Commit Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org):

```
feat: add Docker health check
fix: handle rate limit on large orgs
docs: update health scoring docs
```

## Opening a Pull Request

1. Create a branch from `main`.
2. Make focused, reviewable changes.
3. Open the PR with a clear description.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
