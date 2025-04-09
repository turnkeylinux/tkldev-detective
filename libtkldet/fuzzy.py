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

"""Very basic fuzzy search"""

MAX_DIFF = 3
"words that differ more than MAX_DIFF will not be suggested"


def fuzzy_diff(x: str, y: str) -> int:
    """
    Calculate difference between two strings

    Return value has no objective meaning, only for comparison
    """
    diff = 0
    for i in range(max(len(x), len(y))):
        if len(x) <= i or len(y) <= i:
            diff += 1
        else:
            diff += x[i] != y[i]
    return diff


def fuzzy_suggest(
    check: str, options: list[str], max_diff: int = MAX_DIFF
) -> str | None:
    """
    Suggest a string from given options

    Given a 'check' value, and a list of valid options, find the option
    closest to the 'check' value, given that it's 'difference' (calculated by
    'fuzzy_diff' is less than or equal to max_diff
    """
    weighted_options = [(word, fuzzy_diff(check, word)) for word in options]
    weighted_options = sorted(weighted_options, key=lambda x: x[1])
    if weighted_options[0][1] > max_diff:
        return None
    return weighted_options[0][0]
