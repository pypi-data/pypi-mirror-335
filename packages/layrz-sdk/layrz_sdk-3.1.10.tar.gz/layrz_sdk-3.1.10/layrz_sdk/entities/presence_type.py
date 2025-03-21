from enum import Enum


class PresenceType(Enum):
  """Presence type enum"""

  ENTRANCE = 'ENTRANCE'
  EXIT = 'EXIT'

  def __str__(self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self) -> str:
    """Readable property"""
    return f'PresenceType.{self.name}'
