import pyinotify
import attr

from logger import get_logger

logger = get_logger(__name__)


@attr.s
class WatchHandler(pyinotify.ProcessEvent):
    indexer = attr.ib()

    def process_IN_MODIFY(self, event):
        c = self.indexer.discover(event.pathname)
        if c.get(event.pathname):
            logger.info(f"Reindexed {event.pathname}")
            self.indexer.index(event.pathname, c[event.pathname])
