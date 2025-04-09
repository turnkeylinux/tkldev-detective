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
try:
    import yaml
except ImportError:
    YAML = False
else:
    YAML = True
from collections.abc import Generator

from libtkldet.linter import FileItem, FileLinter, register_linter
from libtkldet.report import FileReport, Report, ReportLevel


class YamlLinter(FileLinter):
    ENABLE_TAGS: set[str] = {"ext:yaml", "ext:yml"}
    DISABLE_TAGS: set[str] = set()

    def check(self, item: FileItem) -> Generator[Report, None, None]:
        with open(item.abspath, "r") as fob:
            try:
                yaml.safe_load(fob)
            except yaml.constructor.ConstructorError:
                # ignore tags and other fancy stuff we can't easily check
                pass
            except yaml.parser.ParserError as e:
                yield FileReport(
                    item=item,
                    line=e.problem_mark.line,
                    column=e.problem_mark.column,
                    location_metadata=None,
                    message=f"{e.context} {e.problem}",
                    fix=None,
                    source="yaml_check",
                    level=ReportLevel.ERROR,
                )
            except yaml.scanner.ScannerError as e:
                yield FileReport(
                    item=item,
                    line=e.problem_mark.line,
                    column=e.problem_mark.column,
                    location_metadata=None,
                    message=f"{e.context} {e.problem}",
                    fix=None,
                    source="yaml_check",
                    level=ReportLevel.ERROR,
                )


if YAML:
    register_linter(YamlLinter)
