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

from libtkldet.classifier import ExactPathClassifier, register_classifier
from libtkldet.linter import FileLinter, register_linter, FileItem
from libtkldet.report import Report, ReportLevel


@register_classifier
class ApplianceMakefileClassifier(ExactPathClassifier):
    path: str = 'Makefile'
    tags: list[str] = ['appliance-makefile']


@register_linter
class ApplianceMakefileLinter(FileLinter):
    ENABLE_TAGS: set[str] = { "appliance-makefile" }
    DISABLE_TAGS: set[str] = set()

    def check(self, item: FileItem) -> Generator[Report, None, None]:
        MK_CONFVARS = ['COMMON_CONFS', 'COMMON_OVERLAYS']
        with open('/turnkey/fab/common/mk/turnkey.mk', 'r') as fob:
            for line in fob:
                if line.startswith('CONF_VARS += '):
                    MK_CONFVARS.extend(line.strip().split()[2:])

        in_define = False
        first_include = None

        with open(item.abspath, 'r') as fob:
            for i, line in enumerate(fob):
                if in_define:
                    if line.startswith("endef"):
                        in_define = False
                    continue
                elif line.startswith('define'):
                    in_define = True
                    continue
                elif line.startswith('include'):
                    first_include = i
                    continue
                elif '=' in line:
                    var = line.split('=')[0].strip()
                    if not var in MK_CONFVARS:
                        yield Report(
                            item,
                            line = i+1,
                            column = (0, len(var)-1),
                            location_metadata = None,
                            message = "variable set is not a known CONF_VAR",
                            fix = "either replace with one of {} or add it to"
                            "turnkey.mk's list of valid CONF_VARS",
                            source = 'appliance-makefile-linter',
                            level = ReportLevel.WARN)

                    if first_include:
                        yield Report(
                            item,
                            line = i+1,
                            column = line.find('='),
                            location_metadata = None,
                            message = "variable defined AFTER includes",
                            fix = "move variable definitions to top of Makefile",
                            source = 'appliance-makefile-linter',
                            level = ReportLevel.WARN)




