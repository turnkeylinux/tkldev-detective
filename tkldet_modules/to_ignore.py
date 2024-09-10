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
"""For marking files which should be ignored"""

from libtkldet.classifier import FileClassifier, FileItem, register_classifier
import os.path
from typing import ClassVar


def is_or_has_ancestor_dir(path: str, directory: str) -> bool:
    """Checks if path has an ancestor directory with a given name"""
    while path not in ("/", ""):
        path, path_segment = os.path.split(path)
        if path_segment == directory:
            return True
    return False


@register_classifier
class FiletypeClassifier(FileClassifier):
    """Classify files by a parent directory"""

    WEIGHT: ClassVar[int] = 5

    def classify(self, item: FileItem) -> None:
        if is_or_has_ancestor_dir(item.abspath, "__pycache__"):
            item.add_tags(self, ["ignore:__pycache__"])
        if is_or_has_ancestor_dir(item.abspath, ".git"):
            item.add_tags(self, ["ignore:.git"])
