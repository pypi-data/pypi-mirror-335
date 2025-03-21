from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Union


class Num(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9


class Plate(Enum):
    ONE = 0
    TWO = 4000


class Letter(Enum):
    A = 4191
    B = 4255
    C = 4319
    D = 4383
    F = 4447


@dataclass
class FiftyFourVialPlate:
    plate: Plate
    letter: Letter
    num: Num

    def value(self) -> int:
        return self.plate.value + self.letter.value + self.num.value


def int_to_ffvp(num: int) -> FiftyFourVialPlate:
    return num


class TenVialColumn(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10


Tray = Union[FiftyFourVialPlate, TenVialColumn]
