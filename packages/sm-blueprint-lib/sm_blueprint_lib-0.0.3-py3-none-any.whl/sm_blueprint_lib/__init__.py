from dataclasses import asdict
from json import load, dump, loads, dumps
from math import ceil, log2

from numpy import ndarray

from sm_blueprint_lib.bases.parts.baseinteractablepart import BaseInteractablePart
from sm_blueprint_lib.blueprint import Blueprint
from sm_blueprint_lib.parts.barrierblock import BarrierBlock
from sm_blueprint_lib.parts.logicgate import LogicGate
from sm_blueprint_lib.parts.timer import Timer
from sm_blueprint_lib.pos import Pos


def load_blueprint(path):
    """Load a blueprint from a path file (normally a blueprint.json).

    Args:
        path (str): The path to the json file.

    Returns:
        Blueprint: The loaded blueprint.
    """
    with open(path) as fp:
        return Blueprint(**load(fp))


def save_blueprint(path, bp: Blueprint):
    """Save a blueprint to a file (normally a blueprint.json).

    Args:
        path (str): The path to save the json file.
        bp (Blueprint): The blueprint to be saved.
    """
    with open(path, mode="w") as fp:
        return dump(asdict(bp), fp, sort_keys=True, separators=(',', ':'))


def load_string(str):
    """Load a blueprint from a json string.

    Args:
        str (str): The string to be loaded.

    Returns:
        Blueprint: The loaded blueprint.
    """
    return Blueprint(**loads(str))


def dump_string(bp: Blueprint):
    """Dump a blueprint into a json-formatted string.

    Args:
        bp (Blueprint): The blueprint to be dumped.

    Returns:
        str: The json-formatted string.
    """
    return dumps(asdict(bp), sort_keys=True, separators=(',', ':'))


def connect(_from, _to, *, parallel=True):
    """Connect interactable parts together, recursively.

    Args:
        _from (Any): Must be an instance of BaseInteractablePart or a subclass.
        Also it can be any nested iterable of instances (list of parts, list of lists of parts, etc).
        _to (Any): Must be an instance of BaseInteractablePart or a subclass.
        Also it can be any nested iterable of instances (list of parts, list of lists of parts, etc).
        parallel (bool, optional): Defines the behaviour of the connections in the following way:

        With parallel=False, everything connects to everything:
            from1 🔀 to1

            from2 🔀 to2

        With parallel=True, every row is connected respectively:
            from1 → to1

            from2 → to2

        Also, if the dimensions does not match it tries to adapt (many to one, one to many, etc)

        Defaults to True.
    """
    if isinstance(_from, BaseInteractablePart) and isinstance(_to, BaseInteractablePart):
        _from.connect(_to)
        return
    if parallel:    # Try connect things row-by-row if possible (one to one, one to many, many to many)
        if not isinstance(_from, BaseInteractablePart) and not isinstance(_to, BaseInteractablePart):   # Assume both are sequence of parts
            for subfrom, subto in zip(_from, _to):
                connect(subfrom, subto, parallel=parallel)
        elif not isinstance(_from, BaseInteractablePart):   # Assume _from is a sequence of parts
            for subfrom in _from:
                connect(subfrom, _to, parallel=parallel)
        else:                                               # Assume _to is a sequence of parts
            for subto in _to:
                connect(_from, subto, parallel=parallel)
    else:           # Just connect everything to everything lol
        if not isinstance(_from, BaseInteractablePart) and not isinstance(_to, BaseInteractablePart):   # Assume both are sequence of parts
            for subfrom in _from:
                for subto in _to:
                    connect(subfrom, subto, parallel=parallel)
        elif not isinstance(_from, BaseInteractablePart):   # Assume _from is a sequence of parts
            for subfrom in _from:
                connect(subfrom, _to, parallel=parallel)
        else:                                               # Assume _to is a sequence of parts
            for subto in _to:
                connect(_from, subto, parallel=parallel)


def check_pos(pos):
    if not isinstance(pos, Pos):
        pos = Pos(*pos)
    return pos


def get_bits_required(number: int | float):
    """Calculates how many bits are required to store this number.

    Args:
        number (int | float): The target number.
    """
    return ceil(log2(number))


def num_to_bit_list(number: int, bit_length: int):
    """Converts a number to a numpy array of its bits.

    Args:
        number (int): The number to convert.
        bit_length (int): The number of bits the list will have.
    """
    output = ndarray(bit_length, dtype=bool)
    for b in range(bit_length):
        output[b] = bool((number >> b) & 1)
    return output
