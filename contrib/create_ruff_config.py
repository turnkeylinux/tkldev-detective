"""
This file creates a ruff.toml file using the configuration found inside
tkldet_modules/ruff.py

Mostly to be used with ruff's formatter
"""

import json
from os.path import abspath, dirname, join
import sys

PROJECT_PATH = dirname(dirname(abspath(__file__)))
TKLDET_MODULE_PATH = join(PROJECT_PATH, "tkldet_modules")

sys.path.insert(0, PROJECT_PATH)
sys.path.insert(1, TKLDET_MODULE_PATH)

import libtkldet
from libtkldet.report import ReportLevel
from ruff import RUFF_LINTS

# these rules cause issues with the formatter
incompatible = ["ISC001", "D203"]

output = """

line-length = 79
indent-width = 4

target-version = "py311"

[lint]
"""

select = []
ignore = [*incompatible]

for group, lints in RUFF_LINTS.items():
    for lint, level in lints.items():
        if level is not None and lint not in incompatible:
            select.append(lint)
        else:
            ignore.append(lint)

output += "select = " + json.dumps(select, indent=4) + "\n"
output += "ignore = " + json.dumps(ignore, indent=4) + "\n"

print(output)
