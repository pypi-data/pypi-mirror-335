from typing import Optional, Dict, Any
from fake_useragent import UserAgent


def get_default(**kwargs: Any) -> Dict[str, str]:
    if not kwargs:
        kwargs = dict(platforms=["desktop"])
    ua = UserAgent(**kwargs)
    headers = {
        "User-Agent": ua.random
    }
    return headers


def update_default(
        headers: Optional[Dict[str, str]] = None,
        default: Optional[Dict[str, str]] = None
) -> Dict[str, str]:
    if headers is None:
        headers = {}
    if default is None:
        default = get_default()
    headers.update(default)
    return headers
