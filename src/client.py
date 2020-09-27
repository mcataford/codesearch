import socket
import json

from settings import settings

from colors import highlight


def search(query):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((settings.SOCKET_HOST, settings.SOCKET_PORT))
        s.sendall(query.encode())
        length = int(s.recv(4).decode())
        results = json.loads(s.recv(length).decode())

        for result in results:
            with open(result["key"], "r") as infile:
                highlighted_text = infile.read()[
                    result["offset_start"] : result["offset_end"]
                ].replace(query, highlight(query))
                line_number = result["line_start"]
                print(highlight(result["key"]))
                for l in highlighted_text.split("\n"):
                    print(f"{highlight(line_number)} {l}")
                    line_number += 1
                print("\n\n")

        s.close()
