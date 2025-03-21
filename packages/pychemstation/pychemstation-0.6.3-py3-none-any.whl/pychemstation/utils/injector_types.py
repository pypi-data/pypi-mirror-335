from dataclasses import dataclass
from enum import Enum
from typing import  Union, Optional

from pychemstation.utils.tray_types import Tray


class SourceType(Enum):
    DEFAULT = "ActualPosition"
    SPECIFIC_LOCATION = "ActualPositionPlusLocation"
    LOCATION = "Location"


class Mode(Enum):
    DEFAULT = "Default"
    SET = "Set"


@dataclass
class Draw:
    amount: Optional[float] = None
    location: Optional[str] = None
    source: Optional[Tray] = None


@dataclass
class Wait:
    duration: int


@dataclass
class Inject:
    pass


class RemoteCommand(Enum):
    START = "START"
    PREPARE = "PREPARE"


@dataclass
class Remote:
    command: RemoteCommand
    duration: int


InjectorFunction = Union[Draw, Wait, Inject, Remote]


@dataclass
class InjectorTable:
    functions: list[InjectorFunction]
