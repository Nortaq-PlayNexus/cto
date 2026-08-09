"""CTO Dashboard — CLI entry point."""

import argparse
import sys

from cto_dashboard import __version__
from cto_dashboard.config.settings import load_config
from cto_dashboard.core.github import GitHubClient
from cto_dashboard.core.health import HealthScorer
from cto_dashboard.core.metrics import MetricsCollector
from cto_dashboard.ui.dashboard import Dashboard


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cto",
        description="Engineering leadership dashboard for GitHub organizations.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="command")

    overview = sub.add_parser("overview", help="Organization overview with health scores")
    overview.add_argument("--org", type=str, help="GitHub organization (overrides config)")
    overview.add_argument("--format", choices=["table", "json"], default="table", help="Output format")

    repo = sub.add_parser("repo", help="Deep-dive into a single repository")
    repo.add_argument("name", type=str, help="Repository name")
    repo.add_argument("--org", type=str, help="GitHub organization (overrides config)")

    team = sub.add_parser("team", help="Contributor activity and team metrics")
    team.add_argument("--org", type=str, help="GitHub organization (overrides config)")
    team.add_argument("--days", type=int, default=30, help="Lookback window in days (default: 30)")

    tech = sub.add_parser("tech", help="Tech stack analysis across the organization")
    tech.add_argument("--org", type=str, help="GitHub organization (overrides config)")

    health = sub.add_parser("health", help="Detailed health report for all repos")
    health.add_argument("--org", type=str, help="GitHub organization (overrides config)")
    health.add_argument("--min-score", type=int, default=0, help="Only show repos below this score (0-100)")

    stale = sub.add_parser("stale", help="Find repos with no recent activity")
    stale.add_argument("--org", type=str, help="GitHub organization (overrides config)")
    stale.add_argument("--days", type=int, default=90, help="Inactivity threshold in days (default: 90)")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    config = load_config()
    org = getattr(args, "org", None) or config.get("default_org")
    if not org:
        print("Error: --org flag or default_org in config required.", file=sys.stderr)
        return 1

    client = GitHubClient(org=org, token=config.get("github_token"))
    scorer = HealthScorer()
    collector = MetricsCollector(client)
    dashboard = Dashboard()

    if args.command == "overview":
        repos = client.list_repos()
        scored = scorer.score_repos(repos)
        if args.format == "json":
            dashboard.print_json(scored)
        else:
            dashboard.print_overview(org, scored)

    elif args.command == "repo":
        repo = client.get_repo(args.name)
        if not repo:
            print(f"Repository '{args.name}' not found in {org}.", file=sys.stderr)
            return 1
        health = scorer.score_repo(repo)
        contributors = client.get_repo_contributors(args.name)
        languages = client.get_repo_languages(args.name)
        dashboard.print_repo_detail(repo, health, contributors, languages)

    elif args.command == "team":
        repos = client.list_repos()
        activity = collector.collect_activity(repos, days=args.days)
        dashboard.print_team_metrics(org, activity, days=args.days)

    elif args.command == "tech":
        repos = client.list_repos()
        stack = collector.collect_tech_stack(repos)
        dashboard.print_tech_stack(org, stack)

    elif args.command == "health":
        repos = client.list_repos()
        scored = scorer.score_repos(repos)
        filtered = [r for r in scored if r["health_score"] < args.min_score] if args.min_score else scored
        dashboard.print_health_report(org, filtered)

    elif args.command == "stale":
        repos = client.list_repos()
        stale = collector.find_stale(repos, days=args.days)
        dashboard.print_stale_repos(org, stale, days=args.days)

    return 0


if __name__ == "__main__":
    sys.exit(main())
