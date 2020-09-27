import argparse

from server import Server
from indexer import Indexer
from client import search
import settings

parser = argparse.ArgumentParser()

parser.add_argument("command")
parser.add_argument("--q", required=False)

args = parser.parse_args()

if args.command == "start":
    server = Server(
        indexer=Indexer(trigram_threshold=settings.SIGNIFICANCE_THRESHOLD),
        watched=[".."],
    )
    server.run()
elif args.command == "search":
    search(args.q)
