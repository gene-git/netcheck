#!/usr/bin/python
'''
Plot netcheck results
'''
# pylint: disable=invalid-name
from lib import Plot


def main():
    """
    Run test
    """
    nplot = Plot()
    nplot.do_plot()


if __name__ == '__main__':
    main()
