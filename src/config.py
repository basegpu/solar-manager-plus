import datetime as dt
from dateutil.rrule import rrule, HOURLY
import glob
from pydantic import BaseModel
import pytz
import streamlit as st
import yaml

from utils import RESOURCES_PATH


class Tariff(BaseModel):
    
    sell: float
    buy: float

    def __str__(self) -> str:
        return f'({self.sell} / {self.buy})'


class Slots(BaseModel):
    
    first_date: dt.date
    last_date: dt.date
    days_of_week: list[int]
    switching_hours: list[int] = []

    def __str__(self) -> str:
        return f'{self.start} - {self.end}'


class Config(BaseModel):

    name: str
    date: dt.date
    volume: int
    location: str
    timezone: str
    sm_id: str
    tariffs: list[Tariff] = []
    structure: list[Slots] = []

    def __str__(self) -> str:
        return self.name
    
    @property
    def now(self) -> dt.datetime:
        return dt.datetime.now(pytz.timezone(self.timezone))
    
    @property
    def dates(self) -> list[dt.date]:
        return [self.date + dt.timedelta(days=x) for x in range((self.now.date() - self.date).days + 1)]

    @property
    def hourly_datetimes(self) -> list[dt.datetime]:
        start = self.datetime_from_date(self.dates[0])
        end = self.datetime_from_date(self.dates[-1])
        return [dt for dt in rrule(HOURLY, dtstart=start, until=end)]
    
    def datetime_from_date(self, date: dt.date) -> dt.datetime:
        return dt.datetime(date.year, date.month, date.day, tzinfo=pytz.timezone(self.timezone))


CONFIGS = []
yml_files = glob.glob(f'{RESOURCES_PATH}/*.yml')
for file in yml_files:
    with open(file, 'r') as stream:
        try:
            cfg = yaml.safe_load(stream)
            CONFIGS.append(Config(**cfg))
        except yaml.YAMLError as e:
            print(e)


def set_config(config: Config) -> None:
    st.session_state['config'] = config

def get_config() -> Config:
    return st.session_state['config']