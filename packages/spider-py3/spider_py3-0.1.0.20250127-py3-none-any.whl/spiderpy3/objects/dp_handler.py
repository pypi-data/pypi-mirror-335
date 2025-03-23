from abc import abstractmethod
from typing import Any

from spiderpy3.objects.handler import Handler
from spiderpy3.mixins.dp import DpMixin


class DpHandler(Handler, DpMixin):
    @abstractmethod
    def action(self, *args, **kwargs) -> Any:
        pass
