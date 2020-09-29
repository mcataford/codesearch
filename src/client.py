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
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    pad = curses.newpad(y, x)
    while True:
        row = 0
        y_offset = 0
        pad.clear()
        while row < current_y + y - 1:
            l = buffer[current_y + y_offset]
            if l["type"] == "path":
                pad.addstr(row, 0, l["value"], curses.color_pair(1))
                row += 1
                y_offset += 1
            elif l["type"] == "sep":
                row += 1
                y_offset += 1
            else:
                pad.addstr(row, 0, str(l["lineno"]), curses.color_pair(1))
                pad.addstr(row, 5, l["value"])
                row += 1
                y_offset += 1

            if y_offset == y or current_y == y - 1:
                break

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
                output.append({"value": result["key"], "type": "path"})
                for l in highlighted_text.split("\n"):
                    output.append({"value": l, "type": "code", "lineno": line_number})
                    line_number += 1
                output.append({"type": "sep"})

        s.close()

        curses.wrapper(display_handler, output)
