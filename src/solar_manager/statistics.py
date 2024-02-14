from pydantic import BaseModel, Field

from config import Slot


class Statistics(BaseModel):
    # all values are in Wh
    consumption: float = Field()
    production: float = Field()
    selfConsumption: float = Field()

    def savings_for(self, slot: Slot) -> float:
        notSpent = self.selfConsumption / 1000 * slot.buy
        sold = (self.production - self.selfConsumption) / 1000 * slot.sell
        return notSpent + sold