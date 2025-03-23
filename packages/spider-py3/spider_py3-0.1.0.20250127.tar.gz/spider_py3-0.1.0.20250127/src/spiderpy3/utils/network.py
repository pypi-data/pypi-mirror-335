import httpx
import socket
from typing import Literal


def check_port_occupancy(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        port_occupied = s.connect_ex(("127.0.0.1", port)) == 0
        return port_occupied


def get_host(host_type: Literal["local", "public"] = "local") -> str:
    if host_type == "local":
        return socket.gethostbyname(socket.gethostname())
    elif host_type == "public":
        return httpx.get("https://api.ipify.org", timeout=60).text
    else:
        raise ValueError("host_type 只能是 `local` 或 `public`！")
