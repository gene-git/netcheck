#!/usr/bin/python
# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2025-present Gene C <arch@sapience.com>
'''
Plot netcheck results
'''
# pylint: disable=invalid-name
from netcheck_mod.lib import Plot


def main():
    """
    Run test
    """
    nplot = Plot()
    nplot.do_plot()


if __name__ == '__main__':
    main()
