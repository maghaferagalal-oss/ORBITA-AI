from pydantic import BaseModel, Field
from typing import List

class IndicatorInput(BaseModel):
    sleep_hours: float = Field(ge=0, le=24)
    activity_index: float = Field(ge=0, le=100)
    stress_index: float = Field(ge=0, le=100)
    radiation_index: float = Field(ge=0, le=100)
    hr_deviation_index: float = Field(ge=0, le=100)

class ForecastInput(BaseModel):
    history: List[IndicatorInput] = Field(min_length=3, max_length=90)
