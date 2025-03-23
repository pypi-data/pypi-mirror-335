import atexit
from typing import Any
from abc import ABC, abstractmethod


class DB(ABC):
    def __init__(
            self,
            *args: Any,
            **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)

        self._open()
        atexit.register(self._close)

    @abstractmethod
    def open(self) -> Any:
        pass

    @abstractmethod
    def close(self, *args: Any, **kwargs: Any) -> None:
        pass

    @abstractmethod
    def _open(self) -> None:
        pass

    @abstractmethod
    def _close(self) -> None:
        pass
