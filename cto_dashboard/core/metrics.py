"""Team metrics and tech stack analysis."""

from datetime import datetime, timezone, timedelta
from collections import defaultdict

from cto_dashboard.core.github import GitHubClient


class MetricsCollector:
    def __init__(self, client: GitHubClient):
        self.client = client

    def collect_activity(self, repos: list[dict], days: int = 30) -> dict:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        contributor_commits: dict[str, int] = defaultdict(int)
        contributor_repos: dict[str, set[str]] = defaultdict(set)
        repo_commit_counts: dict[str, int] = {}
        total_commits = 0

        for repo in repos:
            name = repo.get("name", "")
            commits = self.client.get_repo_commits(name, since=since, per_page=100)
            repo_commit_counts[name] = len(commits)
            total_commits += len(commits)

            for commit in commits:
                author = commit.get("author") or {}
                login = author.get("login")
                if login:
                    contributor_commits[login] += 1
                    contributor_repos[login].add(name)

        contributors = []
        for login, count in sorted(contributor_commits.items(), key=lambda x: -x[1]):
            contributors.append({
                "login": login,
                "commits": count,
                "repos": list(contributor_repos[login]),
                "repo_count": len(contributor_repos[login]),
            })

        return {
            "period_days": days,
            "total_commits": total_commits,
            "contributors": contributors,
            "repo_activity": repo_commit_counts,
        }

    def collect_tech_stack(self, repos: list[dict]) -> dict:
        language_bytes: dict[str, int] = defaultdict(int)
        repo_languages: dict[str, list[str]] = {}
        all_topics: dict[str, int] = defaultdict(int)

        for repo in repos:
            name = repo.get("name", "")
            langs = self.client.get_repo_languages(name)
            repo_languages[name] = list(langs.keys())
            for lang, bytes_count in langs.items():
                language_bytes[lang] += bytes_count

            for topic in repo.get("topics", []):
                all_topics[topic] += 1

        total_bytes = sum(language_bytes.values()) or 1
        languages = []
        for lang, bytes_count in sorted(language_bytes.items(), key=lambda x: -x[1]):
            languages.append({
                "name": lang,
                "bytes": bytes_count,
                "percentage": round((bytes_count / total_bytes) * 100, 1),
            })

        topics = sorted(all_topics.items(), key=lambda x: -x[1])

        return {
            "languages": languages,
            "repo_languages": repo_languages,
            "topics": [{"name": t, "count": c} for t, c in topics],
            "total_repos": len(repos),
        }

    def find_stale(self, repos: list[dict], days: int = 90) -> list[dict]:
        threshold = datetime.now(timezone.utc) - timedelta(days=days)
        stale = []

        for repo in repos:
            if repo.get("archived"):
                continue
            pushed = repo.get("pushed_at")
            if not pushed:
                stale.append({"name": repo["name"], "last_push": "never", "days_stale": -1, "url": repo.get("html_url", "")})
                continue
            try:
                last = datetime.fromisoformat(pushed.replace("Z", "+00:00"))
                if last < threshold:
                    stale.append({
                        "name": repo["name"],
                        "last_push": pushed,
                        "days_stale": (datetime.now(timezone.utc) - last).days,
                        "url": repo.get("html_url", ""),
                    })
            except (ValueError, TypeError):
                continue

        stale.sort(key=lambda r: -r.get("days_stale", 0))
        return stale
