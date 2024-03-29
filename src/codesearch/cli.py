import argparse

from pathlib import Path
from .server import Server
from .indexer import Indexer
from .client import search
from .settings import settings


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("command")
    parser.add_argument("--q", required=False)

    args = parser.parse_args()

    if args.command == "start":
        watched = [Path(p).expanduser() for p in settings.WATCHED]
        server = Server(
            indexer=Indexer(
                domain=watched,
                exclusions=settings.EXCLUDES,
                file_types=settings.FILE_TYPES,
            ),
            watched=watched,
        )
        server.run()
    elif args.command == "search":
        search(args.q)
