from abc import abstractmethod
from typing import Any

from spiderpy3.objects.task import Task
from spiderpy3.mixins.dp import DpMixin


class DpTask(Task, DpMixin):
    @abstractmethod
    def action(self, *args, **kwargs) -> Any:
        pass
