from dataclasses import dataclass, field

from .basepart import BasePart
from ...bounds import Bounds
from ...constants import AXIS


@dataclass
class BaseBoundablePart(BasePart):
    """Base class for all Boundable parts (those that are draggable)
    """
    bounds: Bounds
    xaxis: int = field(kw_only=True, default=AXIS.DEFAULT_XAXIS)
    zaxis: int = field(kw_only=True, default=AXIS.DEFAULT_ZAXIS)

    def __post_init__(self):
        super().__post_init__()
        if not isinstance(self.bounds, Bounds):
            try:
                self.bounds = Bounds(**self.bounds)
            except TypeError:
                self.bounds = Bounds(
                    self.bounds[0], self.bounds[1], self.bounds[2])
