import os
import sys
import httpx
import zipfile
import platform
from typing import Optional, Literal, Dict, Any, Tuple, List

from spiderpy3.utils.url import is_valid, get_furl_obj
from spiderpy3.utils.headers import get_default


def url_to_file_path(
        url: str,
        headers: Optional[Dict[str, Any]] = None,
        file_path: Optional[str] = None,
        dir_path: Optional[str] = None,
        file_name: Optional[str] = None,
        file_prefix: Optional[str] = None,
        file_suffix: Optional[str] = None
) -> Optional[str]:
    if not is_valid(url):
        return

    if headers is None:
        headers = get_default()

    if file_path is None:
        if dir_path is None:
            sys_argv0 = sys.argv[0]
            if not os.path.isfile(sys_argv0):
                return
            dir_path = os.path.dirname(sys_argv0)
        if file_name is None:
            if file_prefix is not None and file_suffix is not None:
                file_name = file_prefix + file_suffix
            else:
                if file_prefix is None:
                    file_prefix, _ = os.path.splitext(get_furl_obj(url).path.segments[-1])
                if file_suffix is None:
                    _, file_suffix = os.path.splitext(get_furl_obj(url).path.segments[-1])
                    if file_suffix is None:
                        response = httpx.head(url, headers=headers)
                        # content-type: image/jpeg
                        if (content_type := response.headers.get("content-type")) is not None:
                            file_ext = content_type.split("/", maxsplit=1)[-1]
                            file_suffix = "." + file_ext
                file_name = file_prefix + file_suffix
        file_path = os.path.join(dir_path, file_name)

    if os.path.exists(file_path):
        return file_path

    dir_path = os.path.dirname(file_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    try:
        response = httpx.get(url, headers=headers)
        content = response.content
        with open(file_path, "wb") as file:
            file.write(content)
    except Exception:  # noqa
        file_path = None

    return file_path


def compress_dir_path(dir_path: str, compress_file_path: Optional[str] = None, mode: Literal["zip"] = "zip") -> str:
    dir_path = os.path.abspath(dir_path)
    if not os.path.isdir(dir_path):
        raise ValueError(f"不支持 dir_path：{dir_path}！")

    valid_modes = ["zip"]
    if mode not in valid_modes:
        raise ValueError(f"不支持 mode：{mode}！")

    if compress_file_path is None:
        compress_file_path = os.path.join(
            os.path.dirname(dir_path), os.path.basename(dir_path) + "." + mode
        )

    if mode == "zip":
        with zipfile.ZipFile(compress_file_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_file_path = os.path.relpath(file_path, dir_path)
                    zf.write(file_path, arcname=rel_file_path)

    return compress_file_path


def get_file_paths_and_dir_paths(path: str) -> Tuple[List[str], List[str]]:
    file_paths = []
    dir_paths = []

    path = os.path.abspath(path)

    with os.scandir(path) as entries:
        for entry in entries:
            system = platform.system()
            if system == "Windows":
                from nt import DirEntry
            elif system == "Linux":
                from posix import DirEntry
            elif system == "Darwin":
                from posix import DirEntry
            else:
                raise ValueError(f"system：`{system}` 不支持该系统！")

            entry: DirEntry
            if entry.is_file():
                file_paths.append(entry.path)
            elif entry.is_dir():
                dir_paths.append(entry.path)
                sub_file_paths, sub_dir_paths = get_file_paths_and_dir_paths(entry.path)
                file_paths.extend(sub_file_paths)
                dir_paths.extend(sub_dir_paths)

    return file_paths, dir_paths
