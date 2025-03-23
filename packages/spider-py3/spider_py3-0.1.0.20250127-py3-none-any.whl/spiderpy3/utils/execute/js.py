import os
import json
import execjs
import subprocess
import py_mini_racer
from typing import Optional, Tuple, Dict, Any


def execute_js_code_by_execjs(
        js_code: Optional[str] = None,
        js_file_path: Optional[str] = None,
        func_name: Optional[str] = None,
        func_args: Optional[Tuple[Any, ...]] = None
) -> Any:
    if js_code is None and js_file_path is None:
        raise ValueError(f"js_code：{js_code}，js_file_path：{js_file_path} 不能同时为 None ！")
    if js_file_path is not None:
        with open(js_file_path, "r", encoding="utf-8") as f:
            js_code = f.read()

    ctx = execjs.compile(js_code)
    if func_name is None:
        result = ctx.eval(js_code)
        return result
    if func_args is None:
        func_args = tuple()
    result = ctx.call(func_name, *func_args)
    return result


def execute_js_code_by_py_mini_racer(
        js_code: Optional[str] = None,
        js_file_path: Optional[str] = None,
        func_name: Optional[str] = None,
        func_args: Optional[Tuple[Any, ...]] = None
) -> Any:
    if js_code is None and js_file_path is None:
        raise ValueError(f"js_code：{js_code}，js_file_path：{js_file_path} 不能同时为 None ！")
    if js_file_path is not None:
        with open(js_file_path, "r", encoding="utf-8") as f:
            js_code = f.read()

    ctx = py_mini_racer.MiniRacer()
    result = ctx.eval(js_code)
    if func_name is None:
        return result
    if func_args is None:
        func_args = tuple()
    result = ctx.call(func_name, *func_args)
    return result


def execute_js_code_by_subprocess(
        js_code: Optional[str] = None,
        js_file_path: Optional[str] = None,
        func_args: Optional[Tuple[Dict[str, Any], ...]] = None,
) -> Any:
    if js_code is None and js_file_path is None:
        raise ValueError(f"js_code, js_file_path 不能同时为 None ！")
    if js_file_path is not None:
        with open(js_file_path, "r", encoding="utf-8") as f:
            js_code = f.read()

    # js_code 中通过 process.argv.slice(2) 来接收参数
    func_args = ["node", "-e", js_code] + list(map(lambda x: json.dumps(x), func_args))
    process = subprocess.Popen(
        func_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()
    result = stdout.decode()
    return result
