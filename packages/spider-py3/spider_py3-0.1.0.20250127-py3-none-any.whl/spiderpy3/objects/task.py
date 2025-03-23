from abc import abstractmethod
from typing import Any

from spiderpy3.objects.handler import Handler


class Task(Handler):
    @abstractmethod
    def action(self, *args, **kwargs) -> Any:
        pass
