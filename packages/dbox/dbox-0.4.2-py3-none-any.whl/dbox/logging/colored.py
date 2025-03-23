import logging
import sys
from typing import Dict, Optional

from colorama import Back, Fore, Style

log = logging.getLogger(__name__)


# credit: https://gist.github.com/joshbode/58fac7ababc700f51e2a9ecdebe563ad
class ColoredFormatter(logging.Formatter):
    """Colored log formatter."""

    DEFAULT_COLOR_MAP = {
        "DEBUG": Fore.CYAN,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.RED + Back.WHITE + Style.BRIGHT,
    }
    DEFAULT_LAYOUT = "{asctime} {color}{levelname:7}{reset} {name} {message}"

    def __init__(self, *args, colors: Optional[Dict[str, str]] = None, **kwargs) -> None:
        """Initialize the formatter with specified format strings."""

        super().__init__(*args, **kwargs)
        self.colors = colors if colors else {}

    def format(self, record) -> str:
        """Format the specified record as text."""
        record.color = self.colors.get(record.levelname, "")
        record.reset = Style.RESET_ALL
        return super().format(record)

    @classmethod
    def create(
        cls,
        fmt=DEFAULT_LAYOUT,
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S",
        colors=DEFAULT_COLOR_MAP,
    ):
        return ColoredFormatter(fmt, style=style, datefmt=datefmt, colors=colors)


def setup_colored_logging(
    root_level="INFO",
    fmt=ColoredFormatter.DEFAULT_LAYOUT,
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
    colors=ColoredFormatter.DEFAULT_COLOR_MAP,
    stream=sys.stderr,
):
    """Quickly setup colored logging system.
    This will clear all existing handlers on root logger
    and attach a colored stream handler to stderr
    """
    formatter = ColoredFormatter.create(fmt, style=style, datefmt=datefmt, colors=colors)
    colored_handler = logging.StreamHandler(stream)
    colored_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers[:] = []
    root.addHandler(colored_handler)
    root.setLevel(root_level)
