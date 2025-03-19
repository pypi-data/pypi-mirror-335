from enum import Enum


class Action(Enum):
    """
    An enumeration to provide action values. The action represents how the snek
    should accelerate. The bearing of the snek is the current speed, and an action
    will be applied to the current bearing.
    """

    MAINTAIN = "maintain"
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
