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

import yaml
from typing import Generator

from libtkldet.linter import FileLinter, FileItem, register_linter
from libtkldet.report import Report, ReportLevel, register_filter, ReportFilter
from libtkldet.apt_file import find_python_package
from libtkldet.common_data import is_package_to_be_installed
import re

MISSING_MODULE_RE = re.compile(r"^Unable to import '(.*)'$")


@register_filter
class MissingModuleFilter(ReportFilter):
    def filter(self, report: Report) -> Generator[Report, None, None]:
        if report.source == "pylint" and report.raw["symbol"] == "import-error":
            module_name = MISSING_MODULE_RE.match(report.raw["message"]).group(1)
            if '.' in module_name:
                module_name = module_name.split('.', 1)[0]
            package = find_python_package(module_name)

            modified_fix = report.fix or ''
            modified_message = report.message
            modified_level = report.level

            if not package:
                if not report.fix:
                    modified_fix = ""
                modified_fix += (
                    " (unable to find module, module might be provided by"
                    " overlay or by non-debian repo, if so ignore this lint)"
                )
            else:
                if not is_package_to_be_installed(package):
                    modified_message += f' (perhaps you meant to add "{package}" to the plan?)'
                else:
                    modified_level = ReportLevel.WARN
                    modified_message += (f' ("{package}" likely provides this '
                    +'module and will be installed, so this is probably safe to'
                    +' ignore)')

            yield report.modified(
                fix=modified_fix, 
                message=modified_message,
                level=modified_level
            )
        else:
            yield report
