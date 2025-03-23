class SHAPEID:
    BARRIER_BLOCK = "09ca2713-28ee-4119-9622-e85490034758"
    LOGIC_GATE = "9f0f56e8-2c31-4d83-996c-d00a9b296c3f"
    TIMER = "8f7fd0e7-c46e-4944-a414-7ce2437bb30f"
    SENSOR5 = "20dcd41c-0a11-4668-9b00-97f278ce21af"
    SWITCH = "7cf717d7-d167-4f2d-a6e7-6b2c70aa3986"
    SHAPEID_TO_CLASS = {}


class AXIS:
    DEFAULT_XAXIS = 1
    DEFAULT_ZAXIS = 3


class VERSION:
    BLUEPRINT_VERSION = 4


TICKS_PER_SECOND = 40

__global_id_counter = 0
"""Atempting to modify this global variable may cause to break your blueprints lol.
"""


def get_new_id():
    global __global_id_counter
    __global_id_counter = (new_id := __global_id_counter) + 1
    return new_id
