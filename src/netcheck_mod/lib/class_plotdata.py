# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2025-present Gene C <arch@sapience.com>
'''
Plot helpers
'''
# pylint: disable=too-many-function-args
from typing import (Tuple)
from datetime import datetime
import dateutil
from dateutil.relativedelta import relativedelta
import pandas as pd


class PlotData:
    '''
    data in convenient form
    '''
    def __init__(self, fpath: str):

        self.df: pd.DataFrame
        self.dates: pd.DatetimeIndex
        self.df_range: pd.core.frame.DataFrame

        self.read_csv(fpath)

    def read_csv(self, fpath: str):
        '''
        Read csv file
          start_date,start_time,nsent,nrecv,nlost,loss_pct,min,avg,max,dev,end_date,end_time
        '''
        if not fpath:
            return

        df = pd.read_csv(fpath)

        df['dates'] = pd.to_datetime(df['start_date'] + ' ' + df['start_time'])
        self.dates = df['dates'].iloc[0]
        self.df = df

    def date_times(self) -> list[str]:
        '''
        Return list of dates
        '''
        dates: list[str] = []
        dts = self.df_range['dates']
        if not dts:
            return dates

        diff = dts[-1] - dts[0]
        days_diff = diff.days

        with_time = False
        if days_diff > 1:
            with_time = True

        for dt in dts:
            if with_time:
                elem = datetime.strftime(dt, '%Y-%m-%d %H:%M')
            else:
                elem = datetime.strftime(dt, '%Y-%m-%d')
            dates.append(elem)
        return dates

    def loss_pct(self):
        '''
        Return list of dates
        '''
        loss_pct = self.df_range['loss_pct']
        return loss_pct

    def date_range(self, t0: str, t1: str):
        '''
        Make new df filtered by t0 -> t1
        t0 / t1 can be:
            date
            now-<num><units>    e.g. now-12h
            start+<num><units>
            end-<num><units>
        '''
        now = datetime.now()
        t0_dt = self.date_filter(now, t0)
        t1_dt = self.date_filter(now, t1)

        if not t0_dt and not t1_dt:
            self.df_range = self.df
            return

        df = self.df_range

        if t0_dt and t1_dt:
            self.df_range = df[(df['dates'] >= t0_dt) & (df['dates'] <= t1_dt)]

        elif t0_dt:
            self.df_range = df[(df['dates'] >= t0_dt)]

        elif t1_dt:
            self.df_range = df[(df['dates'] <= t1_dt)]

    def loss_series(self):
        '''
        Return pd Series
        '''
        dates = self.df_range['dates']
        loss = self.df_range['loss_pct']
        time_series = pd.Series(data=list(loss), index=dates)
        return time_series

    def date_filter(self, now: datetime, t0: str) -> datetime | None:
        '''
        find date from
            - date
            - now-<num><units>
            - start+<num><units>
            - end-<num><units>
        If t0 is not a filter then return None
        '''
        (what, digits, units) = tparse(t0)
        if not what:
            return None

        date = None
        if what == 'date':
            date = dateutil.parser.parse(t0)
        else:
            df = self.df_range
            dates = df['dates']
            args = {units: digits}

            match what:
                case 'now':
                    date = now + relativedelta(**args)  # type: ignore[arg-type]

                case 'start':
                    date = dates[0] + relativedelta(**args)  # type: ignore[arg-type]

                case 'end':
                    date = dates[-1] + relativedelta(**args)  # type: ignore[arg-type]
        return date


def units_standard(units: str) -> str:
    '''
    Map units to standard used by dateutil
    these are relative (plural)
    years, months, weeks, days, hours, minutes, seconds, microseconds:
    '''
    sunit = 'days'
    if units.startswith('y'):
        sunit = 'years'

    elif units.startswith('mo'):
        sunit = 'months'

    elif units.startswith('w'):
        sunit = 'weeks'

    elif units.startswith('d'):
        sunit = 'days'

    elif units.startswith('h'):
        sunit = 'hours'

    elif units.startswith('m'):
        sunit = 'minutes'

    elif units.startswith('s'):
        sunit = 'seconds'

    return sunit


def tparse(t0: str) -> Tuple[str | None, int, str]:
    '''
    Parse t0
    returns
        what, num, units
    '''
    if not t0 or t0 == 'all':
        return (None, 0, '')

    keys = ['now', 'start', 'end']
    what = None
    for key in keys:
        if t0.startswith(key):
            what = key
            break

    if what:
        sign = 1
        tnext = t0.replace(what, '')
        if tnext[0] == '-':
            sign = -1
            tnext = tnext[1:]
        elif tnext[0] == '+':
            tnext = tnext[1:]

        digits_list = [num for num in tnext[0:] if num.isdigit()]
        digits_str = ''.join(digits_list)
        units = tnext.replace(digits_str, '')
        digits = sign*int(digits_str)
        units = units_standard(units)

    else:
        what = 'date'
        digits = 0
        units = ''

    return (what, digits, units)
