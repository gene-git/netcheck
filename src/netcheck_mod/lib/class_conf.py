# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2025-present Gene C <arch@sapience.com>
'''
 Check network staus using ping
   - Savs results to file(s)
 ------------
  2018-12-12
 ------------
'''
# pylint: disable=too-few-public-methods,invalid-name
# pylint: disable=too-many-instance-attributes
# ---------------------------------
from typing import (List)
import argparse


class Conf:
    """
     Command line inputs.

     Args:
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
        self.hosts: List[str] = []
        self.num = 100
        self.interval = ''
        self.Interface = ''
        self.ip4_only: bool = False
        self.ip6_only: bool = False

        self.any = False
        self.verb = False

        self.dir = ''
        self.base = ''
        self.no_parallel = False

        opts = get_avail_options()
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


def parse_args_init(name: str, opts):
    '''
    Initialize argparse
    '''
    par = argparse.ArgumentParser(description=name)
    for (opt_keys, kwargs) in opts:
        if isinstance(opt_keys, tuple) and opt_keys[1]:
            opt_short = opt_keys[0]
            opt_long = opt_keys[1]
            par.add_argument(opt_short, opt_long, **kwargs)
        else:
            opt_short = opt_keys
            par.add_argument(opt_short, **kwargs)
    return par


def get_avail_options():
    """
    Options for argparser
    """
    opts = []
    val: str | bool | None

    val = False
    ohelp = f'Report error if any host has loss instead of all hosts ({val})'
    opt = [('-a', '--any'), {'action': 'store_true', 'help': ohelp}]
    opts.append(opt)

    val = 'ncheck'
    ohelp = f'base name for output ({val})'
    opt = [('-b', '--base'), {'default': val, 'help': ohelp}]
    opts.append(opt)

    val = ''
    ohelp = f'directory to save output ({val})'
    opt = [('-d', '--dir'), {'default': val, 'help': ohelp}]
    opts.append(opt)

    val = '0.25'
    ohelp = f'ping interval ({val})'
    opt = [('-i', '--interval'), {'default': val, 'help': ohelp}]
    opts.append(opt)

    val = ''
    ohelp = f'ping interface or IP address to use as source ({val})'
    opt = [('-I', '--Interface'), {'default': val, 'help': ohelp}]
    opts.append(opt)

    ohelp = 'Use IPv4 only (False})'
    opt = [('-4', '--ip4-only'), 
           {'action': 'store_true', 'help': ohelp}]
    opts.append(opt)

    ohelp = f'Use IPv6 only (False)'
    opt = [('-6', '--ip6-only'), 
           {'action': 'store_true', 'help': ohelp}]
    opts.append(opt)

    val = '100'
    ohelp = f'num pings ({val})'
    opt = [('-n', '--num'), {'default': val, 'help': ohelp}]
    opts.append(opt)

    val = False
    ohelp = f'No parallel ({val})'
    opt = [('-np', '--no_parallel'), {'action': 'store_true', 'help': ohelp}]
    opts.append(opt)

    val = False
    ohelp = f'test mode - generate fake lost packets({val})'
    opt = [('-t', '--test'), {'action': 'store_true', 'help': ohelp}]
    opts.append(opt)

    val = '1.1.1.1,8.8.8.8'
    val = None
    ohelp = f'host(s) comma separated if more than one ({val})'
    opt = [('hosts'), {'default': val, 'help': ohelp, 'nargs': '*'}]
    opts.append(opt)

    val = False
    ohelp = f'verbose mode ({val})'
    opt = [('-v', '--verb'), {'action': 'store_true', 'help': ohelp}]
    opts.append(opt)

    return opts
