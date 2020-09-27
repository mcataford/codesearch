from typing import List, Optional

import attr
from settings import settings
from base import IndexBase


@attr.s
class TrigramIndex(IndexBase):
    _trigrams = attr.ib(default=attr.Factory(dict))
    _threshold = attr.ib(default=settings.SIGNIFICANCE_THRESHOLD)

    def index(self, key: str, content: str):
        self._trigrams[key] = self._trigramize(content)

    def query(self, query: str, haystack: Optional[List[str]] = None) -> List[str]:
        if not haystack:
            haystack = self._trigrams

        query_trigrams = self._trigramize(query)
        results = []

        for item in haystack:
            shared = self._trigrams[item].intersection(query_trigrams)
            ratio = len(shared) / len(query_trigrams)
            if ratio < self._threshold:
                continue

            results.append((ratio, item, list(shared)))

        results.sort(reverse=True, key=lambda x: x[0])

        return results

    def _trigramize(self, content: str) -> List[str]:
        return {content[pos : pos + 3].lower() for pos in range(len(content) - 2)}
