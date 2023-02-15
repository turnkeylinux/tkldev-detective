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

"""tools to extract variable definitions from makefiles, purpose built for
fab tool-chain on tkldev, so ignores tests & definitions, butchers most
functions, doesn't understand targets, makes more unspoken assumptions and probably
produces a lot of other erroneous output (if used for general makefile parsing)
"""
from typing import Optional
from dataclasses import dataclass
import os

ASSIGNMENT_OPERATORS = ["?=", ":=", "+=", "="]
CHECKS = ["ifeq", "ifneq", "ifdef", "ifndef"]
MAKEFILE_ENV = {"FAB_PATH": os.environ["FAB_PATH"], "FAB_SHARE_PATH": "/usr/share/fab"}


def parse_assignment(line: str) -> Optional[tuple[str, str, str]]:
    """attempt to parse a makefile assignment operation,
    if successful return tuple of (variable_name, operator, variable_value)
    """
    for operator in ASSIGNMENT_OPERATORS:
        if operator in line:
            name, value = line.split(operator, 1)
            if name.startswith("export "):
                name = name.split(" ", 1)[1]
            return name.strip(), operator, value.strip()
    return None


@dataclass
class CommonFabBuildData:
    "holds lists of paths of each component type included from common"

    overlays: list[str]
    conf: list[str]
    removelists: list[str]
    removelists_final: list[str]


@dataclass
class MakefileData:
    """holds variables set by makefiles"""

    variables: dict[str, list[str]]

    def resolve_var(self, value: str) -> list[str]:
        """expand make variables, env variables and split into multiple values"""
        if value.startswith("$(") and value.endswith(")"):
            var_name = value[2:-1]
            if var_name in MAKEFILE_ENV:
                return [MAKEFILE_ENV[var_name]]
            return self.variables.get(var_name, [])
        return value.split()

    def assign_var(self, name: str, operator: str, values: str):
        """process a variable assignment"""
        if operator == "+=":
            # add to existing definition
            if name not in self.variables:
                self.variables[name] = []
            for value in values.split():
                self.variables[name].extend(self.resolve_var(value))
        elif operator == "?=":
            # set only if not already set
            if name not in self.variables:
                self.variables[name] = []
                for value in values.split():
                    self.variables[name].extend(self.resolve_var(value))
        elif operator in ("=", ":="):
            # set unconditionally (these are semantically different operations)
            if name not in self.variables:
                self.variables[name] = []
            for value in values.split():
                self.variables[name].extend(self.resolve_var(value))
        else:
            raise ValueError(f"unknown operator {operator!r}")

    def __getitem__(self, key: str) -> list[str]:
        return self.variables[key]

    def to_fab_data(self) -> CommonFabBuildData:
        """return just the high level data relating to included overlays, conf
        and removelists"""
        return CommonFabBuildData(
            overlays=[*self["COMMON_OVERLAYS"]],
            conf=[*self["COMMON_CONF"]],
            removelists=[*self["COMMON_REMOVELISTS"]],
            removelists_final=[*self["COMMON_REMOVELISTS_FINAL"]],
        )


def parse_makefile(
    path: str, makefile_data: Optional[MakefileData] = None
) -> MakefileData:
    """attempts to naively get all variables defined in makefile tree. This
    function is recursive and makefile_data is used when including other
    makefiles"""
    if makefile_data is None:
        makefile_data = MakefileData({})

    # defines aren't checked we skip all lines inside a define block
    in_define = False

    # if checks are only checked if the condition applies
    in_if = False
    if_applies = False

    with open(path, "r") as fob:
        for line in fob:
            if in_define:
                if line.startswith("endef"):
                    in_define = False
                continue
            if in_if:
                if line.startswith("endif"):
                    in_if = False
                if not if_applies:
                    continue
            if line.startswith("define "):
                in_define = True
                continue
            if line.startswith("if"):
                in_if = True
                continue
            if line[0].isspace():
                continue
            if "=" in line:
                parsed = parse_assignment(line)
                if not parsed:
                    print("broken var parse {line!r}")
                else:
                    makefile_data.assign_var(*parsed)
            if line.startswith("include "):
                parse_makefile(
                    line.split(" ", 1)[1]
                    .strip()
                    .replace("$(FAB_PATH)", os.environ["FAB_PATH"])
                    .replace("$(FAB_SHARE_PATH)", "/usr/share/fab"),
                    makefile_data,
                )
    return makefile_data
