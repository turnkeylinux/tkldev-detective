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

from typing import ClassVar, Iterator

from .classifier import Item, FileItem
from .report import Report


class Linter:
    """Base class for linters

    by default linters automatically enable/disable based on `ENABLE_TAGS` and
    `DISABLE_TAGS`
    """

    ENABLE_TAGS: ClassVar[set[str]]
    "tags which this linter should work on (or all if omitted)"
    DISABLE_TAGS: ClassVar[set[str]]
    "tags which this linter should never work on"

    WEIGHT: ClassVar[int] = 100

    ItemType: ClassVar[type[Item]] = Item

    def should_check(self, item: Item) -> bool:
        """Actually performs check to see if the linter should run on this item

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

    def do_check(self, item: Item) -> Iterator[Report] | None:
        """Run lint, if `should_check` returns True, used internally"""
        if isinstance(item, self.ItemType) and self.should_check(item):
            return self.check(item)
        return None

    def check(self, item: Item) -> Iterator[Report]:
        """Actually run lint"""
        raise NotImplementedError


class FileLinter(Linter):
    """Specific linter that operates only on FileItems"""

    ItemType: type[Item] = FileItem

    def check(self, item: Item) -> Iterator[Report]:
        raise NotImplementedError


_LINTERS: list[type[Linter]] = []


def register_linter(linter: type[Linter]) -> type[Linter]:
    """Register a linter

    Must be called on all linters added
    """
    _LINTERS.append(linter)
    return linter


def get_weighted_linters() -> list[Linter]:
    """Return instances of registered classifiers in order of weight"""
    return sorted(
        (x() for x in _LINTERS), key=lambda x: (x.WEIGHT, x.__class__.__name__)
    )
