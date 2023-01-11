COLORS = {"green": "\033[92m", "yellow": "\033[93m", "red": "\033[91m"}
ENDC = "\033[0m"


def highlight(text, color="green"):
    color_code = COLORS[color]
    return f"{color_code}{text}{ENDC}"
