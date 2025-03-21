"""Broadcast result"""

from datetime import datetime

from pydantic import BaseModel, Field

from .broadcast_request import BroadcastRequest
from .broadcast_response import BroadcastResponse
from .broadcast_status import BroadcastStatus


class BroadcastResult(BaseModel):
  """Broadcast result data"""

  service_id: int = Field(description='Service ID')
  asset_id: int = Field(description='Asset ID')
  status: BroadcastStatus = Field(description='Broadcast status')
  request: BroadcastRequest = Field(description='Broadcast request')
  response: BroadcastResponse = Field(description='Broadcast response')
  submitted_at: datetime = Field(description='Broadcast submission date')
