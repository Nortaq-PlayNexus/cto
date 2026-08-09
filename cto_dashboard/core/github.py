"""GitHub API client for fetching repository and organization data."""

import requests
from datetime import datetime, timezone
from typing import Any


class GitHubClient:
    BASE = "https://api.github.com"

    def __init__(self, org: str, token: str | None = None):
        self.org = org
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        })
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def _get(self, url: str, params: dict | None = None) -> Any:
        resp = self.session.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def list_repos(self) -> list[dict]:
        repos = []
        page = 1
        while True:
            data = self._get(
                f"{self.BASE}/orgs/{self.org}/repos",
                params={"per_page": 100, "page": page, "sort": "pushed"},
            )
            if not data:
                break
            repos.extend(data)
            if len(data) < 100:
                break
            page += 1
        return repos

    def get_repo(self, name: str) -> dict | None:
        try:
            return self._get(f"{self.BASE}/repos/{self.org}/{name}")
        except requests.HTTPError:
            return None

    def get_repo_contributors(self, name: str) -> list[dict]:
        try:
            return self._get(
                f"{self.BASE}/repos/{self.org}/{name}/contributors",
                params={"per_page": 100},
            )
        except requests.HTTPError:
            return []

    def get_repo_languages(self, name: str) -> dict[str, int]:
        try:
            return self._get(f"{self.BASE}/repos/{self.org}/{name}/languages")
        except requests.HTTPError:
            return {}

    def get_repo_commits(self, name: str, since: datetime | None = None, per_page: int = 100) -> list[dict]:
        params: dict[str, Any] = {"per_page": per_page}
        if since:
            params["since"] = since.isoformat()
        try:
            return self._get(f"{self.BASE}/repos/{self.org}/{name}/commits", params=params)
        except requests.HTTPError:
            return []

    def get_repo_pulls(self, name: str, state: str = "all", per_page: int = 100) -> list[dict]:
        try:
            return self._get(
                f"{self.BASE}/repos/{self.org}/{name}/pulls",
                params={"state": state, "per_page": per_page, "sort": "updated"},
            )
        except requests.HTTPError:
            return []

    def get_repo_issues(self, name: str, state: str = "all", per_page: int = 100) -> list[dict]:
        try:
            return self._get(
                f"{self.BASE}/repos/{self.org}/{name}/issues",
                params={"state": state, "per_page": per_page, "sort": "updated"},
            )
        except requests.HTTPError:
            return []

    def get_repo_workflows(self, name: str) -> list[dict]:
        try:
            data = self._get(f"{self.BASE}/repos/{self.org}/{name}/actions/workflows")
            return data.get("workflows", [])
        except requests.HTTPError:
            return []

    def get_org_members(self) -> list[dict]:
        try:
            return self._get(f"{self.BASE}/orgs/{self.org}/members", params={"per_page": 100})
        except requests.HTTPError:
            return []
