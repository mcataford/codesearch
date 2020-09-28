import json
import socket
import pyinotify
import attr
from watcher import WatchHandler
from indexer import Indexer
from constants import QUERY_STRING_LENGTH
from pathlib import Path
from settings import settings

from logger import get_logger

logger = get_logger(__name__)


@attr.s
class Server:
    indexer = attr.ib()
    watched = attr.ib()
    _notifier = attr.ib(default=None)
    _socket = attr.ib(default=None)

    def _handle_socket(self, *, socket):
        socket.bind((settings.SOCKET_HOST, settings.SOCKET_PORT))
        socket.listen()

        logger.info(
            f"Listening on {settings.SOCKET_HOST}:{settings.SOCKET_PORT}",
            prefix="Server",
        )

        while True:
            conn, _ = socket.accept()
            query_string = conn.recv(QUERY_STRING_LENGTH).decode()
            logger.info(f"Query string: {query_string}", prefix="Query")
            if query_string:
                try:
                    query_results = self.indexer.query(query_string)
                    response = json.dumps(query_results).encode()
                    response_length = str(len(response.decode()))
                    with open(Path(settings.BUFFER_PATH).expanduser(), "wb") as outfile:
                        outfile.write(response)
                    conn.sendall(response_length.encode())
                except KeyboardInterrupt:
                    raise e
                except Exception as e:
                    logger.warning(e)
                    pass

    def _start_socket(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_obj:
                self._socket = socket_obj
                self._handle_socket(socket=socket_obj)
        except Exception as e:
            logger.warning(e)
            raise e

    def _start_watch(self):
        watch_manager = pyinotify.WatchManager()

        for path in self.watched:
            logger.info(f"Watching {path}", prefix="Server")
            watch_manager.add_watch(path, pyinotify.ALL_EVENTS, rec=True)

        event_handler = WatchHandler(indexer=self.indexer)
        notifier = pyinotify.ThreadedNotifier(watch_manager, event_handler)
        notifier.start()
        self._notifier = notifier

    def run(self):
        collected = {}

        self.indexer.index(self.watched)

        try:
            self._start_watch()
            self._start_socket()
        except:
            self._socket.close()
            self._notifier.stop()
