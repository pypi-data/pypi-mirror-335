import re
import hashlib
from typing import Literal, Optional, Any, List, Dict


def camel_to_snake(text: str) -> str:
    """
    >>> camel_to_snake('CamelCaseString')
    'camel_case_string'

    :param text:
    :return:
    """
    text = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
    text = re.sub("([a-z0-9])([A-Z])", r"\1_\2", text).lower()
    return text


def snake_to_camel(text: str) -> str:
    """
    >>> snake_to_camel('snake_case_string')
    'SnakeCaseString'

    :param text:
    :return:
    """
    return "".join(word.capitalize() for word in text.split("_"))


ALGO_TYPE = Literal[
    "md5", "sha1", "sha224", "sha256", "sha384", "sha512", "blake2b", "blake2s", "sha3_224", "sha3_256", "sha3_384",
    "sha3_512", "shake_128", "shake_256"
]


def gen_data_id(
        *args: Any,
        keys: Optional[List] = None, item: Optional[Dict] = None,
        algo_type: ALGO_TYPE = "md5"
) -> str:
    """
    >>> gen_data_id('123456')
    'e10adc3949ba59abbe56e057f20f883e'

    :param args:
    :param keys:
    :param item:
    :param algo_type:
    :return:
    """
    m = hashlib.new(algo_type)
    if args:
        values = args
    elif keys is not None and item is not None:
        if isinstance(keys, list) and isinstance(item, dict):
            values = [item[k] for k in keys if k in item]
        else:
            raise ValueError(f"keys 必须是列表，item 必须是字典！")
    elif item is not None:
        values = [item[k] for k in sorted(item.keys())]
    else:
        raise ValueError(f"args 或 keys 和 item 或 item 必须提供之一！")

    data = list(map(lambda x: str(x), values))

    for i in data:
        m.update(i.encode())

    data_id = m.hexdigest()
    return data_id
