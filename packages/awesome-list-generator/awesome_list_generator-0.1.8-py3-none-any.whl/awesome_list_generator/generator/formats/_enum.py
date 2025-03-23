import enum

from . import Formatter, FormatterMarkdown


class Format(enum.StrEnum):
    JSON = "json"
    MARKDOWN = "markdown"


def get_formatter(fmt: str | Format) -> Formatter:
    match fmt:
        case Format.JSON:
            raise NotImplementedError
        case Format.MARKDOWN:
            return FormatterMarkdown()
        case _:
            msg: str = f"Unsupported format: {fmt}"
            raise ValueError(msg)
