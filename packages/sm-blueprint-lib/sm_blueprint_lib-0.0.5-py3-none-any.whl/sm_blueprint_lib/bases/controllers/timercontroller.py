from dataclasses import dataclass, field

from bases.controllers.baselogiccontroller import BaseLogicController


@dataclass
class TimerController(BaseLogicController):
    """Timer's Controller
    """
    seconds: int
    ticks: int
