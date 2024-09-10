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
from typing import Generator, ClassVar
import subprocess
from os.path import join, dirname, abspath

from libtkldet.linter import FileLinter, FileItem, register_linter
from libtkldet.report import Report, FileReport, parse_report_level
from libtkldet.apt_file import is_installed, is_in_path

if is_installed("pylint") and not is_in_path("ruff"):
    rcfile = join(dirname(dirname(abspath(__file__))), "pylint_rcfile")

    @register_linter
    class PyLinter(FileLinter):
        ENABLE_TAGS: ClassVar[set[str]] = {
            "ext:py",
            "shebang:/usr/bin/python",
            "shebang:/usr/bin/python3",
            "shebang:/usr/bin/python3.9",
            "shebang:/usr/bin/env python",
            "shebang:/usr/bin/env python3",
            "shebang:/usr/bin/env python3.9",
        }
        DISABLE_TAGS: ClassVar[set[str]] = set()

        def check(self, item: FileItem) -> Generator[Report, None, None]:
            for report in json.loads(
                subprocess.run(
                    [
                        "/usr/bin/pylint",
                        item.abspath,
                        "-f",
                        "json",
                        "--rcfile",
                        rcfile,
                    ],
                    capture_output=True,
                    text=True,
                ).stdout
            ):
                if report["obj"]:
                    location_metadata = (
                        f'{report["obj"]} in module {report["module"]}'
                    )
                else:
                    location_metadata = f'in base of module {report["module"]}'

                yield FileReport(
                    item=item,
                    line=report["line"],
                    column=report["column"],
                    location_metadata=location_metadata,
                    message="[{} | {}] {}".format(
                        report["message-id"],
                        report["symbol"],
                        report["message"],
                    ),
                    fix=None,
                    source="pylint",
                    raw=report,
                    level=parse_report_level(report["type"]),
                )
