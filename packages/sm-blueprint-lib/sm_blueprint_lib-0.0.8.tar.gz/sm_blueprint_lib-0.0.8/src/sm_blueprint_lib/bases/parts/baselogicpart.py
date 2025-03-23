from dataclasses import dataclass, field

from .baseinteractablepart import BaseInteractablePart
from ..controllers.baselogiccontroller import BaseLogicController


@dataclass
class BaseLogicPart(BaseInteractablePart):
    """Base class for Logic parts with active state (mostly Logic Gate and Timer)
    """
    controller: BaseLogicController = field(default_factory=BaseLogicController)
    xaxis: int = field(kw_only=True, default=1)
    zaxis: int = field(kw_only=True, default=-2)