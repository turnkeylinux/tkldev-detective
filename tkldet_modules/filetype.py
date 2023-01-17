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
from libtkldet.classifier import FileClassifier, FileItem, register_classifier
from os.path import splitext, isfile


@register_classifier
class FiletypeClassifier(FileClassifier):
    WEIGHT = 10

    def classify(self, item: FileItem):
        if isfile(item.abspath) and "." in item.value:
            item.add_tags(self, [f"ext:{splitext(item.value)[1][1:]}"])
