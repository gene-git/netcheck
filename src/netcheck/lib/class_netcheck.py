'''
 Check network staus using ping
   - Savs results to file(s)
 ------------
  2018-12-12
 ------------
'''
# pylint: disable=too-few-public-methods,too-many-locals
# pylint: disable=too-many-instance-attributes
# ---------------------------------
from typing import (List)
import os
import time
import random

from pyconcurrent import (ProcRunAsyncio, ProcResult)
from .class_conf import Conf
from .class_result import (Result, merge_results)
# ---------------------------------


class NetCheck:
    '''
    Data for network check of 1 host
    '''
    def __init__(self):
        self.start_time = time.localtime()
        self.ping_cmd = ''
        self.result = []

        self.conf = Conf()
        self.set_ping_cmd()

    def set_ping_cmd(self):
        """ ping command without host """
        conf = self.conf
        num = conf.num
        interval = conf.interval

        self.ping_cmd = '/usr/bin/ping'
        if self.conf.ip4_only:
            self.ping_cmd += ' -4'

        elif self.conf.ip6_only:
            self.ping_cmd += ' -6'

        self.ping_cmd += f' -c {num} -A -i {interval}'

        if not conf.verb:
            self.ping_cmd += ' -q'

        if conf.Interface:
            self.ping_cmd += f' -I {conf.Interface}'

        if conf.verb:
            print(f' Using: {self.ping_cmd} ({conf.hosts})')

    async def check(self):
        """
        Run concurrently ping of each host
        """
        conf = self.conf
        if conf.no_parallel:
            num = 1
        else:
            num = len(conf.hosts)

        pargs = self.ping_cmd.split()
        count = 1
        tasks = []
        for host in conf.hosts:
            tasks.append((count, host))
            count += 1
        proc = ProcRunAsyncio(pargs, tasks, num_workers=num, timeout=30)
        await proc.run_all()

        self.result = self.extract_results(proc.result)

    def extract_results(self, proc_results: List[ProcResult]) -> List[Result]:
        """
        Extract result data from
        """
        conf = self.conf
        results: List[Result] = []
        if not proc_results:
            return results

        for pres in proc_results:
            host = pres.arg
            res = Result(host)
            results.append(res)
            res.success = pres.success
            if pres.time_start and pres.time_start > 0:
                res.time_start = time.localtime(pres.time_start)
            if pres.time_end:
                res.time_end = time.localtime(pres.time_end)

            if res.success and pres.stdout is not None:
                #
                # Keep the parts we need
                #
                stdout = pres.stdout.split('\n')
                stdout = stdout[-3:]
                send_recv = stdout[0].split(",")
                rtt = stdout[1].split("=")[1].split("/")

                res.nsent = int(send_recv[0].split(" ")[0])
                res.nrecv = int(send_recv[1].split(" ")[1])

                # fake packet loss for test
                if conf.test:
                    if random.randint(0, 1) > 0:
                        res.nrecv -= random.randint(0, res.nsent)

                res.nlost = res.nsent - res.nrecv
                res.loss_pct = 100.0 * res.nlost / res.nsent

                res.min = get_float(0.0, rtt[0])
                res.avg = get_float(0.0, rtt[1])
                res.max = get_float(0.0, rtt[2])
                res.dev = get_float(0.0, rtt[3].split(" ")[0])

                res.bad_hosts = 1 if res.nlost > 0 else 0

            else:
                res.nsent = conf.num
                res.nrecv = 0
                res.nlost = conf.num
                res.loss_pct = 100
                res.min = 0
                res.avg = 0
                res.max = 0
                res.dev = 0
                res.bad_hosts = 1
        return results

    def reports(self):
        """
        Save results
         - terminal output only if either:
             - conf.verb = True
           or
             - any all hosts have packet loss or 1 or more has loss
               when conf.any == True
         - Saved to files:
             - Only if at least 1 dropped packed for that file. for that file.
        """
        conf = self.conf
        num_hosts = len(conf.hosts)

        res_merged = merge_results(self.result)
        start = time.strftime("%Y-%m-%d %H:%M:%S", res_merged.time_start)
        end = time.strftime("%Y-%m-%d %H:%M:%S", res_merged.time_end)

        #
        # do we report
        #
        any_hosts_bad = res_merged.bad_hosts > 0
        all_hosts_bad = res_merged.bad_hosts == num_hosts
        report_any_bad = conf.any

        terminal_output = False
        if conf.verb or (any_hosts_bad and (all_hosts_bad or report_any_bad)):
            terminal_output = True

        if terminal_output:
            hosts_all = ' '.join(conf.hosts)
            result = self.result
            hosts_loss_lst = [res.host for res in result if res.bad_hosts > 0]
            hosts_loss = ' '.join(hosts_loss_lst)

            isbad = '' if any_hosts_bad else 'No '
            print(f'\n\t*** {isbad}Packets lost ***\n')
            print(f' Hosts        : {hosts_all}')
            print(f' With Loss    : {hosts_loss}')
            print(f' Start        : {start}')
            print(f' End          : {end}')
            print(f' Failed hosts : {res_merged.bad_hosts}\n')

        if res_merged.bad_hosts > 0:
            if terminal_output:
                print('Merged Result:')
                res_merged.print(hdr_on=True)
            if conf.dir:
                # save 2 files - any loss and all hosts have losses
                if any_hosts_bad:
                    file = os.path.join(conf.dir, f'{conf.base}-merged.any')
                    res_merged.save(file)
                if all_hosts_bad:
                    file = os.path.join(conf.dir, f'{conf.base}-merged.all')
                    res_merged.save(file)

        if terminal_output:
            print('')
        hdr_on = True
        for res in self.result:
            if res.bad_hosts <= 0:
                continue
            if terminal_output:
                res.print(hdr_on=hdr_on)
            hdr_on = False
            if conf.dir:
                file = os.path.join(conf.dir, f'{conf.base}-{res.host}')
                res.save(file)

# ---------------------------------
# Helpers
# ---------------------------------


def get_float(default, string) -> float:
    """
    if string is a number return as float else return default
    """
    try:
        fnum = float(string)
    except ValueError:
        fnum = default
    return fnum
