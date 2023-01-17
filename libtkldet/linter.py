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
Encapsulates "Linter"s

code here provides interface for modules to provide linting
"""
from typing import Generator, Type, Optional

from .classifier import Item, FileItem
from .report import Report


class Linter:
    """Base class for linters

    by default linters automatically enable/disable based on `ENABLE_TAGS` and
    `DISABLE_TAGS`
    """

    ENABLE_TAGS: set[str]
    "tags which this linter should work on (or all if omitted)"
    DISABLE_TAGS: set[str]
    "tags which this linter should never work on"

    WEIGHT: int = 100

    ItemType: Type[Item] = Item

    def should_check(self, item: Item) -> bool:
        """actually performs check to see if the linter should run on this item.

        if `ENABLE_TAGS` is empty, run lint on all items except those that have
        tags in `DISABLE_TAGS`

        if `ENABLE_TAGS` has tags, run lint only on items which have at least 1 tag
        from `ENABLE_TAGS` and non from `DISABLE_TAGS`

        (safe to override)
        """
        if not self.ENABLE_TAGS:
            for tag in self.DISABLE_TAGS:
                if tag in item.tags:
                    return False
        else:
            enabled = False
            for tag in self.ENABLE_TAGS:
                if tag in item.tags:
                    enabled = True
                    break
            for tag in self.DISABLE_TAGS:
                if tag in item.tags:
                    enabled = False
                    break
            if not enabled:
                return False
        return True

    def do_check(self, item: Item) -> Optional[Generator[Report, None, None]]:
        """runs lint, if `should_check` returns True, used internally"""
        if isinstance(item, self.ItemType) and self.should_check(item):
            return self.check(item)
        return None

    def check(self, item: Item) -> Generator[Report, None, None]:
        """abstract method, actually runs lint, to be implemented by subclass"""
        ...


class FileLinter(Linter):
    """ Specific linter that operates only on FileItems """

    ItemType: Type[Item] = FileItem

    def check(self, item: Item) -> Generator[Report, None, None]:
        ...


_LINTERS: list[Type[Linter]] = []


def register_linter(linter: Type[Linter]):
    """registers a linter for use in tkldev-detective, must be called on all
    linters added"""
    _LINTERS.append(linter)
    return linter


def get_weighted_linters() -> list[Linter]:
    """returnss instances of registered classifiers in order of weight"""
    return sorted(
        map(lambda x: x(), _LINTERS), key=lambda x: (x.WEIGHT, x.__class__.__name__)
    )
