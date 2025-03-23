import pydantic


class ProjectConfig(pydantic.BaseModel):
    name: str | None = None
    categories: list[str] | None = None
    cargo: str | None = None
    conda: str | None = None
    ctan: str | None = None
    github: str | None = None
    go: str | None = None
    npm: str | None = None
    pypi: str | None = None
