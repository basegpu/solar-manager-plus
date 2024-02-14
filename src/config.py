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
    def dates(self) -> list[dt.date]:
        today = dt.datetime.now(pytz.timezone(self.timezone)).date()
        return [self.date + dt.timedelta(days=x) for x in range((today - self.date).days + 1)]
    
    def expected_end(self, amount: float) -> dt.date:
        return self.date + dt.timedelta(days=(self.volume / amount))


with open('src/resources/config.yml', 'r') as stream:
    try:
        cfg = yaml.safe_load(stream)
        CONFIG = Config(**cfg)
    except yaml.YAMLError as e:
        print(e)