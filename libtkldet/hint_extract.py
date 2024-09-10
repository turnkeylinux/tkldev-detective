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

"""Utilities for annotating parts of files"""

from . import colors as co

H_PAD = 6  # padding (for hint lines to account for line numbers)


def extract_line(path: str, row: int) -> str:
    """Extract a single line from a file"""
    with open(path, "r") as fob:
        for i, line in enumerate(fob):
            if i == row:
                return (
                    str(i + 1).rjust(4)
                    + ": "
                    + co.GREEN
                    + line.rstrip()
                    + co.RESET
                )
    return "<COULD NOT FIND LINE>"


def extract_line_col(path: str, row: int, col: int) -> list[str]:
    """Annotate line with specific column"""
    return [
        extract_line(path, row),
        co.RED + "^".rjust(col + H_PAD + 1) + co.RESET,
    ]


def extract_line_cols(
    path: str, row: int, col_span: tuple[int, int]
) -> list[str]:
    """Annotate line with span of columns"""
    min_col, max_col = col_span
    return [
        extract_line(path, row),
        co.RED
        + "^".rjust(min_col + H_PAD)
        + "-" * (max_col - min_col - 1)
        + "^"
        + co.RESET,
    ]


def extract_lines(path: str, row_span: tuple[int, int]) -> list[str]:
    """Extract a multiple lines from a file"""
    min_row, max_row = row_span
    out = []
    with open(path, "r") as fob:
        for i, line in enumerate(fob):
            if i in (min_row, max_row):
                out.append(
                    co.RED
                    + "> "
                    + str(i + 1).rjust(4)
                    + ":"
                    + co.GREEN
                    + line.rstrip()
                    + co.RESET
                )
            elif min_row < i < max_row:
                out.append(
                    co.RED
                    + "| "
                    + str(i + 1).rjust(4)
                    + ":"
                    + co.GREEN
                    + line.rstrip()
                    + co.RESET
                )
    return out


def extract_lines_cols(
    path: str, row_span: tuple[int, int], col_span: tuple[int, int]
) -> list[str]:
    """Extract a span of characters in a file over multiple lines"""
    min_row, max_row = row_span
    min_col, max_col = col_span
    out = []
    with open(path, "r") as fob:
        for i, line in enumerate(fob):
            if min_row <= i <= max_row:
                out.append(
                    str(i + 1).rjust(4)
                    + ":"
                    + co.GREEN
                    + line.rstrip()
                    + co.RESET
                )
            if i == min_row:
                out.append(co.RED + "^".rjust(min_col + H_PAD) + co.RESET)
            elif i > min_row:
                if i == max_row:
                    out.append(
                        co.RED
                        + "+".rjust(min_col + H_PAD)
                        + "-" * (max_col - min_col - 1)
                        + "^"
                        + co.RESET
                    )
                else:
                    out.append(co.RED + "|".rjust(min_col + H_PAD) + co.RESET)
    return out


def format_extract(
    path: str,
    row_span: tuple[int, int] | int,
    col_span: tuple[int, int] | int | None,
) -> list[str]:
    """Annotate segment of file

    Given a row or span of rows and optionally a column or span of columns
    return an annotated segment of the specified file
    """

    if isinstance(row_span, tuple) and row_span[0] == row_span[1]:
        row_span = row_span[0]
    if isinstance(col_span, tuple) and col_span[0] == col_span[1]:
        col_span = col_span[0]

    if isinstance(row_span, int):
        row_span -= 1
        if col_span is None:
            return [extract_line(path, row_span)]
        if isinstance(col_span, int):
            return extract_line_col(path, row_span, col_span)
        if isinstance(col_span, tuple):
            return extract_line_cols(path, row_span, col_span)
    else:  # tuple
        row_span = (row_span[0] - 1, row_span[1] - 1)
        if col_span is None:
            return extract_lines(path, row_span)
        if isinstance(col_span, tuple):
            return extract_lines_cols(path, row_span, col_span)
        if isinstance(col_span, int):
            return extract_lines(path, row_span)
    print(row_span, col_span)
    error_message = "some combination of 0/1/more rows/cols is not supported!"
    raise NotImplementedError(error_message)
