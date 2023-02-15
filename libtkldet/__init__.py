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

from typing import Generator
from os.path import relpath, abspath
from . import locator, common_data, classifier
from .common_data import APPLIANCE_ROOT


def initialize(path: str):
    """initialize everything, involves scraping makefiles, parsing plans, etc."""
    root = locator.get_appliance_root(path)
    common_data.initialize_common_data(root)


def yield_appliance_items() -> Generator[classifier.Item, None, None]:
    '''generator that yields everything "lintable"'''

    yield from common_data.iter_packages()
    for path in locator.locator(APPLIANCE_ROOT):
        yield classifier.FileItem(
            value=path,
            _tags={},
            relpath=relpath(path, start=APPLIANCE_ROOT),
            abspath=abspath(path),
        )
