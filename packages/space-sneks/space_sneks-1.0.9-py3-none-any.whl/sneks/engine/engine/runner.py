from collections import deque

from sneks.engine.config.instantiation import config
from sneks.engine.engine.mover import NormalizedScore
from sneks.engine.engine.state import State


def demo() -> None:
    config.graphics.display = True
    # config.game.rows = 360
    # config.game.columns = 540
    # config.graphics.cell_size = 2
    config.graphics.step_delay = 40
    config.runs = 100
    config.turn_limit = 10000
    config.registrar_submission_sneks = 20

    main()


def main() -> list[NormalizedScore] | None:
    pr = None

    if config.profile:
        import cProfile

        pr = cProfile.Profile()
        pr.enable()

    result = main2()

    if config.profile:
        pr.disable()
        import pstats

        stats = pstats.Stats(pr)
        stats.sort_stats("tottime").print_stats(20)

    return result


def main2() -> list[NormalizedScore] | None:
    runs = 0
    state = State()
    state.reset()
    if config.graphics.display:
        from sneks.engine.gui.graphics import Painter
        from sneks.engine.gui.recorder import Recorder

        recorder = None
        if config.graphics.record:
            recorder = Recorder()
        painter = Painter(recorder=recorder)
        painter.initialize()
        ended_frames = deque(maxlen=10)
        while runs < config.runs:
            painter.clear()
            painter.draw_boarders()
            painter.draw_stars()
            ended_frames.appendleft(state.ended_snakes)
            for i, ended in enumerate(ended_frames):
                for head in ended:
                    painter.draw_ended_head(head, splash=i)
            state.ended_snakes = []
            for snake in state.snakes:
                painter.draw_snake(
                    snake.collision_tail[0], snake.visible_tail, True, snake.color
                )
            for asteroid in state.asteroids:
                painter.draw_asteroid(asteroid=asteroid)
            painter.draw()
            if state.should_continue(config.turn_limit):
                state.step()
            else:
                print(f"Run complete: {runs}")
                if recorder is not None:
                    recorder.animate_game()
                    recorder.reset()
                normalized = state.report()
                for s in normalized:
                    print(f"{s.total():.4f} {s}")
                painter.end_delay()
                runs += 1
                state.reset()
        return None
    else:
        scores = []
        while runs < config.runs:
            if state.should_continue(config.turn_limit):
                state.step()
            else:
                normalized = state.report()
                for s in normalized:
                    print(f"{s.total():.4f} {s}")
                scores += normalized
                state.reset()
                runs += 1
                if runs % (config.runs / 20) == 0:
                    print(f"{100 * runs / config.runs}% complete")
        return scores


if __name__ == "__main__":
    main()
