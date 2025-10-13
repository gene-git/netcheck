#!/usr/bin/python
'''
 Check network staus using ping
   - Savs results to file(s)

 Sample use:
    netcheck -d <dir> -n 100 1.1.1.1 8.8.8.8
 ------------
  2018-12-12
 ------------
'''
import asyncio
from lib import NetCheck


async def main():
    """
    Run test
    """
    ncheck = NetCheck()
    await ncheck.check()
    ncheck.reports()

# -----------------------------------------------------
if __name__ == '__main__':
    asyncio.run(main())
