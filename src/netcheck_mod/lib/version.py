# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2022-present Gene C <arch@sapience.com>
"""
Project netcheck
"""

__version__ = "1.10.0"
__date__ = "2026-01-04"
__reldev__ = "release"


def version() -> str:
    """ report version and release date """
    vers = f'netcheck: version {__version__} ({__date__}'
    return vers
