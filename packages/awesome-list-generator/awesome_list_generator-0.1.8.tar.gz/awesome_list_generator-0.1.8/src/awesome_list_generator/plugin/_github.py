import datetime
from typing import Any, Self

import githubkit
import githubkit.versions.latest.models as ghm
import pydantic
from environs import env


class GitHubInfo(pydantic.BaseModel):
    owner: str
    name: str
    archived: bool
    description: str | None = None
    topics: list[str] = []
    language: str | None = None
    license: str | None = None
    forks: int
    stars: int
    open_issues: int
    open_pulls: int
    updated: datetime.datetime

    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.name}"

    @property
    def html_url(self) -> str:
        return f"https://github.com/{self.owner}/{self.name}"

    @property
    def license_link(self) -> str:
        return f"{self.html_url}/blob/main/LICENSE"

    @property
    def forks_link(self) -> str:
        return f"{self.html_url}/forks"

    @property
    def stars_link(self) -> str:
        return f"{self.html_url}/stargazers"

    @property
    def issues_link(self) -> str:
        return f"{self.html_url}/issues"

    @property
    def pulls_link(self) -> str:
        return f"{self.html_url}/pulls"

    @classmethod
    async def fetch(cls, name: str) -> Self:
        gh: githubkit.GitHub = get_octokit()
        owner: str
        repo: str
        owner, _, repo = name.partition("/")
        repository: ghm.FullRepository = (
            await gh.rest.repos.async_get(owner, repo)
        ).parsed_data
        return cls(
            owner=repository.owner.login,
            name=repository.name,
            archived=repository.archived,
            description=repository.description,
            topics=repository.topics or [],
            language=repository.language,
            license=repository.license_.name if repository.license_ else None,
            forks=repository.forks_count,
            stars=repository.stargazers_count,
            open_issues=repository.open_issues_count,
            open_pulls=await count_open_pulls(owner, repo),
            updated=repository.updated_at,
        )


def get_octokit() -> githubkit.GitHub:
    return githubkit.GitHub(
        env.str("INPUT_GITHUB_TOKEN", None)
        or env.str("INPUT_TOKEN", None)
        or env.str("GH_TOKEN", None)
        or env.str("GITHUB_TOKEN", None)
    )


async def count_open_pulls(owner: str, repo: str) -> int:
    gh: githubkit.GitHub = get_octokit()
    data: dict[str, Any] = await gh.async_graphql(
        r"""
query countOpenPRs($owner: String!, $repo: String!) {
  repository(owner: $owner, name: $repo) {
    pullRequests(states: [OPEN]) {
      totalCount
    }
  }
}""",
        {"owner": owner, "repo": repo},
    )
    return data["repository"]["pullRequests"]["totalCount"]
