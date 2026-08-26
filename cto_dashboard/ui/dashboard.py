"""Rich terminal dashboard for CTO Dashboard."""

import json
from datetime import datetime, timezone

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


def _health_bar(score: int) -> Text:
    if score >= 80:
        color = "green"
        label = "HEALTHY"
    elif score >= 60:
        color = "yellow"
        label = "FAIR"
    elif score >= 40:
        color = "dark_orange"
        label = "AT RISK"
    else:
        color = "red"
        label = "CRITICAL"

    filled = score // 5
    bar = "█" * filled + "░" * (20 - filled)
    return Text(f"{bar} {score}/100 [{label}]", style=color)


def _format_size(kb: int) -> str:
    if kb < 1024:
        return f"{kb} KB"
    if kb < 1024 * 1024:
        return f"{kb / 1024:.1f} MB"
    return f"{kb / (1024 * 1024):.1f} GB"


def _time_ago(iso_str: str) -> str:
    if not iso_str:
        return "never"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        delta = datetime.now(timezone.utc) - dt
        days = delta.days
        if days == 0:
            return "today"
        if days == 1:
            return "yesterday"
        if days < 30:
            return f"{days}d ago"
        if days < 365:
            return f"{days // 30}mo ago"
        return f"{days // 365}y ago"
    except (ValueError, TypeError):
        return "unknown"


class Dashboard:
    def print_overview(self, org: str, repos: list[dict]):
        console.print()
        console.print(
            Panel(
                f"[bold white]Organization Overview[/bold white]\n"
                f"[dim]{org}[/dim]  •  {len(repos)} repositories",
                border_style="blue",
                expand=True,
            )
        )

        table = Table(box=box.ROUNDED, show_lines=True, title=f"{org} Repositories")
        table.add_column("#", style="dim", width=3)
        table.add_column("Repository", style="bold cyan", min_width=20)
        table.add_column("Language", style="magenta")
        table.add_column("Health", min_width=25)
        table.add_column("★ Stars", justify="right")
        table.add_column("Issues", justify="right")
        table.add_column("Last Push", justify="right")

        for i, repo in enumerate(repos, 1):
            health = _health_bar(repo["health_score"])
            table.add_row(
                str(i),
                repo["name"],
                repo.get("language") or "—",
                health,
                str(repo.get("stars", 0)),
                str(repo.get("open_issues", 0)),
                _time_ago(repo.get("last_push", "")),
            )

        console.print(table)

        healthy = sum(1 for r in repos if r["health_score"] >= 80)
        at_risk = sum(1 for r in repos if 40 <= r["health_score"] < 80)
        critical = sum(1 for r in repos if r["health_score"] < 40)

        console.print()
        summary = Table(show_header=False, box=None, padding=(0, 2))
        summary.add_row("✅ Healthy", f"[green]{healthy}[/green]")
        summary.add_row("⚠️  At Risk", f"[yellow]{at_risk}[/yellow]")
        summary.add_row("🔴 Critical", f"[red]{critical}[/red]")
        console.print(Panel(summary, title="Health Summary", border_style="blue"))
        console.print()

    def print_repo_detail(self, repo: dict, health: dict, contributors: list[dict], languages: dict[str, int]):
        console.print()
        console.print(
            Panel(
                f"[bold cyan]{repo.get('full_name', repo.get('name', ''))}[/bold cyan]\n"
                f"{repo.get('description') or 'No description'}",
                border_style="blue",
                expand=True,
            )
        )

        meta = Table(show_header=False, box=None, padding=(0, 2))
        meta.add_column(style="bold")
        meta.add_column()
        meta.add_row("Language", repo.get("language") or "—")
        meta.add_row("Stars", str(repo.get("stargazers_count", 0)))
        meta.add_row("Forks", str(repo.get("forks_count", 0)))
        meta.add_row("Open Issues", str(repo.get("open_issues_count", 0)))
        meta.add_row("Size", _format_size(repo.get("size", 0)))
        meta.add_row("Default Branch", repo.get("default_branch", "main"))
        meta.add_row("Last Push", _time_ago(repo.get("pushed_at", "")))
        meta.add_row("License", (repo.get("license") or {}).get("name", "None"))
        meta.add_row("Archived", "Yes" if repo.get("archived") else "No")
        console.print(Panel(meta, title="Repository Info", border_style="dim"))

        console.print()
        console.print("[bold]Health Score[/bold]")
        console.print(_health_bar(health["health_score"]))
        console.print()

        checks = Table(show_header=False, box=None, padding=(0, 1))
        checks.add_column(style="bold")
        checks.add_column()
        for check, score in health.get("scores", {}).items():
            icon = "✅" if score > 0 else "❌"
            label = check.replace("_", " ").title()
            checks.add_row(f"  {icon}", label)
        console.print(Panel(checks, title="Health Checks", border_style="dim"))

        if contributors:
            console.print()
            ctable = Table(box=box.SIMPLE_HEAVY, title="Top Contributors")
            ctable.add_column("Contributor", style="cyan")
            ctable.add_column("Commits (last 100)", justify="right")
            ctable.add_column("Repos", justify="right")
            for c in contributors[:10]:
                ctable.add_row(c["login"], str(c.get("total_commits", c.get("contributions", 0))), str(c.get("repo_count", 1)))
            console.print(ctable)

        if languages:
            console.print()
            total = sum(languages.values()) or 1
            lang_table = Table(box=box.SIMPLE_HEAVY, title="Languages")
            lang_table.add_column("Language", style="magenta")
            lang_table.add_column("Percentage", justify="right")
            lang_table.add_column("Bytes", justify="right")
            for lang, bytes_count in sorted(languages.items(), key=lambda x: -x[1]):
                pct = round((bytes_count / total) * 100, 1)
                lang_table.add_row(lang, f"{pct}%", f"{bytes_count:,}")
            console.print(lang_table)

        console.print()

    def print_team_metrics(self, org: str, activity: dict, days: int):
        console.print()
        console.print(
            Panel(
                f"[bold white]Team Activity — {org}[/bold white]\n"
                f"[dim]Last {days} days  •  {activity['total_commits']} total commits[/dim]",
                border_style="blue",
                expand=True,
            )
        )

        contributors = activity.get("contributors", [])
        if contributors:
            table = Table(box=box.ROUNDED, show_lines=True, title="Contributors by Activity")
            table.add_column("#", style="dim", width=3)
            table.add_column("Contributor", style="cyan")
            table.add_column("Commits", justify="right", style="green")
            table.add_column("Repos Touched", justify="right")
            table.add_column("Active Repos", style="dim")

            for i, c in enumerate(contributors, 1):
                repos_str = ", ".join(c["repos"][:3])
                if len(c["repos"]) > 3:
                    repos_str += f" +{len(c['repos']) - 3} more"
                table.add_row(
                    str(i),
                    c["login"],
                    str(c["commits"]),
                    str(c["repo_count"]),
                    repos_str,
                )
            console.print(table)
        else:
            console.print("[dim]No commit activity found in this period.[/dim]")

        repo_activity = activity.get("repo_activity", {})
        if repo_activity:
            console.print()
            rtable = Table(box=box.SIMPLE_HEAVY, title="Repo Activity")
            rtable.add_column("Repository", style="cyan")
            rtable.add_column("Commits", justify="right")
            for name, count in sorted(repo_activity.items(), key=lambda x: -x[1]):
                if count > 0:
                    rtable.add_row(name, str(count))
            console.print(rtable)

        console.print()

    def print_tech_stack(self, org: str, stack: dict):
        console.print()
        console.print(
            Panel(
                f"[bold white]Tech Stack — {org}[/bold white]\n"
                f"[dim]{stack['total_repos']} repositories analyzed[/dim]",
                border_style="blue",
                expand=True,
            )
        )

        languages = stack.get("languages", [])
        if languages:
            table = Table(box=box.ROUNDED, show_lines=True, title="Languages by Usage")
            table.add_column("#", style="dim", width=3)
            table.add_column("Language", style="magenta")
            table.add_column("Share", min_width=20)
            table.add_column("Percentage", justify="right")

            for i, lang in enumerate(languages[:15], 1):
                pct = lang["percentage"]
                filled = int(pct / 5)
                bar = "█" * filled + "░" * (20 - filled)
                table.add_row(str(i), lang["name"], bar, f"{pct}%")
            console.print(table)

        topics = stack.get("topics", [])
        if topics:
            console.print()
            ttable = Table(box=box.SIMPLE_HEAVY, title="Repository Topics")
            ttable.add_column("Topic", style="cyan")
            ttable.add_column("Repos", justify="right")
            for t in topics[:20]:
                ttable.add_row(t["name"], str(t["count"]))
            console.print(ttable)

        repo_langs = stack.get("repo_languages", {})
        if repo_langs:
            console.print()
            rltable = Table(box=box.SIMPLE_HEAVY, title="Languages per Repository")
            rltable.add_column("Repository", style="cyan")
            rltable.add_column("Languages")
            for name, langs in repo_langs.items():
                rltable.add_row(name, ", ".join(langs) if langs else "—")
            console.print(rltable)

        console.print()

    def print_health_report(self, org: str, repos: list[dict]):
        console.print()
        console.print(
            Panel(
                f"[bold white]Health Report — {org}[/bold white]\n"
                f"[dim]{len(repos)} repositories[/dim]",
                border_style="blue",
                expand=True,
            )
        )

        table = Table(box=box.ROUNDED, show_lines=True)
        table.add_column("#", style="dim", width=3)
        table.add_column("Repository", style="bold cyan", min_width=20)
        table.add_column("Health", min_width=25)
        table.add_column("Issues", justify="right")
        table.add_column("Last Push", justify="right")
        table.add_column("Flagged Checks", style="red")

        for i, repo in enumerate(repos, 1):
            failed = [k for k, v in repo.get("scores", {}).items() if v == 0]
            flagged = ", ".join(f.replace("_", " ") for f in failed[:3])
            if len(failed) > 3:
                flagged += f" +{len(failed) - 3}"
            table.add_row(
                str(i),
                repo["name"],
                _health_bar(repo["health_score"]),
                str(repo.get("open_issues", 0)),
                _time_ago(repo.get("last_push", "")),
                flagged or "—",
            )

        console.print(table)
        console.print()

    def print_stale_repos(self, org: str, repos: list[dict], days: int):
        console.print()
        console.print(
            Panel(
                f"[bold white]Stale Repositories — {org}[/bold white]\n"
                f"[dim]No activity in {days}+ days[/dim]",
                border_style="blue",
                expand=True,
            )
        )

        if not repos:
            console.print("[green]All repositories have recent activity.[/green]")
            console.print()
            return

        table = Table(box=box.ROUNDED, show_lines=True, title=f"Stale ({len(repos)} repos)")
        table.add_column("#", style="dim", width=3)
        table.add_column("Repository", style="bold red", min_width=20)
        table.add_column("Days Stale", justify="right", style="red")
        table.add_column("Last Push", justify="right")

        for i, repo in enumerate(repos, 1):
            table.add_row(
                str(i),
                repo["name"],
                str(repo.get("days_stale", "?")),
                repo.get("last_push", "never"),
            )

        console.print(table)
        console.print()

    def print_json(self, data):
        console.print_json(json.dumps(data, indent=2, default=str))
