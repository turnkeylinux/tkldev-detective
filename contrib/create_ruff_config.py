#!/usr/bin/env python3

"""
Create a ruff config file from tkldet_modules/ruff.py

Mostly to be used with ruff's formatter
"""

import subprocess
import json
import sys
from os.path import abspath, dirname, join

PROJECT_PATH = dirname(dirname(abspath(__file__)))
TKLDET_MODULE_PATH = join(PROJECT_PATH, "tkldet_modules")

sys.path.insert(0, PROJECT_PATH)
sys.path.insert(1, TKLDET_MODULE_PATH)

from ruff import RUFF_LINTS

known_ruff_lints = json.loads(subprocess.run(['ruff', 'rule', '--all', '--output-format', 'json'],
               capture_output=True).stdout)
known_ruff_lints = { rule['code'] for rule in known_ruff_lints }

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

found = set()

for lints in RUFF_LINTS.values():
    for lint, level in lints.items():
        if lint in known_ruff_lints:
            found.add(lint)

        if level is not None and lint not in incompatible:
            select.append(lint)
        else:
            ignore.append(lint)

output += "select = " + json.dumps(select, indent=4) + "\n"
output += "ignore = " + json.dumps(ignore, indent=4) + "\n"

print(output)

missing = known_ruff_lints-found
if missing:
    sys.stderr.write(f'missing {missing}\n')
