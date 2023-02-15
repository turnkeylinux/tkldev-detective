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
"""Utilities and data relating to ${FAB_PATH}/common"""

import os
from os.path import join, isfile
from typing import Generator, Optional
from .plan_resolve import parse_plan, PlanEntry
from .locator import iter_plan
from .classifier import PackageItem
from .mkparser import parse_makefile, CommonFabBuildData

APPLIANCE_ROOT: str = ""
_PLAN_RESOLVE_CACHE: list[PlanEntry] = []
_INCLUDED_PLAN_CACHE: set[str] = set()
_FAB_DATA: CommonFabBuildData


def initialize_common_data(appliance_root: str):
    """parse plan & makefile and initialize data which utilizes it"""
    global APPLIANCE_ROOT, _PLAN_RESOLVE_CACHE, _INCLUDED_PLAN_CACHE, _FAB_DATA
    APPLIANCE_ROOT = appliance_root

    for plan_path in iter_plan(appliance_root):
        entries = parse_plan(plan_path)

        _PLAN_RESOLVE_CACHE.extend(entries)

        for entry in entries:
            _INCLUDED_PLAN_CACHE.update(entry.include_stack)

    _FAB_DATA = parse_makefile(join(appliance_root, "Makefile")).to_fab_data()


def is_package_to_be_installed(package_name: str) -> bool:
    """check if an apt package will be installed via plan"""
    for entry in _PLAN_RESOLVE_CACHE:
        if entry.package_name == package_name:
            return True
    return False


def is_common_plan_included(plan_name: str) -> bool:
    """check if a common plan (by file name) is included in appliance build """
    return join("/turnkey/fab/common/plans", plan_name) in _INCLUDED_PLAN_CACHE


def iter_packages() -> Generator[PackageItem, None, None]:
    """ iterate over all packages which will be installed """
    for entry in _PLAN_RESOLVE_CACHE:
        yield PackageItem(
            value=entry.package_name, _tags={}, plan_stack=entry.include_stack[:]
        )


def get_common_overlays() -> list[str]:
    """ return a list of all common overlays included in this appliance """
    return _FAB_DATA.overlays[:]


def get_common_conf() -> list[str]:
    """ return a list of all common conf scripts included in this appliance """
    return _FAB_DATA.conf[:]


def get_common_removelists() -> list[str]:
    """ return a list of all common removelists included in this appliance """
    return _FAB_DATA.removelists[:]


def get_common_removelists_final() -> list[str]:
    """ return a list of all common final removelists included in this appliance """
    return _FAB_DATA.removelists_final[:]


def get_path_in_common_overlay(path: str) -> Optional[str]:
    """check if a given path (expressed as an absolute path, where it would be
    placed in a build)"""
    path = path.lstrip("/")
    for common in _FAB_DATA.overlays:
        common_path = join(
            os.getenv("FAB_PATH", "/turnkey/fab"), "common/overlays", common, path
        )
        if isfile(common_path):
            return common_path
    return None
