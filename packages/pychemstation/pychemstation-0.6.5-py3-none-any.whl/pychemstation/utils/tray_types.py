from __future__ import annotations

import math
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

    @classmethod
    def from_num(cls, num: int) -> Num:
        match num:
            case 1:
                return Num.ONE
            case 2:
                return Num.TWO
            case 3:
                return Num.THREE
            case 4:
                return Num.FOUR
            case 5:
                return Num.FIVE
            case 6:
                return Num.SIX
            case 7:
                return Num.SEVEN
            case 8:
                return Num.EIGHT
            case 9:
                return Num.NINE
            case _:
                raise ValueError("Num is one of 1 to 9")


class Plate(Enum):
    ONE = -96
    TWO = 4000

    @classmethod
    def from_num(cls, plate: int) -> Plate:
        if 1 <= plate <= 2:
            return Plate.ONE if plate == 1 else Plate.TWO
        raise ValueError("Plate is one or 1 or 2")


class Letter(Enum):
    A = 4191
    B = 4255
    C = 4319
    D = 4383
    E = 4447
    F = 4511

    @classmethod
    def from_str(cls, let: str) -> Letter:
        match let:
            case "A":
                return Letter.A
            case "B":
                return Letter.B
            case "C":
                return Letter.C
            case "D":
                return Letter.D
            case "E":
                return Letter.E
            case "F":
                return Letter.F
            case _:
                raise ValueError("Letter is one of A to F")


@dataclass
class FiftyFourVialPlate:
    plate: Plate
    letter: Letter
    num: Num

    def value(self) -> int:
        return self.plate.value + self.letter.value + self.num.value

    @classmethod
    def from_str(cls, loc: str):
        if len(loc) != 5:
            raise ValueError("Plate locations must be PX-LY, where X is either 1 or 2 and Y is 1 to 9")
        try:
            plate = int(loc[1])
            letter = loc[3]
            num = int(loc[4])
            return FiftyFourVialPlate(plate=Plate.from_num(plate),
                                      letter=Letter.from_str(letter),
                                      num=Num.from_num(num))
        except Exception as e:
            raise ValueError("Plate locations must be PX-LY, where X is either 1 or 2 and Y is 1 to 9")

    @classmethod
    def from_int(cls, num: int) -> FiftyFourVialPlate:
        row_starts = [
            # plate 1
            FiftyFourVialPlate.from_str('P1-F1'),
            FiftyFourVialPlate.from_str('P1-E1'),
            FiftyFourVialPlate.from_str('P1-D1'),
            FiftyFourVialPlate.from_str('P1-C1'),
            FiftyFourVialPlate.from_str('P1-B1'),
            FiftyFourVialPlate.from_str('P1-A1'),
            # plate 2
            FiftyFourVialPlate.from_str('P2-F1'),
            FiftyFourVialPlate.from_str('P2-E1'),
            FiftyFourVialPlate.from_str('P2-D1'),
            FiftyFourVialPlate.from_str('P2-C1'),
            FiftyFourVialPlate.from_str('P2-B1'),
            FiftyFourVialPlate.from_str('P2-A1'),
        ]

        # find which row
        possible_row = None
        for i in range(0, 6):
            p1_val = row_starts[i].value()
            p2_val = row_starts[6 + i].value()
            if num >= p2_val:
                possible_row = row_starts[6 + i]
            elif p1_val <= num < row_starts[-1].value():
                possible_row = row_starts[i]
            if possible_row:
                break

        # determine which num
        if possible_row:
            starting_loc = possible_row
            base_val = starting_loc.plate.value + starting_loc.letter.value
            for i in range(1, 10):
                if num - i == base_val:
                    return FiftyFourVialPlate(
                        plate=starting_loc.plate,
                        letter=starting_loc.letter,
                        num=Num.from_num(i))
        raise ValueError("Number didn't match any location. " + str(num))


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
