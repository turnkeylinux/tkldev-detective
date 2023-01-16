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
from typing import Generator
import stat
import os

from libtkldet.linter import FileLinter, register_linter, FileItem
from libtkldet.report import Report, FileReport, ReportLevel


@register_linter
class ApplianceConfDLinter(FileLinter):
    ENABLE_TAGS: set[str] = { "appliance-conf.d" }
    DISABLE_TAGS: set[str] = set()

    def check(self, item: FileItem) -> Generator[Report, None, None]:
        mode = os.lstat(item.abspath).st_mode
        if not ((mode & stat.S_IXUSR) or (mode & stat.S_IXGRP) or (mode & stat.S_IXOTH)):
            yield FileReport(
                item=item,
                line=None,
                column=None,
                location_metadata=None,
                message=f'conf.d script isn\'t executable',
                fix=f'`chmod +x {item.abspath}`',
                source='confd linter',
                level=ReportLevel.ERROR
            )
