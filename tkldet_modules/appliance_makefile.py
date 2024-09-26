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

"""Linters for appliance makefile"""

from collections.abc import Generator
from typing import ClassVar

from libtkldet.fuzzy import fuzzy_suggest
from libtkldet.linter import FileItem, FileLinter, register_linter
from libtkldet.report import FileReport, Report, ReportLevel


@register_linter
class ApplianceMakefileLinter(FileLinter):
    """Linter for appliance makefile"""

    ENABLE_TAGS: ClassVar[set[str]] = {"appliance-makefile"}
    DISABLE_TAGS: ClassVar[set[str]] = set()

    def check(self, item: FileItem) -> Generator[Report, None, None]:
        mk_confvars = ["COMMON_CONF", "COMMON_OVERLAYS"]
        with open("/turnkey/fab/common/mk/turnkey.mk", "r") as fob:
            for line in fob:
                if line.startswith("CONF_VARS += "):
                    mk_confvars.extend(line.strip().split()[2:])

        in_define = False
        first_include = None

        with open(item.abspath, "r") as fob:
            for i, line in enumerate(fob):
                if in_define:
                    # ignore matches inside define, might cause false
                    # positives
                    if line.startswith("endef"):
                        in_define = False
                    continue
                elif line.startswith("define"):
                    # ignore matches inside define, might cause false
                    # positives
                    in_define = True
                    continue
                elif line.startswith("include"):
                    first_include = i
                    continue
                elif "=" in line:
                    if "+=" in line:
                        var = line.split("+=", 1)[0].strip()
                    else:
                        var = line.split("=", 1)[0].strip()
                    if var not in mk_confvars:
                        suggested_var = fuzzy_suggest(var, mk_confvars)
                        if suggested_var:
                            fix = (
                                f"did you mean {suggested_var!r}"
                                f" instead of {var!r} ?"
                            )
                        else:
                            fix = (
                                f"either replace with one of {mk_confvars}"
                                " or add it to turnkey.mk's list of valid"
                                " CONF_VARS"
                            )
                        yield FileReport(
                            item=item,
                            line=i + 1,
                            column=(1, len(var)),
                            location_metadata=None,
                            fix=fix,
                            message="variable set is not a known CONF_VAR",
                            source="appliance-makefile-linter",
                            level=ReportLevel.WARN,
                        )

                    if first_include:
                        yield FileReport(
                            item=item,
                            line=i + 1,
                            column=line.find("="),
                            location_metadata=None,
                            message="variable defined AFTER includes",
                            fix="move variable definitions to top of Makefile",
                            source="appliance-makefile-linter",
                            level=ReportLevel.WARN,
                        )
