from .base import IndexBase
import attr

from .logger import get_logger

logger = get_logger(__name__)


@attr.s
class LineIndex(IndexBase):
    _lines = attr.ib(default=attr.Factory(dict))

    def index(self, key: str, content: str):
        self._lines[key] = {}
        current, count = 0, 0
        for line in content.split("\n"):
            self._lines[key][count] = (current, current + len(line))
            current += len(line)
            count += 1

    def query(self, key: str):
        return self._lines[key]
