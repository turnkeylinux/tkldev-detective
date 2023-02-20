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
"""used to hold custom errors/exceptions for internal use"""

class TKLDevDetectiveError(Exception):
    ...


class ApplianceNotFound(TKLDevDetectiveError):
    """appliance was not found for some reason (likely path/app name was
    incorrect)"""

    ...


class PlanNotFound(TKLDevDetectiveError):
    """a plan could not be included (likely include name is incorrect)"""

    ...


class UnknownPlanDirective(TKLDevDetectiveError):
    """encountered some unexpected cpp directive in plan"""

    ...


class InvalidPlan(TKLDevDetectiveError):
    """plan appears to not be valid (mismatched #if* and #endif directives
    likely)"""

    ...
