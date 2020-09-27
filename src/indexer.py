from base import IndexerBase
from pathlib import Path
from typing import Dict
import re

import attr

import settings


from logger import get_logger

logger = get_logger(__name__)


@attr.s
class Indexer(IndexerBase):
    _trigrams = attr.ib(default=attr.Factory(dict))
    _collected = attr.ib(default=attr.Factory(dict))
    _lines = attr.ib(default=attr.Factory(dict))
    trigram_threshold = attr.ib(default=0)

    @property
    def trigrams(self):
        return dict(self._trigrams)

    def discover(self, path_root: str) -> Dict[str, str]:
        logger.info(f"Collecting {path_root}")
        collected = {}

        if any([x in path_root for x in settings.excludes]):
            return {}

        current = Path(path_root)

        if current.is_dir():
            for child_path in current.iterdir():
                collected.update(self.discover(str(child_path)))

            self._collected.update(collected)

            return dict(self._collected)
        if current.suffix not in settings.types:
            return {}

        try:
            with open(current, "r") as infile:
                self._collected[str(current.resolve())] = infile.read()
        except:
            pass

        return dict(self._collected)

    def index(self, path: str, content: str):
        p = Path(path)

        self._trigrams[path] = set()

        for idx in range(len(content) - 2):
            self._trigrams[path].add(content[idx : idx + 3])

        self._lines[path] = {}

        content = self._collected[path]
        current, count = 0, 0
        for line in self._collected[path].split("\n"):
            self._lines[path][count] = (current, current + len(line))
            current += len(line)
            count += 1

    def query(self, query: str):
        trigram_results = self.search_trigrams(query)
        confirmed = self.search_content(query, trigram_results)

        return confirmed

    def find_closest_line(self, path, index, offset=0):
        content = self._lines[path]

        for l in content:
            if content[l][0] <= index <= content[l][1]:
                return l

        logger.error(f"{path} {index}")
        logger.error(content)
        return 0

    def search_content(self, query: str, leads):
        confirmed = []
        uniques = 0
        for lead in leads:
            lead_content = self._collected[lead[1]]
            results = re.finditer(query, lead_content)
            hits_in_lead = []
            for hit in results:
                start_line = self.find_closest_line(lead[1], hit.start())
                end_line = self.find_closest_line(lead[1], hit.end())

                start_line_range = max(0, start_line - 5)
                end_line_range = min(len(self._lines[lead[1]]) - 1, end_line + 5)

                hits_in_lead.append(
                    (
                        lead[1],
                        self._lines[lead[1]][start_line_range][0],
                        self._lines[lead[1]][end_line_range][1],
                        start_line_range,
                        end_line_range,
                    )
                )

            if hits_in_lead:
                confirmed.extend(hits_in_lead)
                uniques += 1

        logger.info(f"{len(confirmed)} hits in {uniques} files.")
        return confirmed

    def search_trigrams(self, query: str):
        query_trigrams = [query[idx : idx + 3] for idx in range(len(query) - 2)]
        results = []

        for item in self.trigrams:
            shared = self.trigrams[item].intersection(query_trigrams)
            ratio = len(shared) / len(query_trigrams)
            if ratio < self.trigram_threshold:
                continue

            results.append((ratio, item, list(shared)))

        results.sort(reverse=True, key=lambda x: x[0])

        logger.info(f"Narrowed down to {len(results)} files via trigram search")

        return results
