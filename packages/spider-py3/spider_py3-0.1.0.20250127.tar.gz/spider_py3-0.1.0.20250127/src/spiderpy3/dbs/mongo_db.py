from typing import Optional, Tuple, Any
from urllib.parse import quote_plus
from pymongo import MongoClient
from pymongo.synchronous.database import Database

from spiderpy3.dbs.db import DB


class MongoDB(DB):

    def __init__(
            self,
            *args: Any,
            host: str = "localhost",
            port: int = 27017,
            username: Optional[str] = None,
            password: Optional[str] = None,
            dbname: str,
            **kwargs: Any
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.dbname = dbname

        super().__init__(*args, **kwargs)

    def open(self) -> Tuple[MongoClient, Database]:
        if self.username and self.password:
            uri = "mongodb://%s:%s@%s:%s" % (quote_plus(self.username), quote_plus(self.password), self.host, self.port)
        else:
            uri = "mongodb://%s:%s" % (self.host, self.port)
        client = MongoClient(uri)
        db = client[self.dbname]
        return client, db

    def close(self, client: MongoClient) -> None:
        if client:
            client.close()

    def _open(self) -> None:
        self.client, self.db = self.open()

    def _close(self) -> None:
        self.close(self.client)
