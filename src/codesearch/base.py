from abc import ABC, abstractmethod
from typing import List, Optional


class IndexBase(ABC):
    @abstractmethod
    def index(self, content: str, haystack: Optional[List[str]]):
        pass

    @abstractmethod
    def query(self, query: str) -> List[str]:
        pass


class IndexerBase(ABC):
    @abstractmethod
    def index(self, paths: List[str]):
        pass
