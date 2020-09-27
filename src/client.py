import socket
import json

import settings

from colors import highlight


def search(query):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((settings.SOCKET_HOST, settings.SOCKET_PORT))
        s.sendall(query.encode())
        length = int(s.recv(4).decode())
        results = json.loads(s.recv(length).decode())

        for result in results:
            with open(result[0], "r") as infile:
                highlighted_text = infile.read()[result[1] : result[2]].replace(
                    query, highlight(query)
                )
                line_number = result[3]
                print(highlight(result[0]))
                for l in highlighted_text.split("\n"):
                    print(f"{highlight(line_number)} {l}")
                    line_number += 1
                print("\n\n")

        s.close()
