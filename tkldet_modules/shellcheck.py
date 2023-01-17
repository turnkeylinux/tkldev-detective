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
from libtkldet.report import Report, FileReport, parse_report_level


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

            yield FileReport(
                item=item,
                line=(report["line"], report["endLine"]),
                column=(report["column"], report["endColumn"]),
                location_metadata="",
                message="[{}] {}".format(
                    report["code"],
                    report["message"],
                ),
                fix=report["fix"],
                source="shellcheck",
                level=parse_report_level(report["level"]),
            )
