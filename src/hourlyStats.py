from datetime import datetime
from enum import Enum
import pandas as pd

from config import Config
from solar_manager import RESOURCES_PATH
from solar_manager.data import get_stats


class HourlyStats:

    class Columns(str, Enum):
        year = 'year'
        month = 'month'
        day = 'day'
        hour = 'hour'
        consumption = 'consumption'
        production = 'production'
        selfConsumption = 'selfConsumption'
    
    _data_cols = [Columns.consumption, Columns.production, Columns.selfConsumption]
    
    _types = {
        Columns.year: 'uint16',
        Columns.month: 'uint8',
        Columns.day: 'uint8',
        Columns.hour: 'uint8',
        Columns.consumption: float,
        Columns.production: float,
        Columns.selfConsumption: float
    }

    def __init__(self, config: Config):
        self._cfg = config
        self._filename = f'{RESOURCES_PATH}/{self._cfg.sm_id}_{self.__class__.__name__.lower()}.csv'
        try:
            # try to load cached data from file
            self._df = pd.read_csv(self._filename, index_col=0, parse_dates=True)
        except FileNotFoundError:
            # otherwise create a new dataframe
            self._df = pd.DataFrame(columns=[e.value for e in self.Columns.__members__.values()])
        # get all hours not already in the dataframe
        hours = [h for h in self._cfg.hourly_datetimes if h not in self._df.index]
        for i in range(len(hours) - 1):
            self.add_row(hours[i], hours[i+1])
        for c,t in self._types.items():
            self._df[c] = self._df[c].astype(t)
        # dump the data (without current day) to a file
        self._df.to_csv(self._filename)
    
    def __str__(self) -> str:
        sumCols = [self.Columns.production, self.Columns.consumption, self.Columns.selfConsumption]
        return ', '.join([f'{v/1e6:.2f} MWh {k}' for k,v in self._df[sumCols].sum().items()])
    
    @property
    def raw(self):
        return self._df
    
    def day_view(self, month: int, rate=1000) -> pd.DataFrame:
        '''Returns the average hourly values for the given month, divided by the transformation rate (default 1000)'''
        filter = f'{self.Columns.month} == {month}'
        return self.raw.query(filter).groupby('hour')[self._data_cols].mean()/rate
    
    def year_view(self, hour: int, rate=1000) -> pd.DataFrame:
        '''Returns the average monthly values for the given hour, divided by the transformation rate (default 1000)'''
        filter = f'{self.Columns.hour} == {hour}'
        return self.raw.query(filter).groupby('month')[self._data_cols].mean()/rate

    def add_row(self, start: datetime, end: datetime) -> None:
        stats = get_stats(self._cfg.sm_id, start, end)
        self._df.loc[start] = [start.year, start.month, start.day, start.hour, stats.consumption, stats.production, stats.selfConsumption]