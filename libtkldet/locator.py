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

"""locates files to be classified and eventually linted"""

from os.path import join
from glob import iglob

from typing import Generator


def locator(root: str) -> Generator[str, None, None]:
    """yields (pretty much) every file in an appliance of potential concern"""
    yield from map(
        lambda x: join(root, x), ["Makefile", "changelog", "README.rst", "removelist"]
    )
    yield from iglob(join(root, "conf.d/*"))
    yield from iglob(join(root, "plan/*"))
    yield from iglob(join(root, "overlay/**"), recursive=True)
