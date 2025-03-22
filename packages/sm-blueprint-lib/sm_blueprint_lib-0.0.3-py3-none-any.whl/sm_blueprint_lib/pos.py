from dataclasses import dataclass
from typing import Sequence


@dataclass
class Pos:
    """Class that represents the position of a block (x, y, z)
    """
    x: int
    y: int
    z: int

    def __add__(self, o: "Pos" | Sequence):
        if isinstance(o, Pos):
            return Pos(self.x + o.x, self.y + o.y, self.z + o.z)
        return Pos(self.x + o[0], self.y + o[1], self.z + o[2])
