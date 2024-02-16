import datetime as dt
from pydantic import BaseModel
import pytz
import yaml


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
    
    def datetime_from_date(self, date: dt.date) -> dt.datetime:
        return dt.datetime(date.year, date.month, date.day, tzinfo=pytz.timezone(self.timezone))
    
    def expected_end(self, amount: float, asof: dt.date = None) -> dt.date:
        if asof is None or self.now.date() == asof:
            asof = self.now
        else:
            asof = self.datetime_from_date(asof + dt.timedelta(days=1))
        delta = asof - self.datetime_from_date(self.date)
        days = delta.total_seconds() / 24 / 3600
        return self.date + dt.timedelta(days=self.volume / amount * days)


with open('src/resources/config.yml', 'r') as stream:
    try:
        cfg = yaml.safe_load(stream)
        CONFIG = Config(**cfg)
    except yaml.YAMLError as e:
        print(e)