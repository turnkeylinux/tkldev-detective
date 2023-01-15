from typing import Generator

from libtkldet.classifier import ExactPathClassifier, register_classifier
from libtkldet.linter import FileLinter, register_linter, FileItem
from libtkldet.report import Report, ReportLevel


@register_classifier
class ApplianceMakefileClassifier(ExactPathClassifier):
    path: str = 'Makefile'
    tags: list[str] = ['appliance-makefile']


@register_linter
class ApplianceMakefileLinter(FileLinter):
    ENABLE_TAGS: set[str] = { "appliance-makefile" }
    DISABLE_TAGS: set[str] = set()

    def check(self, item: FileItem) -> Generator[Report, None, None]:
        MK_CONFVARS = ['COMMON_CONFS', 'COMMON_OVERLAYS']
        with open('/turnkey/fab/common/mk/turnkey.mk', 'r') as fob:
            for line in fob:
                if line.startswith('CONF_VARS += '):
                    MK_CONFVARS.extend(line.strip().split()[2:])

        in_define = False
        first_include = None

        with open(item.abspath, 'r') as fob:
            for i, line in enumerate(fob):
                if in_define:
                    if line.startswith("endef"):
                        in_define = False
                    continue
                elif line.startswith('define'):
                    in_define = True
                    continue
                elif line.startswith('include'):
                    first_include = i
                    continue
                elif '=' in line:
                    var = line.split('=')[0].strip()
                    if not var in MK_CONFVARS:
                        yield Report(
                            item,
                            line = i+1,
                            column = (0, len(var)-1),
                            location_metadata = None,
                            message = "variable set is not a known CONF_VAR",
                            fix = "either replace with one of {} or add it to"
                            "turnkey.mk's list of valid CONF_VARS",
                            source = 'appliance-makefile-linter',
                            level = ReportLevel.WARN)

                    if first_include:
                        yield Report(
                            item,
                            line = i+1,
                            column = line.find('='),
                            location_metadata = None,
                            message = "variable defined AFTER includes",
                            fix = "move variable definitions to top of Makefile",
                            source = 'appliance-makefile-linter',
                            level = ReportLevel.WARN)




