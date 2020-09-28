from base import IndexerBase
from pathlib import Path
from typing import Dict, List
import re
from time import perf_counter
from multiprocessing import Pool

import attr

from settings import settings

from process_utils import chunkify_content
from document_models import Corpus
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

    # Document corpus
    corpus = attr.ib(default=attr.Factory(Corpus))
    domain = attr.ib(default=attr.Factory(list))

    def index(self, paths: List[str]):
        start_time = perf_counter()
        discovered = []
        for path in paths:
            discovered.extend(self._discover(path))

        logger.info(f"[Discovery] Discovered {len(discovered)} files.")

        self._preload(discovered)
        self._populate_indices(self.corpus.collect_unprocessed_documents())
        end_time = perf_counter()

        logger.info(
            f"[Index status] {self.corpus.document_count} total files indexed in {end_time - start_time} seconds."
        )

    def query(self, query: str):
        start_time = perf_counter()
        trigram_results = self._trigram_index.query(query)

        logger.info(f"Narrowed down to {len(trigram_results)} files via trigram search")

        confirmed = []
        uniques = 0
        for lead in trigram_results:
            lead_content = self.corpus.get_document(key=lead[1]).content
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
        end_time = perf_counter()
        logger.info(
            f"{len(confirmed)} hits in {uniques} files ({end_time - start_time} seconds elapsed)."
        )
        return [r.to_dict() for r in confirmed]

    def _discover(self, path_root: str) -> Dict[str, str]:
        collected = []
        current = Path(path_root)

        # Avoid any excluded paths
        if any([current.match(x) for x in settings.EXCLUDES]):
            logger.info(f"[Discovery] {path_root} excluded.")
            return []

        if current.is_dir():
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
                    content = infile.read()
                    self.corpus.add_document(key=discovered_file, content=content)
                logger.info(f"[Preloading] Loaded {discovered_file} in memory")
            except Exception as e:
                logger.exception(e)
                logger.error(f"Could not read {discovered_file}, skipping.")

    def _populate_indices(self, uids):
        processes = settings.INDEXING_PROCESSES
        pool = Pool(processes=processes)
        chunks = chunkify_content(uids, processes)
        results = pool.map(self._bulk_process, chunks)
        # TODO: Refactor indices to populate cleanly.
        for result in results:
            self._trigram_index._trigrams.update(result[0])
            self._line_index._lines.update(result[1])

    def _bulk_process(self, uids: List[str]):
        for uid in uids:
            document = self.corpus.get_document(uid=uid)
            path = document.key
            content = document.content
            self._trigram_index.index(path, content)
            self._line_index.index(path, content)
            logger.info(f"[Indexing] Processed {path}")

        return (self._trigram_index._trigrams, self._line_index._lines)

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
