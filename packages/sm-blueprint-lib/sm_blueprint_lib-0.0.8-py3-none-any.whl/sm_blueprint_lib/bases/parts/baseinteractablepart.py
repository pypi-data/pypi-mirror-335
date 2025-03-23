from dataclasses import dataclass, field

from ..controllers.basecontroller import BaseController
from .basepart import BasePart
from ...id import ID


@dataclass
class BaseInteractablePart(BasePart):
    """Base class for Interactable parts
    """
    controller: BaseController = field(default_factory=BaseController)

    def connect(self, o: "BaseInteractablePart"):
        if not self.controller.controllers:
            self.controller.controllers = []
            
        self.controller.controllers.append(ID(o.controller.id))
        return o
