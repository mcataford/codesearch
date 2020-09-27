from abc import ABC, abstractmethod


class IndexerBase(ABC):
    @abstractmethod
    def discover(self, path: str):
        pass

    @abstractmethod
    def index(self, path: str):
        pass
