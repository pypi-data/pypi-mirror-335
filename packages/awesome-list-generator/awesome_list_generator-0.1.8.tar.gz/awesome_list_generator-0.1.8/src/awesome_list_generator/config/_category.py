import pydantic


class Category(pydantic.BaseModel):
    category: str
    title: str
    subtitle: str | None = None
