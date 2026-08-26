"""Repository health scoring system."""

from datetime import datetime, timezone


class HealthScorer:
    WEIGHTS = {
        "has_readme": 10,
        "has_license": 8,
        "has_description": 5,
        "has_topics": 4,
        "has_issues": 5,
        "has_wiki": 3,
        "has_ci": 15,
        "recent_activity": 15,
        "low_open_issues": 10,
        "has_contributing": 5,
        "has_code_of_conduct": 3,
        "has_security_policy": 4,
        "has_changelog": 3,
        "has_docker": 3,
        "open_prs_low": 7,
    }

    def score_repo(self, repo: dict) -> dict:
        scores: dict[str, int] = {}

        scores["has_readme"] = self._check_file_exists(repo, "readme")
        scores["has_license"] = 1 if repo.get("license") else 0
        scores["has_description"] = 1 if repo.get("description") else 0
        scores["has_topics"] = min(len(repo.get("topics", [])), 5)
        scores["has_issues"] = 1 if repo.get("has_issues") else 0
        scores["has_wiki"] = 1 if repo.get("has_wiki") else 0
        scores["has_ci"] = self._check_ci(repo)
        scores["recent_activity"] = self._score_activity(repo)
        scores["low_open_issues"] = self._score_issue_load(repo)
        scores["has_contributing"] = self._check_file_exists(repo, "contributing")
        scores["has_code_of_conduct"] = self._check_file_exists(repo, "code_of_conduct")
        scores["has_security_policy"] = self._check_file_exists(repo, "security")
        scores["has_changelog"] = self._check_file_exists(repo, "changelog")
        scores["has_docker"] = self._check_file_exists(repo, "dockerfile")
        scores["open_prs_low"] = self._score_pr_load(repo)

        total = sum(scores.values())
        max_possible = sum(self.WEIGHTS.values())
        health_score = round((total / max_possible) * 100) if max_possible > 0 else 0

        return {
            "name": repo.get("name", "unknown"),
            "full_name": repo.get("full_name", ""),
            "description": repo.get("description", ""),
            "language": repo.get("language"),
            "health_score": min(health_score, 100),
            "scores": scores,
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "open_issues": repo.get("open_issues_count", 0),
            "size_kb": repo.get("size", 0),
            "last_push": repo.get("pushed_at", ""),
            "archived": repo.get("archived", False),
            "url": repo.get("html_url", ""),
        }

    def score_repos(self, repos: list[dict]) -> list[dict]:
        scored = [self.score_repo(r) for r in repos]
        scored.sort(key=lambda r: r["health_score"])
        return scored

    def _check_file_exists(self, repo: dict, filename: str) -> int:
        default_branch = repo.get("default_branch", "main")
        check_names = {
            "readme": ["README.md", "readme.md", "README.rst", "README"],
            "contributing": ["CONTRIBUTING.md", "contributing.md"],
            "code_of_conduct": ["CODE_OF_CONDUCT.md", "code_of_conduct.md"],
            "security": ["SECURITY.md", "security.md"],
            "changelog": ["CHANGELOG.md", "changelog.md", "CHANGES.md"],
            "dockerfile": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"],
        }
        names = check_names.get(filename, [filename])
        for name in names:
            if name.lower() in [f.lower() for f in repo.get("files", [])]:
                return 1
        return 0

    def _check_ci(self, repo: dict) -> int:
        workflows = repo.get("workflows_count", 0)
        return 1 if workflows > 0 else 0

    def _score_activity(self, repo: dict) -> int:
        pushed = repo.get("pushed_at")
        if not pushed:
            return 0
        try:
            last = datetime.fromisoformat(pushed.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            days = (now - last).days
            if days <= 7:
                return 5
            if days <= 30:
                return 4
            if days <= 90:
                return 3
            if days <= 180:
                return 2
            return 1
        except (ValueError, TypeError):
            return 0

    def _score_issue_load(self, repo: dict) -> int:
        issues = repo.get("open_issues_count", 0)
        if issues == 0:
            return 5
        if issues <= 5:
            return 4
        if issues <= 15:
            return 3
        if issues <= 30:
            return 2
        return 1

    def _score_pr_load(self, repo: dict) -> int:
        prs = repo.get("open_prs", 0)
        if prs == 0:
            return 4
        if prs <= 3:
            return 3
        if prs <= 10:
            return 2
        return 1
