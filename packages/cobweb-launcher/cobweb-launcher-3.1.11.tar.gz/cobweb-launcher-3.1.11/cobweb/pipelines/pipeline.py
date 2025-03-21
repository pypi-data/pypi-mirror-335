from abc import ABC, abstractmethod
from cobweb.base import BaseItem


class Pipeline(ABC):

    @abstractmethod
    def build(self, item: BaseItem) -> dict:
        pass

    @abstractmethod
    def upload(self, table: str, data: list) -> bool:
        pass


