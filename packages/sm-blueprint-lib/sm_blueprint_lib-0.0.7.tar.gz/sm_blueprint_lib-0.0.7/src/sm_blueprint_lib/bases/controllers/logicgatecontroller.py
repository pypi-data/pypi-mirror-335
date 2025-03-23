from dataclasses import dataclass, field

from .baselogiccontroller import BaseLogicController


@dataclass
class LogicGateController(BaseLogicController):
    """Logic Gate's Controller
    """
    mode: int = 0
