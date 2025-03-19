from collections.abc import Generator

from sneks.engine.config.instantiation import config
from sneks.engine.core.action import Action
from sneks.engine.core.cell import Cell
from sneks.engine.core.direction import Direction


class Velocity:
    x: int
    y: int

    def __init__(self):
        self.x = 0
        self.y = 0

    def add(self, action: Action) -> None:
        match action:
            case Action.UP:
                self.y = min(config.game.directional_speed_limit, self.y + 1)
            case Action.RIGHT:
                self.x = min(config.game.directional_speed_limit, self.x + 1)
            case Action.DOWN:
                self.y = max(-config.game.directional_speed_limit, self.y - 1)
            case Action.LEFT:
                self.x = max(-config.game.directional_speed_limit, self.x - 1)

    def get_distance(self) -> float:
        return Cell(0, 0).get_distance(Cell(self.x, self.y))

    def get_direction_components(self) -> Generator[Direction, None, None]:
        """
        Orders the directional components to make a path for the velocity
        """

        options = []
        if self.y > 0:
            options.append(Direction.UP)
        elif self.y < 0:
            options.append(Direction.DOWN)
        if self.x > 0:
            options.append(Direction.RIGHT)
        elif self.x < 0:
            options.append(Direction.LEFT)

        origin = Cell(0, 0)
        target = Cell(self.x, self.y)
        while origin != target:
            component = min(
                options,
                key=lambda direction: origin.get_neighbor(direction).get_distance(
                    target
                ),
            )
            origin = origin.get_neighbor(component)
            yield component
