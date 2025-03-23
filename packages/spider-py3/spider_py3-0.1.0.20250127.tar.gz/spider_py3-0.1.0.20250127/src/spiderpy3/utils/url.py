import re
import furl
import tldextract
from urllib import parse
from w3lib.url import canonicalize_url
from typing import Optional, Tuple, Dict, Any


def get_furl_obj(url: str) -> furl.furl:
    return furl.furl(url)


def is_valid(url: str) -> bool:
    """
    >>> is_valid("https://www.baidu.com/")
    True

    :param url:
    :return:
    """
    try:
        parse_result = get_parse_result(url)
        scheme, netloc = parse_result.scheme, parse_result.netloc
        if not scheme:
            return False
        if not netloc:
            return False
        if scheme not in ("http", "https"):
            return False
        return True
    except ValueError:
        return False


def quote(url: str, safe: str = "%;/?:@&=+$,", encoding: str = "utf-8") -> str:
    """
    >>> quote("https://www.baidu.com/s?wd=你好")
    'https://www.baidu.com/s?wd=%E4%BD%A0%E5%A5%BD'

    :param url:
    :param safe:
    :param encoding:
    :return:
    """
    return parse.quote(url, safe=safe, encoding=encoding)


def unquote(url: str, encoding: str = "utf-8") -> str:
    """
    >>> unquote("https://www.baidu.com/s?wd=%E4%BD%A0%E5%A5%BD")
    'https://www.baidu.com/s?wd=你好'

    :param url:
    :param encoding:
    :return:
    """
    return parse.unquote(url, encoding=encoding)


def encode(params: Dict[str, Any]) -> str:
    """
    >>> encode({"a": "1", "b": "2"})
    'a=1&b=2'

    :param params:
    :return:
    """
    return parse.urlencode(params)


def decode(url: str) -> Dict[str, str]:
    """
    >>> decode("xxx?a=1&b=2")
    {'a': '1', 'b': '2'}

    :param url:
    :return:
    """
    params = {}

    lst = url.split("?", maxsplit=1)[-1].split("&")
    for i in lst:
        key, value = i.split("=", maxsplit=1)
        params[key] = unquote(value)

    return params


def join_url(base_url: str, url: str) -> str:
    """
    >>> join_url("https://www.baidu.com/", "/s?ie=UTF-8&wd=spider-py3")
    'https://www.baidu.com/s?ie=UTF-8&wd=spider-py3'

    :param base_url:
    :param url:
    :return:
    """
    return parse.urljoin(base_url, url)


def join_params(url: str, params: Dict[str, Any]) -> str:
    """
    >>> join_params("https://www.baidu.com/s", {"wd": "你好"})
    'https://www.baidu.com/s?wd=%E4%BD%A0%E5%A5%BD'

    :param url:
    :param params:
    :return:
    """
    if not params:
        return url

    params = encode(params)
    separator = "?" if "?" not in url else "&"
    return url + separator + params


def get_params(url: str) -> Dict[str, str]:
    """
    >>> get_params("https://www.baidu.com/s?wd=spider-py3")
    {'wd': 'spider-py3'}

    :param url:
    :return:
    """
    furl_obj = get_furl_obj(url)
    params = dict(furl_obj.query.params)
    return params


def get_param(url: str, key: str, default: Optional[Any] = None) -> Any:
    """
    >>> get_param("https://www.baidu.com/s?wd=spider-py3", "wd")
    'spider-py3'

    :param url:
    :param key:
    :param default:
    :return:
    """
    params = get_params(url)
    param = params.get(key, default)
    return param


def get_url_params(url: str) -> Tuple[str, Dict[str, str]]:
    """
    >>> get_url_params("https://www.baidu.com/s?wd=spider-py3")
    ('https://www.baidu.com/s', {'wd': 'spider-py3'})

    :param url:
    :return:
    """
    root_url = ""
    params = {}

    if "?" in url:
        root_url = url.split("?", maxsplit=1)[0]
        params = get_params(url)
    else:
        if re.search("[&=]", url) and not re.search("/", url):
            # 只有参数
            params = get_params(url)
        else:
            root_url = url

    return root_url, params


def get_domain(url: str) -> str:
    """
    >>> get_domain("https://www.baidu.com/s?wd=spider-py3")
    'baidu'

    :param url:
    :return:
    """
    er = tldextract.extract(url)
    domain = er.domain
    return domain


def get_subdomain(url: str) -> str:
    """
    >>> get_subdomain("https://passport.jd.com/new/login.aspx?ReturnUrl=https%3A%2F%2Fwww.jd.com%2F")
    'passport'

    :param url:
    :return:
    """
    er = tldextract.extract(url)
    subdomain = er.subdomain
    return subdomain


def get_origin_path(url: str) -> str:
    """
    >>> get_origin_path("https://passport.jd.com/new/login.aspx?ReturnUrl=https%3A%2F%2Fwww.jd.com%2F")
    'https://passport.jd.com/new/login.aspx'

    :param url:
    :return:
    """
    furl_obj = get_furl_obj(url)
    origin_path = str(furl_obj.origin) + str(furl_obj.path)
    return origin_path


def get_parse_result(url: str) -> parse.ParseResult:
    parse_result = parse.urlparse(url)
    return parse_result


def canonicalize(url: str):
    """
    >>> canonicalize("https://www.baidu.com/s?wd=spider-py3")
    'https://www.baidu.com/s?wd=spider-py3'

    :param url:
    :return:
    """
    return canonicalize_url(url)
