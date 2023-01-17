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

"""
Utilities relating to classification/linting files
"""
from typing import Optional


def position_from_char_offset(path: str, offset: int) -> Optional[tuple[int, int]]:
    line = 0
    col = 0
    with open(path, "r") as fob:
        for i, c in enumerate(fob.read()):
            if i == offset:
                return line, col

            if c == "\n":
                line += 1
                col = 0
            else:
                col += 1
    return None


def position_from_byte_offset(path: str, offset: int) -> Optional[tuple[int, int]]:
    line = 0
    col = 0
    with open(path, "rb") as fob:
        for i, c in enumerate(fob.read()):
            if i == offset:
                return line, col

            if c == b"\n":
                line += 1
                col = 0
            else:
                col += 1
    return None
