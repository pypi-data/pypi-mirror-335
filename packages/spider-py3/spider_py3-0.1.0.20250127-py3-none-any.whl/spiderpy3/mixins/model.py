from abc import ABC, abstractmethod
from typing import List


class ModelMixin(ABC):
    @classmethod
    @abstractmethod
    def columns(cls) -> List[str]:
        pass
