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

from typing import Optional

MAX_DIFF = 3
'words that differ more than MAX_DIFF will not be suggested'

def fuzzy_diff(a: str, b: str) -> int:
    diff = 0
    for i in range(max(len(a), len(b))):
        if len(a) <= i or len(b) <= i:
            diff += 1
        else:
            diff += (a[i] != b[i])
    return diff

def fuzzy_suggest(check: str, options: list[str]) -> Optional[str]:
    weighted_options = [(word, fuzzy_diff(check, word)) for word in options]
    weighted_options = sorted(weighted_options, key=lambda x: x[1])
    if weighted_options[0][1] > MAX_DIFF:
        return None
    return weighted_options[0][0]
