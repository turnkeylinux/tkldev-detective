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

from os.path import join, normpath, basename, isdir
from glob import iglob

from typing import Generator

from .error import ApplianceNotFound
from .classifier import FileItem

PRODUCTS_DIR = "/turnkey/fab/products"


def is_appliance_path(path: str):
    """ is path, a path to an appliance? """
    path = normpath(path)
    if path == join(PRODUCTS_DIR, basename(path)):
        return True
    return False


def is_appliance_name(name: str):
    """ is name, the name of an existing appliance on tkldev? """
    return "/" not in name and isdir(join(PRODUCTS_DIR, name))


def is_inside_appliance(path: str):
    """ is path, a path to a file inside an appliance """
    path = normpath(path)
    if not path.startswith(PRODUCTS_DIR + "/"):
        return False
    path = path[len(PRODUCTS_DIR) + 1 :]
    return bool(path)  # if path is non-zero length, it must be a path into an appliance

def get_appliance_root(path: str) -> str:
    '''Given a path to appliance, file inside appliance or appliance name,
    return absolute path to the appliance'''
    if is_appliance_name(path):
        return join(PRODUCTS_DIR, path)
    elif is_appliance_path(path):
        return normpath(path)
    elif is_inside_appliance(path):
        path = path[len(PRODUCTS_DIR)+1:]
        appliance_name = path.split('/', 1)[0]
        return join(PRODUCTS_DIR, appliance_name)
    else:
        raise ApplianceNotFound(
            "input does not appear to be an appliance name, path to an appliance or path to a file inside of an appliance"
        )

def locator(root: str) -> Generator[str, None, None]:
    """yields (pretty much) every file in an appliance of potential concern
    or a specific file only if given a path to a file inside an appliance"""
    if is_appliance_name(root):
        yield from full_appliance_locator(join(PRODUCTS_DIR, root))
    elif is_appliance_path(root):
        yield from full_appliance_locator(root)
    elif is_inside_appliance(root):
        yield root
    else:
        raise ApplianceNotFound(
            "input does not appear to be an appliance name, path to an appliance or path to a file inside of an appliance"
        )


def full_appliance_locator(root: str) -> Generator[str, None, None]:
    """yields (pretty much) every file in an appliance of potential concern"""
    yield from map(
        lambda x: join(root, x), ["Makefile", "changelog", "README.rst", "removelist"]
    )
    yield from iglob(join(root, "conf.d/*"))
    yield from iglob(join(root, "plan/*"))
    yield from iglob(join(root, "overlay/**"), recursive=True)

