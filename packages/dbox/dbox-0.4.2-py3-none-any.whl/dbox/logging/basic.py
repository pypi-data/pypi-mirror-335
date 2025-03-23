import logging
import sys

BASIC_LAYOUT = "{asctime} {levelname:7} {name} {message}"


def setup_basic_logging(
    root_level="INFO",
    fmt=BASIC_LAYOUT,
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stderr,
):
    """Quickly setup colored logging system.
    This will clear all existing handlers on root logger
    and attach a colored stream handler to stderr
    """
    formatter = logging.Formatter(fmt, style=style, datefmt=datefmt)
    root_handler = logging.StreamHandler(stream)
    root_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers[:] = []
    root.addHandler(root_handler)
    root.setLevel(root_level)
