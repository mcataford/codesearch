import logging
import sys
import attr

from colors import highlight


@attr.s
class Logger:
    logger = attr.ib()

    def info(self, message, prefix=None):
        prefix_str = ""
        if prefix:
            prefix_str = highlight(f"[{prefix}]", "green")

        self.logger.info(f"{prefix_str} {message}")

    def warning(self, message, prefix=None):
        prefix_str = ""
        if prefix:
            prefix_str = highlight(f"[{prefix}]", "yellow")

        self.logger.warning(f"{prefix_str} {message}")


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)

    logger_obj = Logger(logger=logger)

    return logger_obj
