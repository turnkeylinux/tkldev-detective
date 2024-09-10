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
"""General file classification"""

from libtkldet.classifier import FileClassifier, FileItem, register_classifier
from os.path import splitext, isfile
from typing import ClassVar
from logging import getLogger

logger = getLogger(__name__)

@register_classifier
class FiletypeClassifier(FileClassifier):
    """Classify files by extension"""

    WEIGHT: ClassVar[int] = 10

    def classify(self, item: FileItem) -> None:
        if isfile(item.abspath) and "." in item.value:
            item.add_tags(self, [f"ext:{splitext(item.value)[1][1:]}"])


@register_classifier
class ShebangClassifier(FileClassifier):
    """Classify files by shebang"""

    WEIGHT: ClassVar[int] = 10

    def classify(self, item: FileItem) -> None:
        if isfile(item.abspath):
            other_parts = []
            with open(item.abspath, "rb") as fob:
                shebang = b""
                head = fob.read(512)

                if b"\n" in head:
                    shebang = head.split(b"\n")[0].strip()
                    if shebang:
                        other_parts = shebang.split()
                        shebang = other_parts.pop(0)

            try:
                other_parts = [part.decode() for part in other_parts]
                shebang = shebang.decode().strip()
            except UnicodeDecodeError:
                logger.debug("failed to decode shebang", exc_info=True)
                item.add_tags(self, ['not-utf8'])
            else:
                if shebang.startswith("#!"):
                    if shebang == '#!/usr/bin/env':
                        item.add_tags(self, [
                            f"shebang:{shebang[2:]} {other_parts[0]}"
                        ])
                    else:
                        item.add_tags(self, [f"shebang:{shebang[2:]}"])
