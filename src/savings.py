from datetime import datetime, date
import pandas as pd
import pytz

from config import CONFIG, Tariff
from solar_manager.data import get_stats
from solar_manager.statistics import Statistics


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
                stats = get_stats(CONFIG.sm_id, start, end)
                self.add_savings(date, stats, CONFIG.tariffs[i%2])
        self._cumsum = self._df.sum(axis=1).cumsum().to_frame('total')
        self._cumsum['expected end'] = self._cumsum.apply(lambda x: CONFIG.expected_end(x['total'], x.name), axis=1)
    
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

    def add_savings(self, date: date, stats: Statistics, tariff: Tariff) -> None:
        self._df.at[date, 'notSpent'] += stats.selfConsumption / 1000 * tariff.buy
        self._df.at[date, 'sold'] += (stats.production - stats.selfConsumption) / 1000 * tariff.sell