from dataclasses import dataclass, field

from sm_blueprint_lib.bases.controllers.baselogiccontroller import BaseLogicController


@dataclass
class LogicGateController(BaseLogicController):
    """Logic Gate's Controller
    """
    mode: int = 0
