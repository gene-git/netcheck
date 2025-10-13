# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2022-present  Gene C <arch@sapience.com>
"""
Project netcheck
"""

__version__ = "1.9.1"
__date__ = "2025-10-13"
__reldev__ = "release"


def version() -> str:
    """ report version and release date """
    vers = f'netcheck: version {__version__} ({__date__}'
    return vers
