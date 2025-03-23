from dataclasses import dataclass, field

from ..bases.controllers.sensorcontroller import SensorController
from ..bases.parts.baseinteractablepart import BaseInteractablePart
from ..constants import SHAPEID


@dataclass
class Sensor5(BaseInteractablePart):
    controller: SensorController = field(
        default_factory=SensorController)
    shapeId: str = field(kw_only=True, default=SHAPEID.SENSOR5)

    def __post_init__(self):
        super().__post_init__()
        # Can specify sensor controller as a dict, a tuple (audioEnable, buttonMode, color, colorMode, range) or just the parameter mode
        if not isinstance(self.controller, SensorController):
            try:
                self.controller = SensorController(**self.controller)
            except TypeError:
                try:
                    self.controller = SensorController(*self.controller)
                except TypeError:
                    self.controller = SensorController(self.controller)
