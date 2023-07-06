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
from typing import Optional, Union
import typing
from dataclasses import dataclass
import os

ASSIGNMENT_OPERATORS = ["?=", ":=", "+=", "="]
CHECKS = ["ifeq", "ifneq", "ifdef", "ifndef"]
MAKEFILE_ENV = {"FAB_PATH": os.environ.get("FAB_PATH", '/turnkey/fab'), "FAB_SHARE_PATH": "/usr/share/fab"}

def split_value(raw: str) -> list[str]:
    chunks = ['']
    bracket_depth = 0
    for c in raw:
        if c == ')':
            bracket_depth -= 1
            chunks[-1] += ')'
        elif c == '(':
            bracket_depth += 1
            chunks[-1] += '('
        elif bracket_depth > 0:
            chunks[-1] += c
        elif c.isspace() and chunks[-1]:
            chunks.append('')
        else:
            chunks[-1] += c

    return chunks

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
class LazyVar:
    "a value referencing a variable we havn't resolved yet"
    name: str

ValueList = list[Union[str, LazyVar]]

@dataclass
class MutMakefileData:
    """holds variables set by makefiles"""

    variables: dict[str, ValueList]
    included: list[str]

    def resolve_var(self, value: str) -> ValueList:
        """expand make variables, env variables and split into multiple values"""
        out_var: list[str | LazyVar] = []

        if value.startswith("$(") and value.endswith(")"):
            var_name = value[2:-1]
            if var_name in MAKEFILE_ENV:
                out_var.append(MAKEFILE_ENV[var_name])
            else:
                out_var.extend(self.variables.get(var_name,
                    [LazyVar(var_name)]))
        else:
            out_var.extend(split_value(value))
        return out_var

    def assign_var(self, name: str, operator: str, values: str):
        """process a variable assignment"""
        if operator == "+=":
            # add to existing definition
            if name not in self.variables:
                self.variables[name] = []
            for value in split_value(values):
                self.variables[name].extend(self.resolve_var(value))
        elif operator == "?=":
            # set only if not already set
            if name not in self.variables:
                self.variables[name] = []
                for value in split_value(values):
                    self.variables[name].extend(self.resolve_var(value))
        elif operator in ("=", ":="):
            # set unconditionally (these are semantically different operations)
            if name not in self.variables:
                self.variables[name] = []
            for value in split_value(values):
                self.variables[name].extend(self.resolve_var(value))
        else:
            raise ValueError(f"unknown operator {operator!r}")

    def finish(self):
        ''' resolve unresolved variables and return a concrete version of this
        class with simpler typing '''
        # variables in make are often not resolved immediately, and such the
        # actual value of a variable may not be available until parsing has
        # finished
        #
        # furthermore values may resolve to other variables that also have not
        # yet been resolved and so on.
        # 
        # smart ways of handling this include chains of dependent variables or
        # handling the semantic difference between `=`, `:=` and similar
        # operations.
        #
        # we don't do that, we just try to resolve everything in a loop until
        # done

        done = False
        while not done:
            keys = list(self.variables.keys())
            for key in keys:
                done = True
                values = self.variables[key]
                new_values = []
                for value in values:
                    if isinstance(value, str):
                        new_values.append(value)
                    elif isinstance(value, LazyVar):
                        new_v = self.variables.get(value.name,
                                [f'$({value.name})'])
                        if isinstance(new_v , LazyVar):
                            done = False
                        new_values.extend(new_v)
                self.variables[key] = new_values

        new_variables = {key: list(values) for key, values in
                self.variables.items()}
        new_included = list(self.included)
        return MakefileData(typing.cast(dict[str, list[str]], new_variables), new_included)

@dataclass
class MakefileData(MutMakefileData):
    """holds variables set by makefiles"""

    variables: dict[str, list[str]]
    included: list[str]

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

    def to_dict(self) -> dict:
        return {
            'variables': self.variables,
            'included': self.included
        }


def parse_makefile(
    path: str, makefile_data: Optional[MakefileData] = None
) -> MakefileData:
    """attempts to naively get all variables defined in makefile tree. This
    function is recursive and makefile_data is used when including other
    makefiles"""
    if makefile_data is None:
        makefile_data = MakefileData({}, [])

    makefile_data.included.append(path)

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
    return makefile_data.finish()
