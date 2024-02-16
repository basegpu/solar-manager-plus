from datetime import datetime, date, timedelta
from random import randint
import sys
import pandas as pd
import pytz

from config import Config, Tariff
from solar_manager.data import get_stats_data


class Savings:

    def __init__(self, config: Config):
        self._cfg = config
        dates = config.dates
        self._df = pd.DataFrame({'notSpent': [0.0]*len(dates), 'sold': [0.0]*len(dates)}, index=dates)
        for date in dates:
            # find the slots for the date
            slots = next(s for s in self._cfg.structure if s.first_date <= date <= s.last_date and date.weekday() in s.days_of_week)
            # loop through the slots and get the according stats
            hours = [0] + slots.switching_hours + [24]
            for i in range(len(hours) - 1):
                start = datetime(date.year, date.month, date.day, hours[i], tzinfo=pytz.timezone('CET'))
                end = datetime(date.year, date.month, date.day, hours[i+1]-1, 59, 59, 999, tzinfo=pytz.timezone('CET'))
                self.add_savings(start, end, self._cfg.tariffs[i%2])
        self._cumsum = self._df.sum(axis=1).cumsum().to_frame('total')
        self._cumsum['expected end'] = self._cumsum.apply(lambda x: self.calc_expected_end(x['total'], x.name), axis=1)
    
    def __str__(self) -> str:
        return ', '.join([f'{v:.1f} {k}' for k,v in self._df.sum().items()])
    
    @property
    def raw(self):
        return self._df
    
    @property
    def last_status(self):
        return self._cumsum.iloc[-1]
    
    @property
    def expected_ends(self):
        return self._cumsum['expected end']

    def add_savings(self, start: datetime, end: datetime, tariff: Tariff) -> None:
        cache_id = randint(0, sys.maxsize) if start.date() <= self._cfg.now.date() <= end.date() else 0
        stats = get_stats_data(self._cfg.sm_id, start, end, cache_id)
        self._df.at[start.date(), 'notSpent'] += stats.selfConsumption / 1000 * tariff.buy
        self._df.at[start.date(), 'sold'] += (stats.production - stats.selfConsumption) / 1000 * tariff.sell
    
    def calc_expected_end(self, amount: float, asof: date = None) -> date:
        if asof is None or self._cfg.now.date() == asof:
            asof = self._cfg.now
        else:
            asof = self._cfg.datetime_from_date(asof + timedelta(days=1))
        delta = asof - self._cfg.datetime_from_date(self._cfg.date)
        days = delta.total_seconds() / 24 / 3600
        return self._cfg.date + timedelta(days=self._cfg.volume / amount * days)