"""Report page"""

from typing import List

from pydantic import BaseModel, Field

from .report_header import ReportHeader
from .report_row import ReportRow


class ReportPage(BaseModel):
  """Report page definition"""

  name: str = Field(description='Name of the page. Length should be less than 60 characters')
  headers: List[ReportHeader] = Field(description='List of report headers', default_factory=list)
  rows: List[ReportRow] = Field(description='List of report rows', default_factory=list)
  freeze_header: bool = Field(description='Freeze header', default=False)
