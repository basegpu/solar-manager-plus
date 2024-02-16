from datetime import datetime, date, timedelta
from random import randint
import sys
import pandas as pd
import pytz

from config import CONFIG, Tariff
from solar_manager.data import get_stats_data


class Savings:

    def __init__(self):
        keys = ['notSpent', 'sold']
        self._df = pd.DataFrame({key: [0.0] * len(CONFIG.dates) for key in keys}, index=CONFIG.dates)
        for date in self._df.index:
            # find the slots for the date
            slots = next(s for s in CONFIG.structure if s.first_date <= date <= s.last_date and date.weekday() in s.days_of_week)
            # loop through the slots and get the according stats
            hours = [0] + slots.switching_hours + [24]
            for i in range(len(hours) - 1):
                start = datetime(date.year, date.month, date.day, hours[i], tzinfo=pytz.timezone('CET'))
                end = datetime(date.year, date.month, date.day, hours[i+1]-1, 59, 59, 999, tzinfo=pytz.timezone('CET'))
                self.add_savings(start, end, CONFIG.tariffs[i%2])
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
        cache_id = randint(0, sys.maxsize) if start.date() <= CONFIG.now.date() <= end.date() else 0
        stats = get_stats_data(CONFIG.sm_id, start, end, cache_id)
        self._df.at[start.date(), 'notSpent'] += stats.selfConsumption / 1000 * tariff.buy
        self._df.at[start.date(), 'sold'] += (stats.production - stats.selfConsumption) / 1000 * tariff.sell
    
    def calc_expected_end(self, amount: float, asof: date = None) -> date:
        if asof is None or CONFIG.now.date() == asof:
            asof = CONFIG.now
        else:
            asof = CONFIG.datetime_from_date(asof + timedelta(days=1))
        delta = asof - CONFIG.datetime_from_date(CONFIG.date)
        days = delta.total_seconds() / 24 / 3600
        return CONFIG.date + timedelta(days=CONFIG.volume / amount * days)