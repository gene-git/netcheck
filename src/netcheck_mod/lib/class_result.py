# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2025-present Gene C <arch@sapience.com>
'''
 Check network staus using ping
   - Savs results to file(s)
 ------------
  2018-12-12
 ------------
'''
# pylint: disable=too-few-public-methods,too-many-instance-attributes
# ---------------------------------
from typing import (List)
import os
import time
import copy
# ---------------------------------


class Result:
    """  ping result """
    def __init__(self, host):
        self.host: str = host
        self.time_start = time.localtime()
        self.time_end: time.struct_time = self.time_start
        self.success: bool = True
        self.nsent: int = 0
        self.nrecv: int = 0
        self.nlost: int = 0
        self.loss_pct: float = 0.0
        self.min: float = 0.0
        self.max: float = 0.0
        self.avg: float = 0.0
        self.dev: float = 0.0

        # count of number of hosts with any lost packets
        # non-merged = 1 if nlost > 0 else 0
        # for mergeed = num hosts with nlost >0
        self.bad_hosts = 0

    def print(self, hdr_on=True):
        """ print to stdout """
        end_time = time.strftime("%H:%M:%S", self.time_end)

        host = self.host
        if len(host) > 15:
            host = self.host[0:15]

        if hdr_on:
            hdr = f'{"host":15s} '
            hdr += f'{"nsent":>5s} {"nrecv":>5s} {"nlost":>5s}  '
            hdr += f'{"loss":>5s} {"min":>5s} {"avg":>5s} {"max":>5s} {"dev":>5s} '
            hdr += f'{"End":>8s}'
            print(hdr)

        if ',' in host:
            ind = host.find(',')
            host = host[0:ind] + ' ...'
        data = f'{host:15s} '
        data += f'{self.nsent:>5d} {self.nrecv:5d} {self.nlost:5d}  '
        data += f'{self.loss_pct:5.1f} {self.min:5.1f} {self.avg:5.1f} {self.max:5.1f} {self.dev:5.1f}'
        data += f' {end_time}'
        print(data)

    def save(self, file):
        """ save to file in CSV format """
        start_date = time.strftime("%Y-%m-%d", self.time_start)
        start_time = time.strftime("%H:%M:%S", self.time_start)

        end_date = time.strftime("%Y-%m-%d", self.time_end)
        end_time = time.strftime("%H:%M:%S", self.time_end)

        # header
        hdr = None
        if not os.path.exists(file):
            hdr = f'{"start_date"},{"start_time"},'
            hdr += f'{"nsent"},{"nrecv"},{"nlost"},'
            hdr += f'{"loss_pct"},{"min"},{"avg"},{"max"},{"dev"},'
            hdr += f'{"end_date"},{"end_time"}'
            hdr += '\n'

        # data
        line = f'{start_date},{start_time},'
        line += f'{self.nsent},{self.nrecv},{self.nlost},'
        line += f'{self.loss_pct:.1f},{self.min:.3f},{self.avg:.3f},{self.max:.3f},{self.dev:.3f},'
        line += f'{end_date},{end_time}'
        line += '\n'

        with open(file, 'a', encoding='utf-8') as fob:
            if hdr:
                fob.write(hdr)
            fob.write(line)


def merge_results(results: List[Result]) -> Result:
    """
    Merge multiple results together
     - numeric are summed or averaged as appropriate
    """
    num_hosts = len(results)
    if num_hosts < 2:
        return results[0]

    merged = copy.copy(results[0])
    merged.host = f'Total ({num_hosts})'
    for res in results[1:]:
        # merged.host += f',{res.host}'

        merged.success &= res.success
        merged.nsent += res.nsent
        merged.nrecv += res.nrecv
        merged.nlost += res.nlost

        merged.bad_hosts += res.bad_hosts

        merged.min = min(merged.min, res.min)
        merged.max = max(merged.max, res.min)
        merged.avg += res.avg
        merged.dev += res.dev

        merged.time_start = min(res.time_start, merged.time_start)
        merged.time_end = max(res.time_end, merged.time_end)

    merged.loss_pct = 100. * merged.nlost/merged.nsent
    merged.avg /= num_hosts
    merged.dev /= num_hosts

    return merged
