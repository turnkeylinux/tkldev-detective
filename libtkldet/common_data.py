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

from os.path import join
from .plan_resolve import parse_plan, PlanEntry
from .locator import iter_plan
from .classifier import PackageItem
from typing import Generator

APPLIANCE_ROOT: str = ''
_plan_resolve_cache: list[PlanEntry] = []
_included_plan_cache: set[str] = set()

def initialize_common_data(appliance_root: str):
    global APPLIANCE_ROOT, _plan_resolve_cache, _included_plan_cache
    APPLIANCE_ROOT = appliance_root

    for plan_path in iter_plan(appliance_root):
        entries = parse_plan(plan_path)

        _plan_resolve_cache.extend(entries)

        for entry in entries:
            _included_plan_cache.update(entry.include_stack)

def is_package_to_be_installed(package_name: str) -> bool:
    for entry in _plan_resolve_cache:
        if entry.package_name == package_name:
            return True
    return False

def is_common_plan_included(plan_name: str) -> bool:
    return join('/turnkey/fab/common/plans', plan_name) in _included_plan_cache

def iter_packages() -> Generator[PackageItem, None, None]:
    for entry in _plan_resolve_cache:
        yield PackageItem(
            value=entry.package_name,
            _tags={},
            plan_stack=entry.include_stack[:]
        )
