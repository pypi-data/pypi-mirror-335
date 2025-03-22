"""Asset Entity"""

import sys
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, model_validator

if sys.version_info >= (3, 11):
  from typing import Self
else:
  from typing_extensions import Self

from .asset_operation_mode import AssetOperationMode
from .custom_field import CustomField
from .device import Device
from .sensor import Sensor


class Asset(BaseModel):
  """Asset entity definition"""

  pk: int = Field(description='Defines the primary key of the asset')
  name: str = Field(description='Defines the name of the asset')
  vin: Optional[str] = Field(
    default=None,
    description='Defines the serial number of the asset, may be an VIN, or any other unique identifier',
  )
  plate: Optional[str] = Field(default=None, description='Defines the plate number of the asset')
  asset_type: Optional[int] = Field(description='Defines the type of the asset', alias='kind_id', default=None)
  operation_mode: AssetOperationMode = Field(description='Defines the operation mode of the asset')
  sensors: List[Sensor] = Field(default_factory=list, description='Defines the list of sensors of the asset')
  custom_fields: List[CustomField] = Field(
    default_factory=list, description='Defines the list of custom fields of the asset'
  )
  devices: List[Device] = Field(default_factory=list, description='Defines the list of devices of the asset')
  children: List[Self] = Field(default_factory=list, description='Defines the list of children of the asset')

  @model_validator(mode='before')
  def _validate_model(cls: Self, data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate model"""
    operation_mode: Optional[str] = data.get('operation_mode')
    if operation_mode == AssetOperationMode.ASSETMULTIPLE.name:
      data['devices'] = []

    else:
      data['children'] = []

    return data

  @property
  def primary(self: Self) -> Optional[Device]:
    """Get primary device"""
    if self.operation_mode not in [AssetOperationMode.SINGLE, AssetOperationMode.MULTIPLE]:
      return None

    for device in self.devices:
      if device.is_primary:
        return device

    return None
