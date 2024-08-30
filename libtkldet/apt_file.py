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

"""relates to finding packages based on files they provide, including those not
installed"""

import subprocess

def is_in_path(name: str) -> bool:
    """check if a given name is in the path"""
    in_path = subprocess.run(
        ["which", name],
        capture_output=True
    )
    return in_path.returncode == 0

def is_installed(package_name: str) -> bool:
    """check if a given package is installed on the HOST system (tkldev)"""
    pkg_installed = subprocess.run(
        ["dpkg-query", "-W", "--showformat='${Status}'", package_name],
        capture_output=True
    )
    return pkg_installed.returncode != 0


HAS_APT_FILE: bool = is_installed("apt-file")


def find_package_by_file(path: str) -> list[str]:
    """return a list of packages that provide a file at a given path"""

    ret = subprocess.run(
        [
            "apt-file",
            "search",
            "--package-only",
            "-x",
            path,
        ],
        capture_output=True,
        text=True,
    )
    if ret.returncode != 0:
        return []
    return ret.stdout.strip().splitlines()


def find_python_package(package_name: str) -> list[str]:
    """return a list of packages that provide a given python module"""
    return find_package_by_file(
        f"/usr/lib/python3/dist-packages/{package_name}(\\.py)?"
    )


def find_python_package_from_import(module_str: str) -> list[str]:
    """return a list of packages that provide a given python import module, may
    be several modules deep (e.g. `foo.bar.baz`), attempts to find most
    specific python package provider
    """
    out = find_python_package(module_str.replace(".", "/"))
    while "." in module_str and not out:
        module_str = module_str.rsplit(".", 1)[0]
        out = find_python_package(module_str.replace(".", "/"))

    return out
