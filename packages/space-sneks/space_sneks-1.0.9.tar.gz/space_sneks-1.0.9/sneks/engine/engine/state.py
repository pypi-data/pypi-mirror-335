import itertools
import random
from collections import Counter
from operator import methodcaller

from sneks.engine.config.instantiation import config
from sneks.engine.core.bearing import Bearing
from sneks.engine.core.cell import Cell
from sneks.engine.core.direction import Direction
from sneks.engine.engine import cells, registrar
from sneks.engine.engine.mover import AsteroidMover, NormalizedScore, Score, SnekMover


class State:
    def __init__(self):
        self.cells: set[Cell] = {
            Cell(x, y)
            for x, y in itertools.product(
                range(config.game.columns), range(config.game.rows)
            )
        }
        self.snakes: list[SnekMover] = []
        self.ended_snakes: list[Cell] = []
        self.asteroids: list[AsteroidMover] = []
        self.steps: int = 0
        self.occupied: set[Cell] = set()

    def reset(self):
        self.steps = 0
        self.snakes = []
        self.ended_snakes = []
        self.asteroids = []
        self.occupied = set()
        sneks = registrar.get_submissions()
        sneks.sort(key=lambda s: s.name)
        color_index = 0
        color_index_delta = max(len(config.graphics.colors.snake) // len(sneks), 1)
        for snek in sneks:
            self.snakes.append(
                SnekMover(
                    name=snek.name,
                    head=self.get_random_free_cell(),
                    snek=snek.snek,
                    color=config.graphics.colors.snake[color_index],
                    size=1,
                )
            )
            color_index = (color_index + color_index_delta) % len(
                config.graphics.colors.snake
            )
        bearing_options = list(
            range(
                -config.game.asteroid_directional_speed_limit,
                config.game.asteroid_directional_speed_limit + 1,
            )
        )
        for i in range(config.game.asteroid_count):
            up = random.choice(bearing_options)
            right = random.choice(bearing_options)
            if up == 0 and right == 0:
                # ensure all asteroids are moving
                increment = 1 if random.getrandbits(1) else -1
                if random.getrandbits(1):
                    up += increment
                else:
                    right += increment
            cluster_size = random.randint(3, 12)
            asteroid = AsteroidMover(
                name=f"asteroid_{i}",
                color=config.graphics.colors.asteroid,
                size=cluster_size,
            )
            asteroid.collision_tail.extend(
                self.get_random_free_cell(cluster_size=cluster_size)
            )
            asteroid.velocity.x = right
            asteroid.velocity.y = up
            self.asteroids.append(asteroid)
        self.set_board()

    def report(self) -> list[NormalizedScore]:
        scores = [s.get_score() for s in self.snakes]
        min_crashes = min(s.crashes for s in scores)
        max_crashes = max(s.crashes for s in scores)
        min_distance = min(s.distance for s in scores)
        max_distance = max(s.distance for s in scores)

        min_score = Score(name="min", crashes=max_crashes, distance=min_distance)
        max_score = Score(
            name="max",
            crashes=min_crashes,
            distance=max_distance,
        )

        normalized = [
            s.normalize(min_score=min_score, max_score=max_score) for s in scores
        ]
        normalized.sort(key=methodcaller("total"), reverse=True)

        return normalized

    def get_random_free_cell(self, *, cluster_size: int = 1):
        # TODO: split out the logic for building asteroids (i.e. clusters)
        options = self.cells.difference(self.get_occupied_cells())
        if options:
            shuffled = list(options)
            if cluster_size == 1:
                return random.choice(shuffled)
            random.shuffle(shuffled)
            directions = list(Direction)
            for candidate in shuffled:
                potential = set()
                potential.add(candidate)
                while len(potential) < cluster_size:
                    for p in potential:
                        next_candidate = p.get_neighbor(random.choice(directions))
                        if (
                            next_candidate in options
                            and next_candidate not in potential
                        ):
                            potential.add(next_candidate)
                            break
                return list(potential)
            return random.choice(shuffled)
        else:
            return None

    def get_occupied_cells(self) -> frozenset[Cell]:
        occupied = frozenset().union(*(s.collision_tail for s in self.snakes))
        return occupied.union(*(a.collision_tail for a in self.asteroids))

    def set_board(self):
        self.occupied = self.get_occupied_cells()

        for current_snake in self.snakes:
            head = current_snake.get_head()

            # build a grid around the head based on the vision range
            grid = {
                Cell(x, y)
                for x, y in itertools.product(
                    range(
                        head.x - config.game.vision_range,
                        head.x + config.game.vision_range,
                    ),
                    range(
                        head.y - config.game.vision_range,
                        head.y + config.game.vision_range,
                    ),
                )
            }

            # set the snek's occupied to occupied cells within grid
            current_snake.snek.occupied = frozenset(
                cells.get_relative_to(cell, head)
                for cell in grid.intersection(self.occupied)
                if cell.get_distance(head) < config.game.vision_range
            )

            current_snake.snek.bearing = Bearing(
                current_snake.velocity.x, current_snake.velocity.y
            )

    def should_continue(self, turn_limit):
        return self.steps < turn_limit and self.snakes

    def end_snake(self, snake: SnekMover):
        self.ended_snakes.append(snake.get_head())
        snake.crashes += 1
        snake.reset(self.get_random_free_cell())

    def step(self):
        # move the heads
        for snake in self.snakes:
            snake.move()

        for asteroid in self.asteroids:
            asteroid.move()

        occupied = frozenset().union(*(a.collision_tail for a in self.asteroids))
        occupations = Counter()
        for s in self.snakes:
            occupations.update(s.collision_tail)

        to_end = []
        # determine ended snakes
        for snake in self.snakes:
            if occupations[snake.get_head()] > 1:
                # collided with another snake
                to_end.append(snake)
            elif not occupied.isdisjoint(snake.collision_tail):
                # collided with asteroid
                to_end.append(snake)

        for snake in to_end:
            self.end_snake(snake)

        self.set_board()
        self.steps += 1
