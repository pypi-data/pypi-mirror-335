from typing import List

from pydantic import BaseModel, Field

from .timeline_serie_item import TimelineSerieItem


class TimelineSerie(BaseModel):
  """Chart Data Serie for Timeline charts"""

  data: List[TimelineSerieItem] = Field(description='List of data points', default_factory=list)
  label: str = Field(description='Label of the serie')
