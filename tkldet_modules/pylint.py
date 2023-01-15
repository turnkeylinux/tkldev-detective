import json
from typing import Generator
import subprocess

from libtkldet.linter import FileLinter, FileItem, register_linter
from libtkldet.report import Report, parse_report_level


@register_linter
class PyLinter(FileLinter):
    ENABLE_TAGS: set[str] = {
        "ext:py",
        "shebang:/usr/bin/python",
        "shebang:/usr/bin/python3",
        "shebang:/usr/bin/python3.9",
    }
    DISABLE_TAGS: set[str] = set()

    def check(self, item: FileItem) -> Generator[Report, None, None]:
        for report in json.loads(
            subprocess.run(
                ["pylint", item.abspath, "-f", "json"], capture_output=True, text=True
            ).stdout
        ):

            if report["obj"]:
                location_metadata = f'{report["obj"]} in module {report["module"]}'
            else:
                location_metadata = f'in base of module {report["module"]}'

            yield Report(
                item,
                line=report["line"],
                column=report["column"],
                location_metadata=location_metadata,
                message="[{} | {}] {}".format(
                    report["message-id"],
                    report["symbol"],
                    report["message"],
                ),
                fix=None,
                source="pylint",
                level=parse_report_level(report["type"]),
            )
