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
Encapsulates "Classifier"s & the "Item"s they operate on

code here provides ability to "classify" different files
"""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from os.path import dirname
from typing import ClassVar, cast


@dataclass(frozen=True)
class Item:
    """
    Some "thing" which can be classified

    tags are used to classify items,
    value is dependant on type of "thing"
    """

    __slots__ = ["value", "_tags"]

    value: str
    """context dependant value, either the thing being classified itself or
    information on how to acccess it (such as a path)"""

    _tags: dict[str, set[str]]
    """maps classifiers to tags, so if necessary it can be determined
    exactly how an item got classsified in a certain way """

    @property
    def tags(self) -> Iterator[str]:
        """Yields all tags, may contain duplicates"""
        for tags in self._tags.values():
            yield from tags

    def add_tags(self, classifier: "Classifier", tags: Iterable[str]) -> None:
        """Add tags to an item"""
        name = classifier.__class__.__name__
        if name not in self._tags:
            self._tags[name] = set()
        self._tags[name].update(tags)

    def has_tag(self, tag: str) -> bool:
        """Check if item contains a given tag"""
        return tag in self.tags

    def has_tag_type(self, tag_type: str) -> bool:
        """Check if item contains a variant tag of a given type"""
        check = tag_type + ":"
        return any(tag.startswith(check) for tag in self.tags)

    def tags_with_type(self, tag_type: str) -> Iterator[str]:
        """Return all tags with a variant tag of a given type"""
        check = tag_type + ":"
        return filter(lambda tag: tag.startswith(check), self.tags)

    def pretty_print(self) -> None:
        """Show item value as well as tags"""
        print(f"{self.value}")
        for src in self._tags:
            print("\t", src, self._tags[src])


@dataclass(frozen=True)
class FileItem(Item):
    """
    Specifically files which can be classified

    value is the raw path found by the locator
    """

    __slots__ = ["relpath", "abspath"]

    relpath: str
    """path relative to the appliance root, use this when inspecting the
    path itself"""

    abspath: str
    """absolute path to file, use this when inspecting the file the path points
    to"""


@dataclass(frozen=True)
class PackageItem(Item):
    """
    Specifically packages installed via plan which can be classied

    value is the package name
    """

    __slots__ = ["plan_stack"]

    plan_stack: list[str]
    """a list of paths, in order from the "base" plan (appliance-specific) all
    the way to the exact plan that included this package. Note this will only
    contain 1 value if a package was included in the appliance specific plan"""


class Classifier:
    """
    Classifier base class

    All registered classifiers are called with each item yielded by the
    locator.

    the tags determined by the classifiers determine which linters are run on
    which files.
    """

    WEIGHT: ClassVar[int] = 100
    """weight is used to order classifiers, as tthey can read tags as well,
    classifier can leverage information provided (or omitted) by previous
    classifiers"""

    ItemType: ClassVar[type[Item]] = Item

    def do_classify(self, item: Item) -> None:
        """
        Perform classification

        Perform a classification so long as the concrete item type
        is compatible with this classifier
        """
        if isinstance(item, self.ItemType):
            self.classify(item)

    def classify(self, item: Item) -> None:
        """Classify exact item type"""
        raise NotImplementedError


class FileClassifier(Classifier):
    """Specialized classifer which operates on "FileItem"s"""

    ItemType: ClassVar[type[Item]] = FileItem


class PackageClassifier(Classifier):
    """Specialized classifier which operates on "PackageItem"s"""

    ItemType: ClassVar[type[Item]] = PackageItem


class ExactPathClassifier(FileClassifier):
    """Classifies an item which matches some exact path"""

    path: ClassVar[str]
    "exact path to match"

    tags: ClassVar[list[str]]
    "exact tags to add to matched item"

    def classify(self, item: Item) -> None:
        item = cast(FileItem, item)
        # item will definitely be subclass of
        # cls.ItemType, just need to convince the type checker

        if item.relpath == self.path:
            item.add_tags(self, self.tags[:])


class SubdirClassifier(FileClassifier):
    """Classifies an item which is inside a given subdirectory"""

    path: ClassVar[str]
    "the parent directory"

    recursive: ClassVar[bool]
    """whether to match a child of any depth or only files directly inside
    the given dir"""

    tags: ClassVar[list[str]]
    "exact tags to add to matched item"

    def classify(self, item: Item) -> None:
        item = cast(FileItem, item)
        # item will definitely be subclass of
        # cls.ItemType, just need to convince the type checker

        if self.recursive:
            if item.relpath.startswith(self.path):
                # XXX doesn't handle any `..` in path, hopefully doesn't matter
                item.add_tags(self, self.tags[:])
        elif dirname(item.relpath) == self.path:
            item.add_tags(self, self.tags[:])


_CLASSIFIERS: list[type[Classifier]] = []


def register_classifier(classifier: type[Classifier]) -> type[Classifier]:
    """
    Register a classifier

    This must be called on classifiers added
    """
    _CLASSIFIERS.append(classifier)
    return classifier


def get_weighted_classifiers() -> list[Classifier]:
    """Return instances of registered classifiers in order of weight"""
    return sorted(
        (c() for c in _CLASSIFIERS),
        key=lambda x: (x.WEIGHT, x.__class__.__name__),
    )
