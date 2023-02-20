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
from typing import Union, Generator, Type, Iterable
import textwrap

from .classifier import Item, FileItem
from . import colors as co
from .hint_extract import format_extract

@dataclass
class Replacement:
    begin_line: int
    end_line: int
    replacement: list[str]

class ReportLevel(Enum):
    """represents a "level" of report, from information through hard issues"""

    INFO = enum.auto()
    CONVENTION = enum.auto()
    REFACTOR = enum.auto()
    WARN = enum.auto()
    ERROR = enum.auto()

    def ansi_color_code(self) -> str:
        """returns an ansi escape code for color, for each level"""
        if self == self.INFO:
            return co.CYAN
        if self == self.CONVENTION:
            return co.CYAN
        if self == self.REFACTOR:
            return co.YELLOW
        if self == self.WARN:
            return co.YELLOW
        if self == self.ERROR:
            return co.RED
        return ""


def parse_report_level(raw: str) -> ReportLevel:
    """parse a string into a ReportLevel"""
    raw = raw.lower()
    if raw in ("i", "info", "note", "message"):
        return ReportLevel.INFO
    if raw in ("c", "convention"):
        return ReportLevel.CONVENTION
    if raw in ("r", "refactor"):
        return ReportLevel.REFACTOR
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
        "location_metadata",
        "message",
        "fix",
        "source",
        "level",
    ]

    item: Item
    "metadata on location of issue (path, tags, etc.)"

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

    raw: Union[dict, None] = None
    "raw data, format depends on `source`, not guaranteed to be set"

    def to_dict(self) -> dict:
        """ return this object as dictionary """
        return {
            "item": self.item,
            "location_metadata": self.location_metadata,
            "message": self.message,
            "fix": self.fix,
            "source": self.source,
            "level": self.level,
            "raw": self.raw,
        }

    def modified(self, **kwargs) -> "Report":
        """return a copy of this report with fields specified in
        `kwargs` replacing fields from this report"""
        data = self.to_dict()
        data.update(kwargs)
        return self.__class__(**data)

    def format(self, suggested_fix: bool = True) -> str:
        """formats report for terminal output and returns as a string"""
        out = "|  "
        out += f"{self.level.ansi_color_code()}{self.level.name} "

        lpad = len(self.level.name)
        wrapped_lines = textwrap.wrap(
            self.message, 70 - lpad, subsequent_indent=" " * lpad
        )
        for line in wrapped_lines:
            out += self.level.ansi_color_code() + line + co.RESET + "\n"

        # out += f"{self.message}{co.RESET}\n"
        if self.fix and suggested_fix:
            out += f"{co.CYAN}suggested fix: {self.fix}{co.RESET}\n"
        return out


@dataclass(frozen=True)
class FileReport(Report):
    """
    Holds all information about a particular issue in a particular location
    in a particular file possibly including metadata, possible fixes,
    severity, which linter created the report, etc.
    """

    line: Union[int, tuple[int, int], None] = None
    "line or (begin_line, end_line) issue occurs"

    column: Union[int, tuple[int, int], None] = None
    "column or (begin_column, end_column) issue occurs"

    def format(self, suggested_fix: bool = True) -> str:
        """formats report for terminal output and returns as a string"""
        out = super().format(False)
        if isinstance(self.item, FileItem):
            if self.line:
                out += f"@{self.item.relpath} +{self.line}\n"
                out += (
                    "\n".join(format_extract(self.item.abspath, self.line, self.column))
                    + "\n"
                )
            else:
                out += f"@{self.item.relpath}\n"
            if self.fix and suggested_fix:
                if isinstance(self.fix, Replacement):
                    out += f'{co.CYAN}replace with:{co.RESET}\n'
                    for i, line in enumerate(self.fix.replacement):
                        out += str(i + self.fix.begin_line + 1).rjust(4) + ": "+ co.BOLD + co.BRIGHT_YELLOW + line + co.RESET + '\n'
                else:
                    out += f"{co.CYAN}suggested fix: {self.fix}{co.RESET}\n"
        return out.rstrip()

    def to_dict(self) -> dict:
        return {
            "item": self.item,
            "location_metadata": self.location_metadata,
            "message": self.message,
            "fix": self.fix,
            "source": self.source,
            "level": self.level,
            "raw": self.raw,
            "line": self.line,
            "column": self.column,
        }


class ReportFilter:
    """Last stop before presenting to the user, report filters can modify,
    split, generate or even remove reports"""

    WEIGHT: int = 100

    def filter(self, report: Report) -> Generator[Report, None, None]:
        """given a report filter or modify it

        there doesn't need to be a 1-1 relationship between inputs and outputs

        reports will be given to this function, and the reports it yields will
        be fed to all remaining filters, after all processing they will be
        presented to the user
        """
        raise NotImplementedError()


_FILTERS: list[Type[ReportFilter]] = []


def register_filter(filt: Type[ReportFilter]):
    """registers a report filter for use in tkldev-detective, must be called on
    all filters added"""
    _FILTERS.append(filt)
    return filt


def get_weighted_filters() -> list[ReportFilter]:
    """returns instances of registered filterss in order of weight"""
    return sorted(
        map(lambda x: x(), _FILTERS), key=lambda x: (x.WEIGHT, x.__class__.__name__)
    )


def filter_all_reports(reports: Iterable[Report]) -> Generator[Report, None, None]:
    """filters all reports through all filters in order of weight"""
    filters = get_weighted_filters()

    for report in reports:
        reports_curr = [report]
        reports_next = []
        for filt in filters:
            for c_report in reports_curr:
                reports_next.extend(filt.filter(c_report))
            reports_curr = reports_next
            reports_next = []
        yield from reports_curr
