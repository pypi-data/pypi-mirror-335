"""Number chart"""

import sys
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from .chart_render_technology import ChartRenderTechnology
from .table_header import TableHeader
from .table_row import TableRow

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self


class TableChart(BaseModel):
  """Table chart configuration"""

  columns: List[TableHeader] = Field(description='List of columns', default_factory=list)
  rows: List[TableRow] = Field(description='List of rows', default_factory=list)

  def render(self: Self, technology: ChartRenderTechnology = ChartRenderTechnology.FLUTTER) -> Dict[str, Any]:
    """
    Render chart to a graphic Library.
    :param technology: The technology to use to render the chart.
    :return: The configuration of the chart.
    """
    if technology == ChartRenderTechnology.FLUTTER:
      return {
        'library': 'FLUTTER',
        'chart': 'TABLE',
        'configuration': self._render_flutter(),
      }

    return {
      'library': 'FLUTTER',
      'chart': 'TEXT',
      'configuration': [f'Unsupported {technology}'],
    }

  def _render_flutter(self: Self) -> Dict[str, Any]:
    """
    Converts the configuration of the chart to a Flutter native components.
    """
    return {
      'columns': [{'key': column.key, 'label': column.label} for column in self.columns],
      'rows': [{'data': row.data} for row in self.rows],
    }
