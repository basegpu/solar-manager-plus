from pydantic import BaseModel, Field


class Savings(BaseModel):
    notSpent: float = Field()
    sold: float = Field()