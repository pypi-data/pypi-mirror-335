import asyncio
from pathlib import Path
from typing import Annotated

import typer
from liblaf import grapes

import awesome_list_generator as alg

app = typer.Typer(name="awesome-list-generator")


async def async_main(cfg: alg.Config) -> None:
    formatter: alg.Formatter = alg.get_formatter(cfg.config.format)
    projects: list[alg.ProjectInfo] = await alg.fetch_projects(cfg.projects)
    formatted: str = formatter.format(cfg.categories, projects)
    print(formatted)


@app.command()
def main(config: Annotated[Path, typer.Argument()] = Path("awesome.yaml")) -> None:
    cfg: alg.Config = grapes.load_pydantic(config, alg.Config)
    asyncio.run(async_main(cfg))
