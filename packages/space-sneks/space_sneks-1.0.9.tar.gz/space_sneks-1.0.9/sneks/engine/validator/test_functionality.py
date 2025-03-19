from sneks.engine.config.instantiation import config
from sneks.engine.core.action import Action
from sneks.engine.core.cell import Cell
from sneks.engine.engine import registrar, runner
from sneks.engine.engine.mover import NormalizedScore
from sneks.engine.interface.snek import Snek


def test_basic_functionality() -> None:
    config.registrar_submission_sneks = 1
    submissions = registrar.get_submissions()
    assert len(submissions) == config.registrar_submission_sneks
    snek: Snek = submissions[0].snek
    snek.occupied = frozenset((Cell(1, 1),))
    assert snek.get_next_action() in Action


def test_extended_functionality() -> None:
    assert config.graphics is not None
    config.graphics.display = False
    config.turn_limit = 100
    config.registrar_submission_sneks = 1
    scores = runner.main()
    assert scores is not None
    assert len(scores) == 10
    for score in scores:
        assert isinstance(score, NormalizedScore)
        assert score.crashes == 0
        assert score.distance == 0
        assert score.raw.crashes >= 0
        assert score.raw.distance >= 0


def test_multiple_functionality() -> None:
    assert config.graphics is not None
    config.graphics.display = False
    config.turn_limit = 200
    config.registrar_submission_sneks = 10
    scores = runner.main()
    assert scores is not None
    assert len(scores) == 100
    for score in scores:
        assert isinstance(score, NormalizedScore)
        assert 0 <= score.crashes <= 1
        assert 0 <= score.distance <= 1
        assert score.raw.crashes >= 0
        assert score.raw.distance >= 0
