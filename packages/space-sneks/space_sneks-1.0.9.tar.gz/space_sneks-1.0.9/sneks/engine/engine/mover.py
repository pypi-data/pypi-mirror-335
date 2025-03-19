import abc
import contextlib
import itertools
import os
from collections import deque
from dataclasses import InitVar, dataclass, field

from sneks.engine.config.instantiation import config
from sneks.engine.core.cell import Cell
from sneks.engine.engine.cells import get_absolute_neighbor
from sneks.engine.engine.velocity import Velocity
from sneks.engine.interface.snek import Snek


@dataclass(frozen=True)
class NormalizedScore:
    crashes: float
    distance: float
    raw: "Score"

    def total(self) -> float:
        return self.crashes + self.distance

    def __repr__(self):
        return (
            f"crashes': {self.crashes:.4f}, distance': {self.distance:.4f} "
            f"crashes: {self.raw.crashes:2d}, distance: {self.raw.distance:.2f} "
            f"name: {self.raw.name}"
        )


@dataclass(frozen=True)
class Score:
    name: str
    crashes: int
    distance: float

    def normalize(self, min_score: "Score", max_score: "Score") -> NormalizedScore:
        return NormalizedScore(
            crashes=(min_score.crashes - self.crashes)
            / max(1, (min_score.crashes - max_score.crashes)),
            distance=(self.distance - min_score.distance)
            / max(1.0, (max_score.distance - min_score.distance)),
            raw=self,
        )


@dataclass
class BaseMover(abc.ABC):
    name: str
    color: tuple[int, int, int]
    size: int
    velocity: Velocity = field(default_factory=Velocity, init=False)
    collision_tail: deque[Cell] = field(default_factory=deque, init=False)
    visible_tail: deque[Cell] = field(default_factory=deque, init=False)
    distance: float = field(default=0.0, init=False)

    def adjust_velocity(self) -> None:
        raise NotImplementedError

    def move(self) -> None:
        self.adjust_velocity()
        self.distance += self.velocity.get_distance()

        # clear out old collision tail
        while len(self.collision_tail) > self.size:
            self.collision_tail.pop()

        # create a new collision tail with incremental movements
        components = self.velocity.get_direction_components()
        movements = 0
        for direction in components:
            movements += 1
            for cell in list(itertools.islice(self.collision_tail, self.size)):
                self.collision_tail.appendleft(get_absolute_neighbor(cell, direction))
                self.visible_tail.appendleft(get_absolute_neighbor(cell, direction))

        # remove the previous location
        if movements > 0:
            for _ in range(self.size):
                self.collision_tail.pop()

        # trim the visible tail
        while len(self.visible_tail) > max(
            1, 3 * (abs(self.velocity.y) + abs(self.velocity.x))
        ):
            self.visible_tail.pop()


@dataclass
class SnekMover(BaseMover):
    snek: Snek
    head: InitVar[Cell]
    crashes: int = 0

    def __post_init__(self, head: Cell) -> None:
        self.reset(head=head)

    def reset(self, head: Cell) -> None:
        self.collision_tail = deque()
        self.visible_tail = deque()
        self.velocity = Velocity()
        self.collision_tail.append(head)

    def get_head(self) -> Cell:
        return self.collision_tail[0]

    def adjust_velocity(self):
        with contextlib.ExitStack() as stack:
            if not config.debug:
                devnull = open(os.devnull, "w")
                stack.enter_context(devnull)
                stack.enter_context(contextlib.redirect_stdout(devnull))
            next_action = self.snek.get_next_action()
        self.velocity.add(next_action)

    def get_score(self) -> Score:
        return Score(
            name=self.name,
            crashes=self.crashes,
            distance=self.distance,
        )


@dataclass
class AsteroidMover(BaseMover):
    def adjust_velocity(self) -> None:
        pass
