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

from typing import Generator, Optional

from libtkldet.report import Report, ReportLevel, register_filter, ReportFilter
from libtkldet.linter import FileItem
from libtkldet.apt_file import find_python_package_from_import
from libtkldet.common_data import (
    is_package_to_be_installed, get_path_in_common_overlay
)
from os.path import dirname
import re

MISSING_MODULE_RE = re.compile(r"^Unable to import '(.*)'$")

def filter_packaged(report: Report, module_name: str) -> Optional[Report]:
    packages = find_python_package_from_import(module_name)

    modified_fix = report.fix or ''
    modified_message = report.message
    modified_level = report.level

    if not packages:
        if not report.fix:
            modified_fix = ""
        modified_fix += (
            " (unable to find module, module might be provided by"
            " overlay or by non-debian repo, if so ignore this lint)"
        )
    else:
        package_installed = False
        for package in packages:
            if is_package_to_be_installed(package):
                modified_level = ReportLevel.INFO
                modified_message += (f' ("{package}" likely provides this '
                +'module and will be installed at build time)')
                package_installed = True
                break
        if not package_installed:
            if len(packages) > 1:
                packages_str = ', '.join('"' + pkg + '"' for pkg in packages)
                modified_message += f' (perhaps you meant to add one of {packages_str} to the plan?)'
            else:
                modified_message += f' (perhaps you meant to add "{packages[0]}" to the plan?)'

    return report.modified(
        fix=modified_fix,
        message=modified_message,
        level=modified_level
    )

@register_filter
class MissingModuleFilter(ReportFilter):
    def filter(self, report: Report) -> Generator[Report, None, None]:
        if report.source == "pylint" and report.raw != None and report.raw["symbol"] == "import-error":
            match = MISSING_MODULE_RE.match(report.raw["message"])
            assert match is not None
            module_name = match.group(1)

            if isinstance(report.item, FileItem) and dirname(report.item.relpath) == 'overlay/usr/lib/inithooks/bin':
                temp_module_name = module_name
                if '.' in temp_module_name:
                    temp_module_name = temp_module_name.split('.', 1)[0]
                if get_path_in_common_overlay(f'/usr/lib/inithooks/bin/{temp_module_name}.py'):
                    # file exists in an overlay from somewhere, so this lint is
                    # definitely incorrect
                    return None

            packaged_report = filter_packaged(report, module_name)
            if packaged_report:
                yield packaged_report

        else:
            yield report
