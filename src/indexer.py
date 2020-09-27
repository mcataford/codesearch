from base import IndexerBase
from pathlib import Path
from typing import Dict, List
import re

import attr

from settings import settings

from trigram_index import TrigramIndex
from line_index import LineIndex
from logger import get_logger

logger = get_logger(__name__)


@attr.s
class SearchResult:
    key = attr.ib()
    offset_start = attr.ib()
    offset_end = attr.ib()
    line_start = attr.ib()
    line_end = attr.ib()

    def to_dict(self):
        return {
            "key": self.key,
            "offset_start": self.offset_start,
            "offset_end": self.offset_end,
            "line_start": self.line_start,
            "line_end": self.line_end,
        }


@attr.s
class Indexer(IndexerBase):
    # Indices
    _trigram_index = attr.ib(default=attr.Factory(TrigramIndex))
    _line_index = attr.ib(default=attr.Factory(LineIndex))

    domain = attr.ib(default=attr.Factory(list))
    _collected = attr.ib(default=attr.Factory(dict))

    def index(self, paths: List[str]):
        discovered = []
        for path in paths:
            discovered.extend(self._discover(path))

        logger.info(f"[Discovery] Discovered {len(discovered)} files.")

        self._preload(discovered)
        for path in self._collected:
            self._process(path)

    def query(self, query: str):
        trigram_results = self._trigram_index.query(query)

        logger.info(f"Narrowed down to {len(trigram_results)} files via trigram search")

        confirmed = []
        uniques = 0
        for lead in trigram_results:
            lead_content = self._collected[lead[1]]
            results = re.finditer(query, lead_content)
            hits_in_lead = []
            for hit in results:
                start_line, end_line = self._find_line_range(
                    lead[1], hit.start(), hit.end()
                )
                start_offset = self._line_index.query(lead[1])[start_line][0]
                end_offset = self._line_index.query(lead[1])[end_line][1]

                hits_in_lead.append(
                    SearchResult(
                        key=lead[1],
                        offset_start=start_offset,
                        offset_end=end_offset,
                        line_start=start_line,
                        line_end=end_line,
                    )
                )

            if hits_in_lead:
                confirmed.extend(hits_in_lead)
                uniques += 1

        logger.info(f"{len(confirmed)} hits in {uniques} files.")
        return [r.to_dict() for r in confirmed]

    def _discover(self, path_root: str) -> Dict[str, str]:
        collected = []
        current = Path(path_root)

        # Avoid any excluded paths
        if any([current.match(x) for x in settings.EXCLUDES]):
            logger.info(f"[Discovery] {path_root} excluded.")
            return []

        if current.is_dir():
            logger.info(list(current.iterdir()))
            for child_path in current.iterdir():
                collected.extend(self._discover(str(child_path)))

            return collected

        if current.suffix not in settings.FILE_TYPES:
            return []

        logger.info(f"Collected {path_root}")
        return [path_root]

    def _preload(self, discovered: List[str]):
        for discovered_file in discovered:
            try:
                with open(discovered_file, "r") as infile:
                    self._collected[discovered_file] = infile.read()
                logger.info(f"[Preloading] Loaded {discovered_file} in memory")
            except:
                logger.error(f"Could not read {discovered_file}, skipping.")

    def _process(self, path: str):
        p = Path(path)
        content = self._collected[path]

        self._trigram_index.index(path, content)

        content = self._collected[path]
        self._line_index.index(path, content)

    def _find_closest_line(self, path, index):
        content = self._line_index.query(path)

        for l in content:
            if content[l][0] <= index <= content[l][1]:
                return l

        return 0

    def _find_line_range(self, key, start, end, padding=5):
        start_line = self._find_closest_line(key, start)
        end_line = self._find_closest_line(key, end)

        start_line_range = max(0, start_line - 5)
        end_line_range = min(len(self._line_index.query(key)) - 1, end_line + 5)

        return (start_line_range, end_line_range)
