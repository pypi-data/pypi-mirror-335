__version__ = "0.2.2"

import logging
from logging.handlers import RotatingFileHandler
from typing import Optional
from pathlib import Path
from logutils.palettes import get_palette, reset


class CustomFormatter(logging.Formatter):
    def __init__(self, colored=None):
        self.colored = colored

    def get_fmt_string(self, level):
        if self.colored:
            p = get_palette(self.colored)
            time_fmt = f"{p['time']}[%(asctime)s]{reset}"
            location_fmt = f"{p['location']}%(filename)s:%(funcName)s:%(lineno)d{reset}"
            match level:
                case logging.DEBUG:
                    level_fmt = f"{p['debug']}%(levelname)s{reset}"
                    message_fmt = f"{p['text']}%(message)s{reset}"
                case logging.INFO:
                    level_fmt = f"{p['info']}%(levelname)s{reset}"
                    message_fmt = f"{p['text']}%(message)s{reset}"
                case logging.WARNING:
                    level_fmt = f"{p['warning']}%(levelname)s{reset}"
                    message_fmt = f"{p['text']}%(message)s{reset}"
                case logging.ERROR:
                    level_fmt = f"{p['error']}%(levelname)s{reset}"
                    message_fmt = f"{p['error']}%(message)s{reset}"
                case logging.CRITICAL:
                    level_fmt = f"{p['critical']}{p['text']}%(levelname)s{reset}{reset}"
                    message_fmt = f"{p['critical']}{p['text']}%(message)s{reset}{reset}"
                case _:
                    raise Exception("Wrong log level")
        else:
            time_fmt = "[%(asctime)s]"
            level_fmt = "%(levelname)s"
            message_fmt = "%(message)s"
            location_fmt = "%(filename)s:%(funcName)s:%(lineno)d"
        fmt = f"{time_fmt} | {level_fmt} | {location_fmt} | {message_fmt}"
        return fmt

    def format(self, record):
        log_fmt = self.get_fmt_string(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_logger(
    name,
    handler_list=["stream"],
    level=logging.INFO,
    propagate=False,
    colored="regular",
    filepath: Optional[Path] = None,
):
    # If there was a previous logger with this ID, return it without creating another
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.DEBUG)

    # Create and add the handlets specified in handler_list. Options are:
    # - "stream": writes to stdout and colors the logs
    # - "file": writes to the specified file in a rotating manner without coloring
    handlers = []
    if "stream" in handler_list:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(CustomFormatter(colored=colored))
        handlers.append(handler)
    if "file" in handler_list and filepath is not None:
        if not filepath.exists():
            filepath.touch()
        handler = RotatingFileHandler(
            filepath, maxBytes=(1 * 100 * 1024 * 1024), backupCount=10
        )
        handler.setLevel(level)
        handler.setFormatter(CustomFormatter(colored=None))
        handlers.append(handler)
    # Do not invent random levelz plz
    if level not in (
        logging.DEBUG,
        logging.INFO,
        logging.WARNING,
        logging.ERROR,
        logging.CRITICAL,
    ):
        raise Exception(f"Level {level} not supported")
    for handler in handlers:
        logger.addHandler(handler)
    logger.propagate = propagate
    return logger
