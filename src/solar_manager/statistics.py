from pydantic import BaseModel, Field


class Statistics(BaseModel):
    # all values are in Wh
    consumption: float = Field()
    production: float = Field()
    selfConsumption: float = Field()

    def __str__(self) -> str:
        return f'consumption: {self.consumption}, production: {self.production}, selfConsumption: {self.selfConsumption}'