import re
import time
import ujson
import random
from tqdm import tqdm
from typing import List, Dict, Callable, Optional, Any

from spiderpy3.utils.execute.js import execute_js_code_by_py_mini_racer


def get_random_pick(data: List[Any]) -> Callable[[], Any]:
    """
    返回一个函数，该函数会从列表中随机选择元素，并确保在重新开始选择前，每个元素都被选过一次

    :param data: 要选择的列表
    :return: 随机选择元素的函数
    """
    shuffled_data = data[:]
    random.shuffle(shuffled_data)
    current_index = 0

    def random_pick() -> Any:
        """随机返回一个元素，确保所有元素被选过后重新打乱顺序"""
        nonlocal shuffled_data, current_index
        if current_index >= len(shuffled_data):
            shuffled_data = data[:]
            random.shuffle(shuffled_data)
            current_index = 0
        selected_item = shuffled_data[current_index]
        current_index += 1
        return selected_item

    return random_pick


class Tqdm(tqdm):
    @staticmethod
    def format_meter(*args, **kwargs):
        tqdm.format_meter(*args, **kwargs)

        prefix = kwargs["prefix"]
        n = kwargs["n"]
        elapsed = kwargs["elapsed"]

        rate_fmt = f"{(n / elapsed):.4f}条/秒" if elapsed != 0 else "?"
        rate_inv_fmt = f"{(elapsed / n):.4f}秒/条" if n != 0 else "?"

        return f"{prefix} [{rate_fmt} {rate_inv_fmt}]"


def monitor(func: Callable[[], int], interval: float = 1.0) -> None:
    with Tqdm(desc="监控") as pbar:
        while True:
            now_n = func()
            pbar.update(now_n - pbar.n)
            time.sleep(interval)


def split_list(lst: List[Any], num_parts: Optional[int] = None, part_size: Optional[int] = None) -> List[Any]:
    if not lst:
        return []

    if num_parts:
        # 按份数拆分
        avg_size = len(lst) // num_parts  # 每份的平均大小
        remainder = len(lst) % num_parts  # 余数部分
        result = []

        # 前 num_parts - 1 份，每份大小为 avg_size
        result.extend([lst[start:start + avg_size] for start in range(0, len(lst) - avg_size - remainder, avg_size)])

        # 最后一份包含余数
        result.append(lst[len(lst) - avg_size - remainder:])

        return result

    elif part_size:
        # 按每份大小拆分
        return [lst[i:i + part_size] for i in range(0, len(lst), part_size)]

    else:
        raise ValueError("必须提供 num_parts 或 part_size 之一")


def jsonp_to_json(jsonp: str) -> Dict[str, Any]:
    func_name = re.match(r"(?P<func_name>jQuery.*?)\(\{.*\}\)\S*", jsonp).groupdict()["func_name"]
    js_code = f"function {func_name}(o){{return o}};function sdk(){{return JSON.stringify({jsonp})}};"
    json_str = execute_js_code_by_py_mini_racer(js_code, func_name="sdk")
    json_obj = ujson.loads(json_str)
    return json_obj
