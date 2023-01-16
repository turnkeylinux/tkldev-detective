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
from libtkldet.classifier import ExactPathClassifier, SubdirClassifier, register_classifier

@register_classifier
class ApplianceMakefileClassifier(ExactPathClassifier):
    path: str = 'Makefile'
    tags: list[str] = ['appliance-makefile']

@register_classifier
class ApplianceConfDClassifier(SubdirClassifier):
    path: str = 'conf.d'
    recursive: bool = False
    tags: list[str] = ['appliance-conf.d']

@register_classifier
class ApplianceOverlayClassifier(SubdirClassifier):
    path: str = 'overlay'
    recursive: bool = True
    tags: list[str] = ['appliance-overlay']

@register_classifier
class AppliancePlanClassifier(SubdirClassifier):
    path: str = 'plan'
    recursive: bool = False
    tags: list[str] = ['appliance-plan']

@register_classifier
class ApplianceInithookFirstbootClassifier(SubdirClassifier):
    path: str = 'overlay/usr/lib/inithooks/firstboot.d'
    recursive: bool = False
    tags: list[str] = ['appliance-inithook-firstboot']

@register_classifier
class ApplianceInithookBinClassifier(SubdirClassifier):
    path: str = 'overlay/usr/lib/inithooks/bin'
    recursive: bool = False
    tags: list[str] = ['appliance-inithook-bin']

@register_classifier
class ApplianceReadmeClassifier(ExactPathClassifier):
    path: str = 'README.rst'
    tags: list[str] = ['appliance-readme']

@register_classifier
class ApplianceChangelogClassifier(ExactPathClassifier):
    path: str = 'changelog'
    tags: list[str] = ['appliance-readme']
