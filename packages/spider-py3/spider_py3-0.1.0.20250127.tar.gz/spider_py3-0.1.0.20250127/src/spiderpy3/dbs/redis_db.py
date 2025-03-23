from redis import Redis
from typing import Optional, Any

from spiderpy3.dbs.db import DB


class RedisDB(DB):

    def __init__(
            self,
            *args: Any,
            host: str = "localhost",
            port: int = 6379,
            password: Optional[str] = None,
            dbname: int = 0,
            **kwargs: Any
    ) -> None:
        self.host = host
        self.port = port
        self.password = password
        self.dbname = dbname

        super().__init__(*args, **kwargs)

    def open(self) -> Redis:
        redis = Redis(
            host=self.host,
            port=self.port,
            db=self.dbname,
            password=self.password,
            encoding="utf-8",
            decode_responses=True
        )
        return redis

    def close(self, redis: Redis) -> None:
        if redis:
            redis.close()

    def _open(self) -> None:
        self.redis = self.open()

    def _close(self) -> None:
        self.close(self.redis)
