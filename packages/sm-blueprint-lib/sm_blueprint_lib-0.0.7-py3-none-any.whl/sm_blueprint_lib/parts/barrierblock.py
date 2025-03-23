from dataclasses import dataclass, field

from ..bases.parts.baseboundablepart import BaseBoundablePart
from ..constants import SHAPEID


@dataclass
class BarrierBlock(BaseBoundablePart):
    shapeId: str = field(kw_only=True, default=SHAPEID.BARRIER_BLOCK)
