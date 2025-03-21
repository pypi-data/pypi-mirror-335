from dataclasses import dataclass


@dataclass
class Pump:
    solvent: str
    in_use: bool
