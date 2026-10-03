from enum import Enum
from contextlib import contextmanager

from rich.console import Console
from rich.theme import Theme
from rich.text import Text
from rich.rule import Rule


class Status(Enum):
    """Result status class, acts as mapper for the sign depending on the status type"""
    OK = "[+]"
    WARN = "[!]"
    FAIL = "[x]"
    ABSENT = "[-]"
    INFO = "[*]"


THEME = Theme({
    "label":  "#6CA8D9",
    "value":  "#00E5FF",
    "dim":    "#8DA1B3",
    "header": "bold #BD93F9",
    "ok":     "#50FA7B",
    "warn":   "#FFB86C",
    "fail":   "#FF5555",
    "absent": "#FF5555",
    "info":   "#8BE9FD",
    "title":  "#98FF98",  # mint green
})

HEADER_LEAD = "════════════ "
HEADER_WIDTH = 90


class Printer:
    """Prints all terminal output: sections, status lines and prompts."""

    def __init__(self):
        self._console = Console(theme=THEME, highlight=False)
        self._console.width = min(HEADER_WIDTH, self._console.width)

    def _rule(self, title=""):
        self._console.print(Rule(title, style="header", align="left", characters="═"))

    def _header(self, title):
        title_formatted = Text.assemble((HEADER_LEAD, "header"), (title, "title"))
        self._rule(title_formatted)

    def _footer(self):
        self._rule()

    @contextmanager
    def section(self, title):
        self._header(title)
        try:
            yield
        finally:
            self._footer()
