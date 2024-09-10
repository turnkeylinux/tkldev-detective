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

"""locates files to be classified and eventually linted"""

from os.path import join, normpath, basename, isdir, isfile
from glob import iglob

from typing import Iterator

from .error import ApplianceNotFoundError

from logging import getLogger

PRODUCTS_DIR = "/turnkey/fab/products"

logger = getLogger(__name__)


def is_appliance_path(path: str) -> bool:
    """is path, a path to an appliance?"""
    path = normpath(path)
    if path == join(PRODUCTS_DIR, basename(path)):
        return isfile(join(path, "Makefile"))
    return False


def is_appliance_name(name: str) -> bool:
    """is name, the name of an existing appliance on tkldev?"""
    return name != "." and "/" not in name and isdir(join(PRODUCTS_DIR, name))


def is_inside_appliance(path: str) -> bool:
    """is path, a path to a file inside an appliance"""
    path = normpath(path)
    if not path.startswith(PRODUCTS_DIR + "/"):
        return False
    path = path[len(PRODUCTS_DIR) + 1 :]
    return bool(
        path
    )  # if path is non-zero length, it must be a path into an appliance


def get_appliance_root(path: str) -> str:
    """Get appliance root from path

    Given a path to appliance, file inside appliance or appliance name,
    return absolute path to the appliance
    """

    root: str | None = None

    if is_appliance_name(path):
        root = join(PRODUCTS_DIR, path)
    elif is_appliance_path(path):
        root = normpath(path)
    elif is_inside_appliance(path):
        path = path[len(PRODUCTS_DIR) + 1 :]
        appliance_name = path.split("/", 1)[0]
        root = join(PRODUCTS_DIR, appliance_name)

    if root is None or not isfile(join(root, "Makefile")):
        logger.info("lint root is not an appliance")
        error_message = (
            "input does not appear to be an appliance name, path to an appliance"
            " or path to a file inside of an appliance"
        )
        raise ApplianceNotFoundError(error_message)
    return root


def locator(root: str, ignore_non_appliance: bool) -> Iterator[str]:
    """Yield most files inside appliance

    Yields almost every file in an appliance of potential concern
    or a specific file only if given a path to a file inside an appliance
    """
    if is_appliance_name(root):
        logger.debug("locator(_) # is appliance name")
        yield from full_appliance_locator(join(PRODUCTS_DIR, root))
    elif is_appliance_path(root):
        logger.debug("locator(_) # is appliance path")
        yield from full_appliance_locator(root)
    elif is_inside_appliance(root):
        logger.debug("locator(_) # is inside appliance")
        yield from full_appliance_locator(get_appliance_root(root))
    elif ignore_non_appliance:
        logger.debug(
            "locator(_) # is not an appliance (but ignore_non_appliance set)"
        )
        yield from everything_locator(root)
    else:
        error_message = (
            "input does not appear to be an appliance name, path to an"
            " appliance or path to a file inside of an appliance"
        )
        raise ApplianceNotFoundError(error_message)


def everything_locator(root: str) -> Iterator[str]:
    """Yield everything, appliance or not"""
    if isfile(root):
        yield root
    else:
        yield from iglob(join(root, "**"), recursive=True, include_hidden=True)


def full_appliance_locator(root: str) -> Iterator[str]:
    """Yield (pretty much) every file in an appliance of potential concern"""
    yield from (
        join(root, x)
        for x in ["Makefile", "changelog", "README.rst", "removelist"]
    )
    yield from iter_conf(root)
    yield from iter_plan(root)
    yield from iter_overlay(root)


def iter_conf(root: str) -> Iterator[str]:
    """yield each conf file in the appliance"""
    yield from iglob(join(root, "conf.d/*"))


def iter_plan(root: str) -> Iterator[str]:
    """yield each plan file in the appliance"""
    yield from iglob(join(root, "plan/*"))


def iter_overlay(root: str) -> Iterator[str]:
    """yield each file in the appliance overlay"""
    yield from iglob(join(root, "overlay/**"), recursive=True)
