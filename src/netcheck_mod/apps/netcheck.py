#!/usr/bin/python
# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2025-present Gene C <arch@sapience.com>
'''
 Check network staus using ping
   - Savs results to file(s)

 Sample use:
    netcheck -d <dir> -n 100 1.1.1.1 8.8.8.8
'''
import asyncio
from netcheck_mod.lib import NetCheck


async def main():
    """
    Run test
    """
    ncheck = NetCheck()
    await ncheck.check()
    ncheck.reports()


if __name__ == '__main__':
    asyncio.run(main())
