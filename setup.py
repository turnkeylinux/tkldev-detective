#!/usr/bin/env python3

from distutils.core import setup

setup(
    name="tkldev-detective",
    version="1.0",
    author="Stefan Davis",
    author_email="stefan@turnkeylinux.org",
    url="https://github.com/turnkeylinux/tkldev-detective",
    packages=["libtkldet"],
    scripts=["tkldev-detective"],
)
