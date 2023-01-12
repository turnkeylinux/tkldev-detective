import json
from typing import Generator
import subprocess

from libtklint.linter import FileLinter, FileItem, register_linter
from libtklint.report import Report, parse_report_level


@register_linter
class Shellcheck(FileLinter):
    ENABLE_TAGS: set[str] = {
        "ext:sh",
        "ext:bash",
        "shebang:/bin/sh",
        "shebang:/bin/bash",
    }
    DISABLE_TAGS: set[str] = set()

    def check(self, item: FileItem) -> Generator[Report, None, None]:
        for report in json.loads(
            subprocess.run(
                ["shellcheck", item.abspath, "-f", "json"],
                capture_output=True,
                text=True,
            ).stdout
        ):

            yield Report(
                item,
                line=(report["line"], report["endLine"]),
                column=(report["column"], report["endColumn"]),
                location_metadata="",
                message="[{}] {}".format(
                    report["code"],
                    report["message"],
                ),
                fix=report["fix"],
                source="shellcheck",
                level=parse_report_level(report["level"]),
            )
