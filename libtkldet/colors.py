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

"""just contains ansi escape codes for various color/term effects"""

_COLORS = [
    "BLACK",
    "RED",
    "GREEN",
    "YELLOW",
    "BLUE",
    "MAGENTA",
    "CYAN",
    "WHITE",
    "BRIGHT_BLACK",
    "BRIGHT_RED",
    "BRIGHT_GREEN",
    "BRIGHT_YELLOW",
    "BRIGHT_BLUE",
    "BRIGHT_MAGENTA",
    "BRIGHT_CYAN",
    "BRIGHT_WHITE",
    "BOLD",
    "RESET",
]

_COLOR_ASCII_CODES = {
    "BLACK": "\x1b[30m",
    "RED": "\x1b[31m",
    "GREEN": "\x1b[32m",
    "YELLOW": "\x1b[33m",
    "BLUE": "\x1b[34m",
    "MAGENTA": "\x1b[35m",
    "CYAN": "\x1b[36m",
    "WHITE": "\x1b[37m",
    "BRIGHT_BLACK": "\x1b[90m",
    "BRIGHT_RED": "\x1b[91m",
    "BRIGHT_GREEN": "\x1b[92m",
    "BRIGHT_YELLOW": "\x1b[93m",
    "BRIGHT_BLUE": "\x1b[94m",
    "BRIGHT_MAGENTA": "\x1b[95m",
    "BRIGHT_CYAN": "\x1b[96m",
    "BRIGHT_WHITE": "\x1b[97m",
    "RESET": "\x1b[0m",
    "BOLD": "\x1b[1m",
}

_COLOR_GLOBALS = globals()

BLACK: str
RED: str
GREEN: str
YELLOW: str
BLUE: str
MAGENTA: str
CYAN: str
WHITE: str
BRIGHT_BLACK: str
BRIGHT_RED: str
BRIGHT_GREEN: str
BRIGHT_YELLOW: str
BRIGHT_BLUE: str
BRIGHT_MAGENTA: str
BRIGHT_CYAN: str
BRIGHT_WHITE: str
RESET: str
BOLD: str


def set_colors_enabled(enabled: bool) -> None:
    """
    Set color globals to ANSI color codes

    If not enabled,  sets them to empty strings
    """
    for color in _COLORS:
        if enabled:
            _COLOR_GLOBALS[color] = _COLOR_ASCII_CODES[color]
        else:
            _COLOR_GLOBALS[color] = ""
