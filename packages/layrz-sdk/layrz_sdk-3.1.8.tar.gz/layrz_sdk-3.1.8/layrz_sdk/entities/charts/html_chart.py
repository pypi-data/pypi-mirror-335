"""HTML chart"""

import sys
from typing import Any, Dict

from pydantic import BaseModel, Field

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self


class HTMLChart(BaseModel):
  """HTML chart configuration"""

  content: str = Field(description='HTML content of the chart', default='<p>N/A</p>')
  title: str = Field(description='Title of the chart', default='Chart')

  def render(self: Self) -> Dict[str, Any]:
    """
    Render chart to a graphic Library.
    :param technology: The technology to use to render the chart.
    :return: The configuration of the chart.
    """
    return {'library': 'HTML', 'configuration': self._render_html()}

  def _render_html(self: Self) -> Dict[str, Any]:
    """
    Converts the configuration of the chart to HTML render engine.
    """
    config = {'content': self.content, 'title': self.title}

    return config
