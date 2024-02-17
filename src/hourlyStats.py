from datetime import datetime
from enum import Enum
import pandas as pd

from config import Config
from solar_manager.data import get_stats
from utils import RESOURCES_PATH


class HourlyStats:

    class Columns(str, Enum):
        year = 'year'
        month = 'month'
        day = 'day'
        hour = 'hour'
        consumption = 'consumption'
        production = 'production'
        selfConsumption = 'selfConsumption'
    
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
            self._df = pd.DataFrame(columns=self.Columns.__members__.keys())
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
        return ', '.join([f'{v:.1f} {k}' for k,v in self._df[sumCols].sum().items()])
    
    @property
    def raw(self):
        return self._df

    def add_row(self, start: datetime, end: datetime) -> None:
        stats = get_stats(self._cfg.sm_id, start, end)
        self._df.loc[start] = [start.year, start.month, start.day, start.hour, stats.consumption, stats.production, stats.selfConsumption]