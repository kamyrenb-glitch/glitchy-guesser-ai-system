import inspect

import pytest

from bot_agent import BotStateError, GuesserBot, LOG_FIELDS
from logic_utils import check_guess, parse_guess


def test_binary_search_finds_every_secret(game_settings):
    _difficulty, (low, high), max_turns = game_settings

    for secret in range(low, high + 1):
        bot = GuesserBot(low, high, max_turns)
        bot.observe(None)

        while not bot.solved:
            range_before = (bot.low, bot.high)
            guess = bot.plan_guess()
            assert type(guess) is int
            assert range_before[0] <= guess <= range_before[1]

            outcome = check_guess(guess, secret)
            bot.observe(outcome)

        assert bot.turn <= max_turns
        assert len(bot.decision_log) == bot.turn
        assert bot.decision_log[-1]["outcome"] == "Win"
        assert all(set(entry) == set(LOG_FIELDS) for entry in bot.decision_log)


def test_bot_observes_feedback_and_narrows_its_range():
    bot = GuesserBot(1, 10, 4)
    bot.observe(None)
    assert bot.plan_guess() == 5

    bot.observe("Too Low")

    assert (bot.low, bot.high) == (6, 10)
    assert bot.decision_log == [
        {
            "turn": 1,
            "range_before": (1, 10),
            "guess": 5,
            "reason": "midpoint of narrowed range",
            "outcome": "Too Low",
            "range_after": (6, 10),
        }
    ]


def test_contradictory_feedback_is_rejected():
    bot = GuesserBot(1, 3, 3)
    guess = bot.plan_guess()
    bot.observe("Too Low")
    assert guess == 2
    assert bot.plan_guess() == 3

    with pytest.raises(BotStateError, match="contradictory"):
        bot.observe("Too Low")


def test_bot_enforces_maximum_turns():
    bot = GuesserBot(1, 2, 1)
    assert bot.plan_guess() == 1
    bot.observe("Too Low")

    with pytest.raises(BotStateError, match="maximum turn limit"):
        bot.plan_guess()


@pytest.mark.parametrize(
    ("raw", "expected_error"),
    [
        ("12.5", "whole number"),
        ("not a number", "whole number"),
        ("21", "between 1 and 20"),
        (None, "Enter a guess"),
    ],
)
def test_player_guess_validation_rejects_invalid_values(raw, expected_error):
    valid, guess, error = parse_guess(raw, 1, 20)

    assert not valid
    assert guess is None
    assert expected_error in error


def test_invalid_feedback_and_invalid_range_are_rejected():
    bot = GuesserBot(1, 10, 4)
    bot.plan_guess()

    with pytest.raises(BotStateError, match="invalid outcome"):
        bot.observe("secret is 5")
    with pytest.raises(BotStateError, match="valid integer game range"):
        GuesserBot(True, 10, 4)


def test_corrupt_decision_log_is_reported_as_invalid_state():
    bot = GuesserBot(1, 10, 4)
    bot.plan_guess()
    bot.observe("Too Low")
    bot.decision_log[0]["range_after"] = (1, 10)

    with pytest.raises(BotStateError, match="contradictory"):
        bot.validate_state()


def test_incomplete_bot_state_is_reported_readably():
    bot = GuesserBot(1, 10, 4)
    del bot.low

    with pytest.raises(BotStateError, match="incomplete"):
        bot.validate_state()


def test_bot_api_and_decision_log_do_not_expose_a_secret():
    bot = GuesserBot(1, 10, 4)

    assert not hasattr(bot, "secret")
    assert "secret" not in inspect.signature(GuesserBot).parameters
    assert "secret" not in inspect.signature(bot.observe).parameters
    assert "secret" not in inspect.signature(bot.plan_guess).parameters
