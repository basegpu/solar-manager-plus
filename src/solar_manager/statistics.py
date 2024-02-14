from pydantic import BaseModel, Field

from config import Tariff


class Statistics(BaseModel):
    # all values are in Wh
    consumption: float = Field()
    production: float = Field()
    selfConsumption: float = Field()

    def savings_for(self, tariff: Tariff) -> float:
        notSpent = self.selfConsumption / 1000 * tariff.buy
        sold = (self.production - self.selfConsumption) / 1000 * tariff.sell
        return notSpent + sold