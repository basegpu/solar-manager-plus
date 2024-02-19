from datetime import datetime, date, timedelta
from enum import Enum
import math
from random import randint
import sys
import pandas as pd
import pytz

from config import Config, Tariff
from solar_manager import RESOURCES_PATH
from solar_manager.data import get_stats


class Savings:

    class Columns(str, Enum):
        notSpent = 'not spent'
        sold = 'sold'
        total = 'total'
        expected = 'expected end'

    def __init__(self, config: Config):
        self._cfg = config
        self._filename = f'{RESOURCES_PATH}/{self._cfg.sm_id}_{self.__class__.__name__.lower()}.csv'
        try:
            # try to load cached data from file
            self._df = pd.read_csv(self._filename, index_col=0, parse_dates=True)
            self._df.index = self._df.index.date
        except FileNotFoundError:
            # otherwise create a new dataframe
            self._df = pd.DataFrame(columns=[e.value for e in self.Columns.__members__.values()])
        for date in config.dates:
            if date in self._df.index:
                # if there is already data for the date, skip loading it
                continue
            else:
                # otherwise init a new row
                self._df.loc[date] = [0, 0, 0, None]
            # find the slots for the date
            slots = next(s for s in self._cfg.structure if s.first_date <= date <= s.last_date and date.weekday()+1 in s.days_of_week)
            # loop through the slots and add the according savings
            hours = [0] + slots.switching_hours + [24]
            for i in range(len(hours) - 1):
                start = datetime(date.year, date.month, date.day, hours[i], tzinfo=pytz.timezone('CET'))
                end = datetime(date.year, date.month, date.day, hours[i+1]-1, 59, 59, 999, tzinfo=pytz.timezone('CET'))
                self.add_savings(start, end, self._cfg.tariffs[i%2])
            # do some post processing
            previous = self._df[self.Columns.total].shift().iloc[-1]
            self._df.at[date, self.Columns.total] = (0.0 if math.isnan(previous) else previous) + self._df.loc[date].sum()
            self._df.at[date, self.Columns.expected] = self.calc_expected_end(self._df.at[date, self.Columns.total], date)
        # dump the data (without current day) to a file
        self._df.iloc[0:-1].to_csv(self._filename)
    
    def __str__(self) -> str:
        return ', '.join([f'{v:.1f} {k}' for k,v in self._df[[self.Columns.notSpent, self.Columns.sold]].sum().items()])
    
    @property
    def raw(self):
        return self._df
    
    @property
    def last_status(self):
        return self._df[[self.Columns.total, self.Columns.expected]].iloc[-1]

    def add_savings(self, start: datetime, end: datetime, tariff: Tariff) -> None:
        cache_id = randint(0, sys.maxsize) if start.date() <= self._cfg.now.date() <= end.date() else 0
        stats = get_stats(self._cfg.sm_id, start, end, cache_id)
        self._df.at[start.date(), self.Columns.notSpent] += stats.selfConsumption / 1000 * tariff.buy
        self._df.at[start.date(), self.Columns.sold] += (stats.production - stats.selfConsumption) / 1000 * tariff.sell
    
    def calc_expected_end(self, amount: float, asof: date = None) -> date:
        if asof is None or self._cfg.now.date() == asof:
            asof = self._cfg.now
        else:
            asof = self._cfg.datetime_from_date(asof + timedelta(days=1))
        delta = asof - self._cfg.datetime_from_date(self._cfg.date)
        days = delta.total_seconds() / 24 / 3600
        return self._cfg.date + timedelta(days=self._cfg.volume / amount * days)