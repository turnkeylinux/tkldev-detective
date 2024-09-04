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
import json
from typing import Generator
import subprocess

from libtkldet.linter import FileLinter, FileItem, register_linter
from libtkldet.report import Report, FileReport, parse_report_level, Replacement
from libtkldet.apt_file import is_installed

if is_installed("shellcheck"):
    def insert_str(v: str, i: int, instr: str) -> str:
        return v[:i] + instr + v[i:]


    def expand_lines(lines: list[str]) -> Generator[str, None, None]:
        for line in lines:
            yield from line.splitlines()


    def format_replacement(
        path: str,
        line_span: tuple[int, int],
        column_span: tuple[int, int],
        replacements: list[dict],
    ) -> Replacement:
        start_line, end_line = line_span
        start_col, end_col = column_span

        start_line -= 1
        end_line -= 1

        lines = []

        with open(path, "r") as fob:
            for i, line in enumerate(fob):
                if i >= start_line and i <= end_line:
                    lines.append(line)

        for replacement in replacements:
            assert replacement["insertionPoint"] in ("beforeStart", "afterEnd")

            if replacement["insertionPoint"] == "beforeStart":
                line = replacement["line"] - start_line - 1
                lines[line] = insert_str(
                    lines[line], replacement["column"], replacement["replacement"]
                )
            elif replacement["insertionPoint"] == "afterEnd":
                line = replacement["endLine"] - start_line - 1
                lines[line] = insert_str(
                    lines[line], replacement["endColumn"] - 1, replacement["replacement"]
                )

        return Replacement(start_line, end_line, expand_lines(lines))


    @register_linter
    class Shellcheck(FileLinter):
        ENABLE_TAGS: set[str] = {
            "ext:sh",
            "ext:bash",
            "shebang:/bin/sh",
            "shebang:/bin/bash",
        }
        DISABLE_TAGS: set[str] = set()

        def check(self, item: FileItem) -> Generator[Report, None, None]:
            for report in json.loads(
                subprocess.run(
                    ["shellcheck", item.abspath, "-f", "json"],
                    capture_output=True,
                    text=True,
                ).stdout
            ):
                if report["column"] == report["endColumn"]:
                    column = None
                else:
                    column = (report["column"], report["endColumn"] - 1)

                if report["line"] == report["endLine"]:
                    line = report["line"]
                else:
                    line = (report["line"], report["endLine"])

                fix = report["fix"]
                if isinstance(report["fix"], dict):
                    fix = format_replacement(
                        item.abspath,
                        (report["line"], report["endLine"]),
                        (report["column"], report["endColumn"]),
                        fix["replacements"],
                    )

                yield FileReport(
                    item=item,
                    line=line,
                    column=column,
                    location_metadata="",
                    message="[{}] {}".format(
                        report["code"],
                        report["message"],
                    ),
                    fix=fix,
                    source="shellcheck",
                    level=parse_report_level(report["level"]),
                )
