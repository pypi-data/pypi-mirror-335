from dataclasses import dataclass, field
from typing import Any, Optional

from sm_blueprint_lib.constants import get_new_id
from sm_blueprint_lib.id import ID


@dataclass
class BaseController:
    """Base class for controller objects (used in interactable parts and so)
    """
    controllers: Optional[list[ID]] = field(kw_only=True, default=None)
    id: int = field(kw_only=True, default_factory=get_new_id)
    joints: Optional[list[ID]] = field(kw_only=True, default=None)

    def __post_init__(self):
        try:
            self.controllers = [ID(**c) for c in self.controllers]
        except TypeError:
            pass