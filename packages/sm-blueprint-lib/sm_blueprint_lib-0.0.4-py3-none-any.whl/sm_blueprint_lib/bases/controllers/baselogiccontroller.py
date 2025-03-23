from dataclasses import dataclass, field

from sm_blueprint_lib.bases.controllers.basecontroller import BaseController


@dataclass
class BaseLogicController(BaseController):
    """Base class for Logic parts' Controllers (mostly Logic Gate and Timer)
    """
    active: bool = field(kw_only=True, default=False)
