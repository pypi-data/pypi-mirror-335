from dataclasses import dataclass


@dataclass
class Bearing:
    """
    Represents the directional speeds of a snek. The speeds are represented
    as integers to show the vertical and horizontal speeds in cells per
    game tick.

    Sneks start with a bearing of ``(0, 0)``. For example, if the action from
    ``get_next_action()`` is ``Action.UP``, the snek will increase the speed vertically
    by one, so on the next game step the bearing will be ``(0, 1)``, and the snek will
    have moved one cell.
    """

    x: int  #:
    y: int  #:
