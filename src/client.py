import socket
import json
from settings import settings
from pathlib import Path
from colors import highlight

import curses


def display_handler(stdscr, buffer):
    current_y = 0
    stdscr.refresh()
    curses.start_color()
    y, x = stdscr.getmaxyx()
    pad = curses.newpad(y, x)
    while True:
        pad.addstr(0, 0, "".join(buffer[current_y : current_y + y - 1]))
        pad.refresh(0, 0, 0, 0, y, x)
        key = stdscr.getch()

        if key in [81, 113]:
            break
        elif key == curses.KEY_UP:
            current_y = max(0, current_y - 1)
        elif key == curses.KEY_DOWN:
            current_y = min(len(buffer), current_y + 1)
        elif key == curses.KEY_NPAGE:
            current_y = min(len(buffer), current_y + y + 1)
        elif key == curses.KEY_PPAGE:
            current_y = max(0, current_y - y - 1)


def search(query):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((settings.SOCKET_HOST, settings.SOCKET_PORT))
        s.sendall(query.encode())
        length = int(s.recv(8).decode())
        results = None

        with open(Path(settings.BUFFER_PATH).expanduser(), "rb") as infile:
            results = infile.read().decode()

        results = json.loads(results)

        output = []
        for result in results:
            with open(result["key"], "r") as infile:
                highlighted_text = infile.read()[
                    result["offset_start"] : result["offset_end"]
                ]
                line_number = result["line_start"]
                output.append(result["key"] + "\n")
                for l in highlighted_text.split("\n"):
                    output.append(f"{line_number} {l}\n")
                    line_number += 1

                output.append("\n")
                output.append("\n")

        s.close()

        curses.wrapper(display_handler, output)
