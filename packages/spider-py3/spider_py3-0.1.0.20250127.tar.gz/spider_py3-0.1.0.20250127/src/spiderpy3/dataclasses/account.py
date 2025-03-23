from dataclasses import dataclass


@dataclass
class Account(object):
    owner: str
    platform: str
    username: str
    password: str
