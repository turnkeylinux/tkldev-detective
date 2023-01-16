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

from libtkldet.linter import FileLinter, FileItem, register_linter
from libtkldet.report import Report, ReportLevel


@register_linter
class JsonLinter(FileLinter):
    ENABLE_TAGS: set[str] = {
        "ext:json",
    }
    DISABLE_TAGS: set[str] = set()

    def check(self, item: FileItem) -> Generator[Report, None, None]:
        with open(item.abspath, 'r') as fob:
            try:
                json.load(fob)
            except json.decoder.JSONDecodeError as e:
                yield Report(
                    item,
                    line=e.lineno,
                    column=e.colno,
                    location_metadata=None,
                    message=e.msg,
                    fix=None,
                    source='json_check',
                    level=ReportLevel.ERROR
                )
