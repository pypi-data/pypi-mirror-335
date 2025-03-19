import hashlib
import itertools
import math
import os
import random
import struct
import sys
from functools import lru_cache

from sneks.engine.config.definition import Colors
from sneks.engine.core.cell import Cell
from sneks.engine.engine import cells
from sneks.engine.engine.cells import get_relative_to
from sneks.engine.engine.mover import AsteroidMover

try:
    import pygame
    from pygame import Surface
except ModuleNotFoundError:
    pygame = object  # type: ignore
    Surface = object  # type: ignore

from sneks.engine.config.instantiation import config
from sneks.engine.gui.recorder import Recorder

assert config.graphics is not None

ROWS = config.game.rows
COLUMNS = config.game.columns
CELL_SIZE = config.graphics.cell_size
PADDING = config.graphics.padding
COLOR_BORDER = config.graphics.colors.border
COLOR_BACKGROUND = config.graphics.colors.background
COLOR_INVALID = config.graphics.colors.invalid

HEIGHT = (2 + ROWS) * CELL_SIZE + ROWS * PADDING
WIDTH = (2 + COLUMNS) * CELL_SIZE + COLUMNS * PADDING


class Painter:
    screen: Surface | None = None

    def __init__(self, recorder: Recorder | None = None):
        self.recorder = recorder

    def initialize(self):
        if config.graphics.headless:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Sneks in SPACE")

    @staticmethod
    def get_rect(surface: pygame.Surface, cell: Cell) -> pygame.Rect:
        return surface.get_rect(
            top=CELL_SIZE
            + PADDING
            + (config.game.rows - cell.y - 1) * (CELL_SIZE + PADDING),
            left=CELL_SIZE + PADDING + cell.x * (CELL_SIZE + PADDING),
        )

    def draw_snake(self, head: Cell, cells, alive: bool, color: tuple[int, int, int]):
        assert self.screen is not None
        surface = pygame.Surface((CELL_SIZE - PADDING, CELL_SIZE - PADDING))
        fill_horizontal = pygame.Surface((PADDING * 2, CELL_SIZE - PADDING))
        fill_vertical = pygame.Surface((CELL_SIZE - PADDING, PADDING * 2))
        surface.fill(color)
        fill_horizontal.fill(color)
        fill_vertical.fill(color)
        previous: Cell | None = None
        previous_color: tuple[int, ...] = color
        for cell in cells:
            surface.fill(previous_color)
            fill_horizontal.fill(previous_color)
            fill_vertical.fill(previous_color)
            rect = self.get_rect(surface=surface, cell=cell)
            self.screen.blit(surface, rect)
            if previous is not None:
                # This is super verbose and can be refactored
                looped = abs(cell.x - previous.x) + abs(cell.y - previous.y) > 1

                relative = get_relative_to(cell, previous)
                dx = min(1, max(relative.x, -1))
                dy = min(1, max(relative.y, -1))
                if looped:
                    dx *= -1
                    dy *= -1
                match (dx, dy):
                    case (1, 0):
                        # fill the padding to the left
                        top = (
                            CELL_SIZE
                            + (config.game.rows - cell.y - 1) * (CELL_SIZE + PADDING)
                            + PADDING
                        )
                        left = CELL_SIZE + cell.x * (CELL_SIZE + PADDING) - PADDING
                        rect = fill_horizontal.get_rect(top=top, left=left)
                        self.screen.blit(fill_horizontal, rect)
                        if looped:
                            # fill the padding to the right of the previous
                            top = (
                                CELL_SIZE
                                + (config.game.rows - cell.y - 1)
                                * (CELL_SIZE + PADDING)
                                + PADDING
                            )
                            left = (
                                CELL_SIZE
                                + (previous.x + 1) * (CELL_SIZE + PADDING)
                                - PADDING
                            )
                            rect = fill_horizontal.get_rect(top=top, left=left)
                            self.screen.blit(fill_horizontal, rect)
                    case (-1, 0):
                        # fill the padding to the right
                        top = (
                            CELL_SIZE
                            + (config.game.rows - cell.y - 1) * (CELL_SIZE + PADDING)
                            + PADDING
                        )
                        left = CELL_SIZE + previous.x * (CELL_SIZE + PADDING) - PADDING
                        rect = fill_horizontal.get_rect(top=top, left=left)
                        self.screen.blit(fill_horizontal, rect)
                        if looped:
                            # fill the padding to the right of the current
                            top = (
                                CELL_SIZE
                                + (config.game.rows - cell.y - 1)
                                * (CELL_SIZE + PADDING)
                                + PADDING
                            )
                            left = (
                                CELL_SIZE
                                + (cell.x + 1) * (CELL_SIZE + PADDING)
                                - PADDING
                            )
                            rect = fill_horizontal.get_rect(top=top, left=left)
                            self.screen.blit(fill_horizontal, rect)
                    case (0, 1):
                        # fill the padding below
                        top = (
                            CELL_SIZE
                            + (config.game.rows - previous.y - 1)
                            * (CELL_SIZE + PADDING)
                            - PADDING
                        )
                        left = CELL_SIZE + cell.x * (CELL_SIZE + PADDING) + PADDING
                        rect = fill_vertical.get_rect(top=top, left=left)
                        self.screen.blit(fill_vertical, rect)
                        if looped:
                            # fill the padding to the below the current
                            top = (
                                CELL_SIZE
                                + (config.game.rows - cell.y) * (CELL_SIZE + PADDING)
                                - PADDING
                            )
                            left = CELL_SIZE + cell.x * (CELL_SIZE + PADDING) + PADDING
                            rect = fill_vertical.get_rect(top=top, left=left)
                            self.screen.blit(fill_vertical, rect)
                    case (0, -1):
                        # fill the padding above
                        top = (
                            CELL_SIZE
                            + (config.game.rows - cell.y - 1) * (CELL_SIZE + PADDING)
                            - PADDING
                        )
                        left = CELL_SIZE + cell.x * (CELL_SIZE + PADDING) + PADDING
                        rect = fill_vertical.get_rect(top=top, left=left)
                        self.screen.blit(fill_vertical, rect)
                        if looped:
                            # fill the padding to the below the previous
                            top = (
                                CELL_SIZE
                                + (config.game.rows - previous.y)
                                * (CELL_SIZE + PADDING)
                                - PADDING
                            )
                            left = CELL_SIZE + cell.x * (CELL_SIZE + PADDING) + PADDING
                            rect = fill_vertical.get_rect(top=top, left=left)
                            self.screen.blit(fill_vertical, rect)
            previous = cell
            previous_color = tuple(int(c * 0.9) for c in previous_color)
        if alive:
            surface.fill(
                struct.unpack(
                    "BBB", hashlib.md5(struct.pack("BBB", *color)).digest()[-3:]
                )
            )
            rect = self.get_rect(surface=surface, cell=head)
            self.screen.blit(surface, rect)

    def draw_asteroid(self, asteroid: AsteroidMover) -> None:
        assert self.screen is not None
        surface = pygame.Surface((CELL_SIZE + PADDING, CELL_SIZE + PADDING))

        # To show the asteroid tails

        # surface.fill(Colors.invalid)
        # for cell in asteroid.collision_tail:
        #     rect = surface.get_rect(
        #         top=CELL_SIZE + (config.game.rows - cell.y - 1) * (CELL_SIZE + PADDING),
        #         left=CELL_SIZE + cell.x * (CELL_SIZE + PADDING),
        #     )
        #     self.screen.blit(surface, rect)

        surface.fill(Colors.asteroid)
        for i in range(asteroid.size):
            cell = asteroid.collision_tail[i]
            rect = surface.get_rect(
                top=CELL_SIZE + (config.game.rows - cell.y - 1) * (CELL_SIZE + PADDING),
                left=CELL_SIZE + cell.x * (CELL_SIZE + PADDING),
            )
            self.screen.blit(surface, rect)

    def draw_ended_head(self, head: Cell, splash: int):
        assert self.screen is not None
        surface = pygame.Surface((CELL_SIZE - PADDING, CELL_SIZE - PADDING))

        surface.fill(COLOR_INVALID)
        rect = self.get_rect(surface=surface, cell=head)
        self.screen.blit(surface, rect)

        surface.fill(tuple(int((0.85**splash) * c) for c in COLOR_INVALID))

        splash_cells = [
            cells.get_absolute_by_offset(cell=head, x_offset=x, y_offset=y)
            for x, y in itertools.product(
                range(-int(splash / 2), int(splash / 2)), repeat=2
            )
        ]
        for c in splash_cells:
            rect = self.get_rect(surface=surface, cell=c)
            self.screen.blit(surface, rect)

    def clear(self):
        self.screen.fill(COLOR_BACKGROUND)

    def draw_boarders(self):
        top = (0, 0, WIDTH, CELL_SIZE - PADDING)
        bottom = (0, HEIGHT - CELL_SIZE + PADDING, WIDTH, HEIGHT)
        left = (0, CELL_SIZE - PADDING, CELL_SIZE - PADDING, HEIGHT)
        right = (WIDTH - CELL_SIZE + PADDING, 0, WIDTH, HEIGHT)

        for rect in (top, bottom, left, right):
            pygame.draw.rect(self.screen, COLOR_BORDER, rect)

    @lru_cache
    def get_stars(self) -> list[tuple[int, int]]:
        return [
            (
                random.randint(CELL_SIZE + PADDING, WIDTH - CELL_SIZE - PADDING),
                random.randint(CELL_SIZE + PADDING, HEIGHT - CELL_SIZE - PADDING),
            )
            for _ in range(ROWS + COLUMNS)
        ]

    def draw_stars(self):
        for center in self.get_stars():
            modifier = math.prod(center) % (256 - max(COLOR_BACKGROUND))
            pygame.draw.circle(
                surface=self.screen,
                color=tuple(modifier + c for c in COLOR_BACKGROUND),
                center=center,
                radius=1.0,
            )

    def draw(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        pygame.display.flip()
        if self.recorder:
            self.recorder.record_frame(self.screen)
        self.step_delay()

    def step_delay(self):
        if not config.graphics.headless:
            if config.graphics.step_keypress_wait:
                self.wait_for_keypress()
            pygame.time.delay(config.graphics.step_delay)

    def end_delay(self):
        if not config.graphics.headless:
            if config.graphics.end_keypress_wait:
                self.wait_for_keypress()
            pygame.time.delay(config.graphics.end_delay)

    @staticmethod
    def wait_for_keypress():
        while True:
            # allow the key to be held instead of waiting for each step
            if any(pygame.key.get_pressed()):
                break
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                break
