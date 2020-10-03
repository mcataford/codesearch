from typing import List, Optional

import attr
from .settings import settings
from .base import IndexBase
from .prefix_tree import PrefixTree


@attr.s
class TrigramIndex(IndexBase):
    _threshold = attr.ib(default=settings.SIGNIFICANCE_THRESHOLD)
    _tree = attr.ib(attr.Factory(PrefixTree.initialize))

    def index(self, uid, key: str, content: str, trigrams):
        if content:
            trigrams = TrigramIndex.trigramize(content)

        for trigram in trigrams:
            self._tree.insert(trigram, uid)

    def query(self, query: str, haystack: Optional[List[str]] = None) -> List[str]:
        query_trigrams = TrigramIndex.trigramize(query)
        results = {}

        for trigram in query_trigrams:
            result_set = self._tree.get(trigram)
            if result_set:
                results[trigram] = result_set

        matches = {}

        for result in results:
            for doc in results[result]:
                matches[doc] = matches.get(doc, 0) + 1

        significant_results = []
        for uid, occurrences in matches.items():
            score = occurrences / len(query_trigrams)
            if score >= self._threshold:
                significant_results.append((f"document:{uid}", score))

        significant_results.sort(reverse=True, key=lambda x: x[0])
        return significant_results

    @staticmethod
    def trigramize(content: str) -> List[str]:
        return {content[pos : pos + 3].lower() for pos in range(len(content) - 2)}
