# Copyright (c) Turnkey GNU/Linux <admin@turnkeylinux.org>
#
# this file is part of tkldev-detective.
#
# tkldev-detective is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# tkldev-detective is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# tkldev-detective. If not, see <https://www.gnu.org/licenses/>.

"""Encapsulates "reports", these are issues, warnings or notes about "Item"s
produced by "Linter"s"""
from dataclasses import dataclass
from enum import Enum
import enum
from typing import Union

from .classifier import Item, FileItem
from .colors import CYAN, YELLOW, RED, RESET
from .hint_extract import format_extract


class ReportLevel(Enum):
    """represents a "level" of report, from information through hard issues"""

    INFO = enum.auto()
    CONVENTION = enum.auto()
    WARN = enum.auto()
    ERROR = enum.auto()

    def ansi_color_code(self) -> str:
        """returns an ansi escape code for color, for each level"""
        if self == self.INFO:
            return CYAN
        if self == self.CONVENTION:
            return CYAN
        if self == self.WARN:
            return YELLOW
        if self == self.ERROR:
            return RED
        return ""


def parse_report_level(raw: str) -> ReportLevel:
    """parse a string into a ReportLevel"""
    raw = raw.lower()
    if raw in ("i", "info", "note", "message"):
        return ReportLevel.INFO
    if raw in ("c", "convention"):
        return ReportLevel.CONVENTION
    if raw in ("w", "warn", "warning"):
        return ReportLevel.WARN
    if raw in ("e", "err", "error", "fatal", "critical"):
        return ReportLevel.ERROR
    raise ValueError(f'couldn\'t parse unknown report level by name "{raw}"')


@dataclass(frozen=True)
class Report:
    """
    Holds all information about a particular issue in a particular location
    possibly including metadata, possible fixes, severity, which linter
    created the report, etc.
    """

    __slots__ = [
        "item",
        "line",
        "column",
        "location_metadata",
        "message",
        "fix",
        "source",
        "level",
    ]

    item: Item
    "metadata on location of issue (path, tags, etc.)"

    line: Union[int, tuple[int, int]]
    "line or (begin_line, end_line) issue occurs"

    column: Union[int, tuple[int, int], None]
    "column or (begin_column, end_column) issue occurs"

    location_metadata: Union[str, None]
    """
    location metadata (optional, can be anything such as function name, header
    section, etc, etc, etc.)
    """

    message: str
    "message describing issue"

    fix: Union[str, None]
    "message describing fix (might be empty)"

    source: str
    "what found this issue? Custom python class? shellcheck? pylint?"

    level: ReportLevel
    "error, warning, etc."

    def format(self) -> str:
        """formats report for terminal output and returns as a string"""
        out = "|  "
        out += f"{self.level.ansi_color_code()}{self.level.name} "
        out += f"{self.message}{RESET}\n"
        if isinstance(self.item, FileItem):
            out += f"@{self.item.relpath} +{self.line}\n"
            out += "\n".join(format_extract(self.item.abspath, self.line, self.column))
        return out
