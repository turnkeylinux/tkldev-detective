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

"""Encapsulates "reports"

these are issues, warnings or notes about "Item"s produced by "Linter"s
"""
from dataclasses import dataclass
from enum import Enum
import enum
from typing import Iterator, Iterable, ClassVar
import textwrap

from .classifier import Item, FileItem
from . import colors as co
from .hint_extract import format_extract


@dataclass
class Replacement:
    """Holds replacement data

    a list of replacements in form provided by linters
    """

    begin_line: int
    end_line: int
    replacement: list[str]


class ReportLevel(Enum):
    """Represents a "level" of report, from information through hard issues"""

    # report represents some information that is not particularly important
    INFO = enum.auto()

    # report represents something that doesn't conform to some convention
    CONVENTION = enum.auto()

    # report represents a probable issue with readability, design
    # anti-pattern, complexity, etc.
    REFACTOR = enum.auto()

    # report represents a probable issue with code correctness, uses
    # inconsistent, error-prone, deprecated or otherwise non-ideal
    # functionality that could be improved
    WARN = enum.auto()

    # report represents a serious issue with code. It is syntactically invalid
    # or similarly incorrect
    ERROR = enum.auto()

    # report represents a possible or confirmed security issue and fix should
    # be seriously considered
    SECURITY = enum.auto()

    def ansi_color_code(self) -> str:
        """Return an ansi escape code for color, for each level"""
        colors = {
            self.INFO: co.CYAN,
            self.CONVENTION: co.CYAN,
            self.REFACTOR: co.YELLOW,
            self.WARN: co.YELLOW,
            self.ERROR: co.RED,
            self.SECURITY: co.RED,
        }
        return colors.get(self, "")


def parse_report_level(raw: str) -> ReportLevel:
    """Parse a string into a ReportLevel"""
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
    if raw in ("s", "security"):
        return ReportLevel.SECURITY
    error_message = f'couldn\'t parse unknown report level by name "{raw}"'
    raise ValueError(error_message)


@dataclass(frozen=True)
class Report:
    """Information to be presented to user

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

    location_metadata: str | None
    """
    location metadata (optional, can be anything such as function name, header
    section, etc, etc, etc.)
    """

    message: str
    "message describing issue"

    fix: str | None
    "message describing fix (might be empty)"

    source: str
    "what found this issue? Custom python class? shellcheck? pylint?"

    level: ReportLevel
    "error, warning, etc."

    raw: dict | None = None
    "raw data, format depends on `source`, not guaranteed to be set"

    def to_dict(self) -> dict:
        """Return this object as dictionary"""
        return {
            "item": self.item,
            "location_metadata": self.location_metadata,
            "message": self.message,
            "fix": self.fix,
            "source": self.source,
            "level": self.level,
            "raw": self.raw,
        }

    def modified(self, **kwargs: Item | str | dict | None) -> "Report":
        """Return new modified version of this report

        Return a copy of this report with fields specified in `kwargs`
        replacing fields from this report
        """
        data = self.to_dict()
        data.update(kwargs)
        return self.__class__(**data)

    def format(self, suggested_fix: bool = True) -> str:
        """Format report for terminal output and return as a string"""
        out = "|  "
        out += f"{self.level.ansi_color_code()}{self.level.name} "

        lpad = len(self.level.name)
        wrapped_lines = textwrap.wrap(
            self.message, 70 - lpad, subsequent_indent=" " * lpad
        )
        for line in wrapped_lines:
            out += self.level.ansi_color_code() + line + co.RESET + "\n"

        if self.fix and suggested_fix:
            out += f"{co.CYAN}suggested fix: {self.fix}{co.RESET}\n"
        return out


@dataclass(frozen=True)
class FileReport(Report):
    """Holds information about a report for a file

    Holds all information about a particular issue in a particular location
    in a particular file possibly including metadata, possible fixes,
    severity, which linter created the report, etc.
    """

    line: int | tuple[int, int] | None = None
    "line or (begin_line, end_line) issue occurs"

    column: int | tuple[int, int] | None = None
    "column or (begin_column, end_column) issue occurs"

    def format(self, suggested_fix: bool = True) -> str:
        """Format report for terminal output and return as a string"""
        out = super().format(suggested_fix=False)
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
                    out += f"{co.CYAN}replace with:{co.RESET}\n"
                    for i, line in enumerate(self.fix.replacement):
                        out += (
                            str(i + self.fix.begin_line + 1).rjust(4)
                            + ": "
                            + co.BOLD
                            + co.BRIGHT_YELLOW
                            + line
                            + co.RESET
                            + "\n"
                        )
                else:
                    out += f"{co.CYAN}suggested fix: {self.fix}{co.RESET}\n"
        return out.rstrip()

    def to_dict(self) -> dict:
        """Return object as dictionary"""
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
    """A filter to change reports before presenting

    Last stop before presenting to the user, report filters can modify,
    split, generate or even remove reports
    """

    WEIGHT: ClassVar[int] = 100

    def filter(self, report: Report) -> Iterator[Report]:
        """Given a report filter or modify it

        There doesn't need to be a 1-1 relationship between inputs and outputs

        Reports will be given to this function, and the reports it yields will
        be fed to all remaining filters, after all processing they will be
        presented to the user
        """
        raise NotImplementedError


_FILTERS: list[type[ReportFilter]] = []


def register_filter(filt: type[ReportFilter]) -> type[ReportFilter]:
    """Register a report filter

    Must be called on all filters added
    """
    _FILTERS.append(filt)
    return filt


def get_weighted_filters() -> list[ReportFilter]:
    """Return instances of registered filters in order of weight"""
    return sorted(
        (x() for x in _FILTERS),
        key=lambda x: (x.WEIGHT, x.__class__.__name__)
    )


def filter_all_reports(reports: Iterable[Report]) -> Iterator[Report]:
    """Filter all reports through all filters in order of weight"""
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
