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

"""very naive cpp parser for plan parsing"""

from os.path import join, isfile
from dataclasses import dataclass
from .error import (
    PlanNotFoundError,
    UnknownPlanDirectiveError,
    InvalidPlanError,
)

static_vars = {"KERNEL": "", "DEBIAN": "", "AMD64": ""}


@dataclass
class PlanEntry:
    """A single package entry in a plan"""

    package_name: str
    """name of a package references in a plan"""

    include_stack: list[str]
    """path to each plan in the hierarchy of includes that resulted in this
    package being installed.

    ``include_stack[0]`` is the highest level plan being processed
    (usually an appliance ``plan/main``)

    ``include_stack[-1]`` is the file this specific package was found in.
    (either the ``plan/main`` or a file it's included at some point during the
    build process, such as ``${FAB_PATH}/common/plans/turnkey/mysql``)
    """

    def get_plan_path(self) -> str:
        """Path to plan file which contains this package"""
        return self.include_stack[-1]


def _include_plan(
    name: str, include_paths: list[str], plan_stack: list[str]
) -> list[PlanEntry]:
    for path in include_paths:
        if isfile(join(path, name)):
            return _parse_plan(join(path, name), include_paths, plan_stack)
    raise PlanNotFoundError(name)


def _remove_multiline_comments(raw: str) -> str:
    """Remove multiline cpp comments (in the form /* I'm a comment */)"""

    out = ""
    comment_depth = 0
    comment_begun = False

    for char in raw:
        if comment_depth > 0:
            if comment_begun:
                if char == "/":
                    comment_depth -= 1
                comment_begun = False
            elif char == "*":
                comment_begun = True

        elif comment_begun:
            if char == "*":
                comment_depth += 1
            else:
                out += "/" + char
            comment_begun = False
        elif char == "/":
            comment_begun = True
        else:
            out += char

    return out


# ignoring lints in this function:
# - C901 (too complex), breaking this down further
#       would obfuscate what it does
# - PLW0912 (too many branches), as above
# - PLW2901 (iteration variable overwritten), variable's meaning does not
#       change with overwrite.


def _parse_plan(  # noqa: C901, PLR0912
    path: str, include_paths: list[str], plan_stack: list[str] | None = None
) -> list[PlanEntry]:
    """Parse a plan

    (uses cpp, but notably does not use *most* cpp functionality).
    This code will not work on *most* cpp related projects
    """

    if plan_stack is None:
        plan_stack = [path]
    else:
        plan_stack.append(path)

    # list of packages we've included
    packages: list[PlanEntry] = []

    # keeps track of if-else' blocks
    #
    # number of items in the stack is how many "if statements" deep we are
    # (a length of 4, would indicate we're 4 "if statements" deep)
    #
    # the boolean value at a given position in the stack indicates if the check
    # is "true".
    cond_stack: list[bool] = []

    with open(path, "r") as fob:
        data = _remove_multiline_comments(fob.read())

    for line in data.splitlines():
        # remove single line comment
        if "//" in line:
            line = line.split("//", 1)[0]  # noqa: PLW2901
        # honestly would've thought hashes in cpp code wouldn't work like this,
        # but apparently it does
        if not line.startswith("#") and "#" in line:
            line = line.split("#", 1)[0]  # noqa: PLW2901

        line = line.strip()  # noqa: PLW2901

        if not line:
            continue

        if line.startswith("#endif"):
            if not cond_stack:
                error_message = (
                    f"unbalanced #if* and #endif directives in plan {path}"
                )
                raise InvalidPlanError(error_message)
            cond_stack.pop()
            continue

        if not cond_stack or cond_stack[-1]:
            # either we're not in a condition, or the current block's check
            # evaluated to True
            if line.startswith("#ifdef"):
                check_var = line[6:].strip()
                cond_stack.append(check_var in static_vars)
            elif line.startswith("#ifndef"):
                check_var = line[6:].strip()
                cond_stack.append(check_var not in static_vars)
            elif line.startswith("#else"):
                assert cond_stack
                cond_stack[-1] = not cond_stack[-1]
            elif line.startswith("#include"):
                packages.extend(
                    _include_plan(
                        line[8:].strip().strip("<>"),
                        include_paths,
                        plan_stack[:],
                    )
                )
            elif line.startswith("#"):
                raise UnknownPlanDirectiveError(line)
            else:
                assert "=" not in line, "assumption broken: '=' in plan"
                packages.append(PlanEntry(line.strip(), plan_stack[:]))
        else:
            # inside the branch we DON'T want to follow given a conditional
            if line.startswith("#ifdef"):
                # any further conditions inside this should also be ignored
                cond_stack.append(False)
            continue
    return packages


def parse_plan(path: str) -> list[PlanEntry]:
    """Parse a plan and return a plan entry for each package"""
    return _parse_plan(path, ["/turnkey/fab/common/plans"])
