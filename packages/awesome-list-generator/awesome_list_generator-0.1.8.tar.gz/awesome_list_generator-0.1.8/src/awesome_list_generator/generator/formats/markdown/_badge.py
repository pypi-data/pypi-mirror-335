import urllib
import urllib.parse

LANGUAGE_TO_LOGO: dict[str, str] = {
    "jupyter notebook": "jupyter",
    "shell": "gnubash",
}


def format_language(language: str) -> str:
    quote: str = urllib.parse.quote(language)
    logo: str = LANGUAGE_TO_LOGO.get(language.lower(), quote)
    return f"![{language}](https://img.shields.io/badge/{quote}-black?logo={logo})"
