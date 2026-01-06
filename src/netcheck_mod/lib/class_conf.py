# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2025-present Gene C <arch@sapience.com>
"""
 Check network staus using ping and save results to file(s)
"""
# pylint: disable=too-few-public-methods,invalid-name
# pylint: disable=too-many-instance-attributes

from typing import Any
import argparse

type _Opt = tuple[str | tuple[str, ...], dict[str, Any]]


class Conf:
    """
     Command line inputs.

     Options:
       -a,--any = Report if any host has loss instead of all hosts (False)
       -b,--base = base name for output file ("<base>-<host>")  ("ncheck")
       -d,--dir = directory to save output  (None)
       -i,--interval = ping interval (0.25)
       -I,--Interface = use this interface/IP as source (see man ping)
       -n,--num = num pings (100)
       -t,--test  = test mode generate fake lost packets (False)
       -v,--verb = more verbose output

        host[,host2,...]

        Output:
            Stdout for basic report

            if -d then output files saved there


        Typical usage:
            pingcheck -n 100 1.1.1.1,8.8.8.8
          or
            pingcheck -n 100 -d "results-dir" 1.1.1.1,8.8.8.8
    """
    def __init__(self):
        self.test = False

        # ping options
        self.hosts: list[str] = []
        self.num: int = 100
        self.interval: str = ''
        self.Interface: str = ''
        self.ip4_only: bool = False
        self.ip6_only: bool = False

        self.any = False
        self.verb = False

        self.dir: str = ''
        self.base: str = ''
        self.no_parallel = False

        opts: list[_Opt] = get_avail_options()
        par = parse_args_init('netcheck', opts)
        parsed = par.parse_args()
        if parsed:
            for (opt, val) in vars(parsed).items():
                if opt == 'num':
                    val = int(val)
                setattr(self, opt, val)

        if not self.hosts:
            self.hosts = ['1.1.1.1', '8.8.8.8']

        if self.ip4_only and self.ip6_only:
            print('Only one of ip4_only/ip6_only allowed. Ignoring')
            self.ip4_only = False
            self.ip6_only = False

        # handle user accidently using comma between hosts
        hosts = []
        for host in self.hosts:
            if ',' in host:
                hosts += host.split(',')
            else:
                hosts.append(host)
        self.hosts = hosts


def parse_args_init(name: str, opts: list[_Opt]):
    '''
    Initialize argparse
    '''
    par = argparse.ArgumentParser(description=name)
    for opt in opts:
        opt_list, kwargs = opt
        if isinstance(opt_list, str):
            par.add_argument(opt_list, **kwargs)
        else:
            par.add_argument(*opt_list, **kwargs)
    return par


def get_avail_options() -> list[_Opt]:
    """
    Options for argparser
    """
    opts: list[_Opt] = []
    val: str | bool | None
    ohelp: str

    val = False
    ohelp = f'Report error if any host has loss instead of all hosts ({val})'
    opts.append((('-a', '--any'), {'action': 'store_true', 'help': ohelp}))

    val = 'ncheck'
    ohelp = f'base name for output ({val})'
    opts.append((('-b', '--base'), {'default': val, 'help': ohelp}))

    val = ''
    ohelp = f'directory to save output ({val})'
    opts.append((('-d', '--dir'), {'default': val, 'help': ohelp}))

    val = '0.25'
    ohelp = f'ping interval ({val})'
    opts.append((('-i', '--interval'), {'default': val, 'help': ohelp}))

    val = ''
    ohelp = f'ping interface or IP address to use as source ({val})'
    opts.append((('-I', '--Interface'), {'default': val, 'help': ohelp}))

    ohelp = 'Use IPv4 only (False})'
    opts.append((('-4', '--ip4-only'), {'action': 'store_true', 'help': ohelp}))

    ohelp = 'Use IPv6 only (False)'
    opts.append((('-6', '--ip6-only'), {'action': 'store_true', 'help': ohelp}))

    val = '100'
    ohelp = f'num pings ({val})'
    opts.append((('-n', '--num'), {'default': val, 'help': ohelp}))

    val = False
    ohelp = f'No parallel ({val})'
    opts.append((('-np', '--no_parallel'), {'action': 'store_true', 'help': ohelp}))

    val = False
    ohelp = f'test mode - generate fake lost packets({val})'
    opts.append((('-t', '--test'), {'action': 'store_true', 'help': ohelp}))

    val = '1.1.1.1,8.8.8.8'
    val = None
    ohelp = f'host(s) comma separated if more than one ({val})'
    opts.append(('hosts', {'default': val, 'help': ohelp, 'nargs': '*'}))

    val = False
    ohelp = f'verbose mode ({val})'
    opts.append((('-v', '--verb'), {'action': 'store_true', 'help': ohelp}))

    return opts
