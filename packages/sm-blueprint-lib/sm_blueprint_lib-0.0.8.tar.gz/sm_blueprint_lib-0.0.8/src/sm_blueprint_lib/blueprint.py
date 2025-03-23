from dataclasses import dataclass, field

from .bases.parts.basepart import BasePart
from .body import Body
from .constants import VERSION


@dataclass
class Blueprint:
    bodies: list[Body] = field(default_factory=lambda: [Body()])
    version: int = VERSION.BLUEPRINT_VERSION

    def __post_init__(self):
        try:
            self.bodies = [Body(**body) for body in self.bodies]
        except TypeError:
            pass

    def add(self, *obj, body=0):
        """Adds the object(s) to the blueprint.

        Args:
            obj (Any): Can be a instance of BasePart or a subclass. It also can be any nested iterable of instances (list of parts, list of lists of parts, etc).
            body (int, optional): Specify in which blueprint's body the object will be placed. Defaults to 0.
        """
        for subobj in obj:
            if isinstance(subobj, BasePart):
                self.bodies[body].childs.append(subobj)
            else:
                for subsubobj in subobj:
                    self.add(subsubobj, body=body)
