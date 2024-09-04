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
"""Classifiers for appliance specific files"""

from libtkldet.classifier import (
    ExactPathClassifier,
    SubdirClassifier,
    register_classifier,
)
from typing import ClassVar

@register_classifier
class ApplianceMakefileClassifier(ExactPathClassifier):
    """Classifies appliance Makefile"""

    path: ClassVar[str] = "Makefile"
    tags: ClassVar[list[str]] = ["appliance-makefile"]


@register_classifier
class ApplianceConfDClassifier(SubdirClassifier):
    """Classifies appliance conf.d scripts"""

    path: ClassVar[str] = "conf.d"
    recursive: ClassVar[bool] = False
    tags: ClassVar[list[str]] = ["appliance-conf.d"]


@register_classifier
class ApplianceOverlayClassifier(SubdirClassifier):
    """Classifies appliance overlay files"""

    path: ClassVar[str] = "overlay"
    recursive: ClassVar[bool] = True
    tags: ClassVar[list[str]] = ["appliance-overlay"]


@register_classifier
class AppliancePlanClassifier(SubdirClassifier):
    """Classifies appliance plans"""

    path: ClassVar[str] = "plan"
    recursive: ClassVar[bool] = False
    tags: ClassVar[list[str]] = ["appliance-plan"]


@register_classifier
class ApplianceInithookFirstbootClassifier(SubdirClassifier):
    """Classifies appliance firstboot inithooks"""

    path: ClassVar[str] = "overlay/usr/lib/inithooks/firstboot.d"
    recursive: ClassVar[bool] = False
    tags: ClassVar[list[str]] = ["appliance-inithook-firstboot"]


@register_classifier
class ApplianceInithookBinClassifier(SubdirClassifier):
    """Classifies appliance inithooks bin scripts"""

    path: ClassVar[str] = "overlay/usr/lib/inithooks/bin"
    recursive: ClassVar[bool] = False
    tags: ClassVar[list[str]] = ["appliance-inithook-bin"]


@register_classifier
class ApplianceReadmeClassifier(ExactPathClassifier):
    """Classifies appliance readme"""

    path: ClassVar[str] = "README.rst"
    tags: ClassVar[list[str]] = ["appliance-readme"]


@register_classifier
class ApplianceChangelogClassifier(ExactPathClassifier):
    """Classifies appliance changelog"""

    path: ClassVar[str] = "changelog"
    tags: ClassVar[list[str]] = ["appliance-readme"]
