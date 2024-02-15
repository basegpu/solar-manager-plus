from pydantic import BaseModel, Field

from config import Tariff
from savings import Savings


class Statistics(BaseModel):
    # all values are in Wh
    consumption: float = Field()
    production: float = Field()
    selfConsumption: float = Field()

    def __str__(self) -> str:
        return f'consumption: {self.consumption}, production: {self.production}, selfConsumption: {self.selfConsumption}'

    def savings_for(self, tariff: Tariff) -> Savings:
        return Savings(
            notSpent = self.selfConsumption / 1000 * tariff.buy,
            sold = (self.production - self.selfConsumption) / 1000 * tariff.sell)