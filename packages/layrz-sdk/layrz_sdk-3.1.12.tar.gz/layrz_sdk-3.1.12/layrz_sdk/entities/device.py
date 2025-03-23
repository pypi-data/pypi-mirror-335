"""Device entitiy"""

from pydantic import BaseModel, Field


class Device(BaseModel):
  """Device entity"""

  pk: int = Field(description='Defines the primary key of the device')
  name: str = Field(description='Defines the name of the device')
  ident: str = Field(description='Defines the identifier of the device')
  protocol: str = Field(description='Defines the protocol of the device')
  is_primary: bool = Field(default=False, description='Defines if the device is the primary device')
