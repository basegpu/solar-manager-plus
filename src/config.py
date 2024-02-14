import datetime as dt
from pydantic import BaseModel
import yaml


class Price(BaseModel):
    
    start: dt.date
    end: dt.date
    sell: float
    buy: float

    def __str__(self) -> str:
        return f'{self.start} - {self.end}'


class Config(BaseModel):

    name: str
    date: dt.date
    volume: int
    location: str
    prices: list[Price] = []

    def __str__(self) -> str:
        return self.name
    
    @property
    def dates(self) -> list[dt.date]:
        return [self.date + dt.timedelta(days=x) for x in range((dt.date.today() - self.date).days + 1)]
    
    def expected_end(self, amount: float) -> dt.date:
        return self.date + dt.timedelta(days=(self.volume / amount))


with open('src/resources/config.yml', 'r') as stream:
    try:
        cfg = yaml.safe_load(stream)
        CONFIG = Config(**cfg)
    except yaml.YAMLError as e:
        print(e)