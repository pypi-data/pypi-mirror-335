import html as html_
from typing import Any
from htmlmin import minify


def compress(html: str, **kwargs: Any) -> str:
    return minify(html, **kwargs)


def escape(text: str) -> str:
    """
    >>> escape("<")
    '&lt;'

    """
    return html_.escape(text)


def unescape(text: str) -> str:
    """
    >>> unescape("&lt;")
    '<'

    """
    return html_.unescape(text)
