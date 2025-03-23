from collections.abc import Generator, Iterable

import awesome_list_generator as alg

from . import format_language


class FormatterMarkdown(alg.Formatter):
    def format(
        self, categories: Iterable[alg.Category], projects: Iterable[alg.ProjectInfo]
    ) -> str:
        markdown: str = "".join(format_markdown(categories, projects))
        return markdown


def format_markdown(
    categories: Iterable[alg.Category], projects: Iterable[alg.ProjectInfo]
) -> Generator[str]:
    categories: list[alg.Category] = list(categories)
    for project in projects:
        for category in project.categories:
            if category not in [category.category for category in categories]:
                categories.append(
                    alg.Category(category=category, title=category.title())
                )
    for category in categories:
        yield from format_category(category, projects)


def format_category(
    category: alg.Category, projects: Iterable[alg.ProjectInfo]
) -> Generator[str]:
    yield f"## {category.title}\n"
    if category.subtitle:
        yield f"_{category.subtitle}_\n"
    for project in projects:
        if category.category in project.categories:
            yield from format_project(project)
    yield "\n"


def format_project(project: alg.ProjectInfo) -> Generator[str]:  # noqa: C901
    yield f"[**{project.name}**]({project.url})"
    if project.archived:
        yield " ![Archived](https://img.shields.io/badge/Archived-9e6a03?logo=GitHub)"
    yield " <br />\n"
    if project.description:
        yield f"{project.description} <br />\n"
    if github := project.github:
        if github.topics:
            for topic in github.topics:
                yield f"[`{topic}`](https://github.com/topics/{topic}) "
            yield "<br />\n"
        if github.language:
            yield format_language(github.language) + "\n"
        if github.license:
            yield f"[![GitHub License](https://img.shields.io/github/license/{github.owner}/{github.name})]({github.license_link})\n"
        if github.forks:
            yield f"[![GitHub forks](https://img.shields.io/github/forks/{github.owner}/{github.name})]({github.forks_link})\n"
        if github.stars:
            yield f"[![GitHub stars](https://img.shields.io/github/stars/{github.owner}/{github.name})]({github.stars_link})\n"
        if github.open_issues:
            yield f"[![GitHub Issues](https://img.shields.io/github/issues/{github.owner}/{github.name})]({github.issues_link})\n"
        if github.open_pulls:
            yield f"[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/{github.owner}/{github.name})]({github.pulls_link})\n"
    yield "\n"
