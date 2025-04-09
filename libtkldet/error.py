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
    """Base class for tkldev-detective specific errors"""


class ApplianceNotFoundError(TKLDevDetectiveError):
    """
    Appliance was not found

    Likely path/app name was incorrect
    """


class PlanNotFoundError(TKLDevDetectiveError):
    """
    A plan could not be included

    Likely include name is incorrect
    """


class UnknownPlanDirectiveError(TKLDevDetectiveError):
    """Encountered some unexpected CPP directive in plan"""


class InvalidPlanError(TKLDevDetectiveError):
    """
    Plan appears to not be valid

    Mismatched #if* and #endif directives likely
    """
