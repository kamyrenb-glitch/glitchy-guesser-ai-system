"""Outcome-driven binary-search agent for the number guessing game."""

from __future__ import annotations

from typing import Any


LOG_FIELDS = (
    "turn",
    "range_before",
    "guess",
    "reason",
    "outcome",
    "range_after",
)
VALID_OUTCOMES = {"Win", "Too High", "Too Low"}


class BotStateError(ValueError):
    """Raised when the bot receives contradictory feedback or invalid state."""


class GuesserBot:
    """A binary-search agent that only receives its own previous outcome."""

    def __init__(self, low: int, high: int, max_turns: int):
        if type(low) is not int or type(high) is not int or low > high:
            raise BotStateError("The bot needs a valid integer game range.")
        if type(max_turns) is not int or max_turns < 1:
            raise BotStateError("The bot needs a positive integer turn limit.")

        self.initial_low = low
        self.initial_high = high
        self.low = low
        self.high = high
        self.max_turns = max_turns
        self.turn = 0
        self.solved = False
        self.decision_log: list[dict[str, Any]] = []
        self._pending: dict[str, Any] | None = None

    def validate_state(
        self, low: int | None = None, high: int | None = None,
        max_turns: int | None = None,
    ) -> None:
        """Check bot invariants and, when supplied, its owning game's settings."""
        required_attributes = (
            "initial_low",
            "initial_high",
            "low",
            "high",
            "max_turns",
            "turn",
            "solved",
            "decision_log",
            "_pending",
        )
        if any(not hasattr(self, attribute) for attribute in required_attributes):
            raise BotStateError("The bot state is incomplete.")

        if (
            type(self.initial_low) is not int
            or type(self.initial_high) is not int
            or self.initial_low > self.initial_high
            or type(self.low) is not int
            or type(self.high) is not int
            or not self.initial_low <= self.low <= self.high <= self.initial_high
            or type(self.max_turns) is not int
            or self.max_turns < 1
            or type(self.turn) is not int
            or not 0 <= self.turn <= self.max_turns
            or type(self.solved) is not bool
            or not isinstance(self.decision_log, list)
        ):
            raise BotStateError("The bot state is invalid.")

        if (
            (low is not None and low != self.initial_low)
            or (high is not None and high != self.initial_high)
            or (max_turns is not None and max_turns != self.max_turns)
        ):
            raise BotStateError("The bot state does not match the current game.")

        expected_log_count = self.turn - (1 if self._pending is not None else 0)
        if len(self.decision_log) != expected_log_count:
            raise BotStateError("The bot decision history is inconsistent.")
        if self._pending is not None:
            if (
                not isinstance(self._pending, dict)
                or set(self._pending) != {"turn", "range_before", "guess", "reason"}
                or self._pending.get("turn") != self.turn
                or self._pending.get("range_before") != (self.low, self.high)
                or type(self._pending.get("guess")) is not int
                or not self.low <= self._pending["guess"] <= self.high
                or self._pending.get("reason") != "midpoint of narrowed range"
            ):
                raise BotStateError("The bot's pending decision is inconsistent.")

        expected_range = (self.initial_low, self.initial_high)
        last_outcome = None
        for index, entry in enumerate(self.decision_log, start=1):
            if (
                not isinstance(entry, dict)
                or set(entry) != set(LOG_FIELDS)
            ):
                raise BotStateError("The bot decision history is invalid.")

            range_before = entry["range_before"]
            range_after = entry["range_after"]
            if (
                type(entry["turn"]) is not int
                or entry["turn"] != index
                or type(entry["guess"]) is not int
                or entry["reason"] != "midpoint of narrowed range"
                or not isinstance(entry["outcome"], str)
                or entry["outcome"] not in VALID_OUTCOMES
                or not isinstance(range_before, tuple)
                or len(range_before) != 2
                or any(type(value) is not int for value in range_before)
                or not isinstance(range_after, tuple)
                or len(range_after) != 2
                or any(type(value) is not int for value in range_after)
                or range_before != expected_range
                or not range_before[0] <= entry["guess"] <= range_before[1]
            ):
                raise BotStateError("The bot decision history is invalid.")
            next_low, next_high = range_before
            if entry["outcome"] == "Too Low":
                next_low = entry["guess"] + 1
            elif entry["outcome"] == "Too High":
                next_high = entry["guess"] - 1
            if (
                next_low > next_high
                or range_after != (next_low, next_high)
            ):
                raise BotStateError("The bot decision history is contradictory.")
            expected_range = range_after
            last_outcome = entry["outcome"]

        if (
            (self.low, self.high) != expected_range
            or self.solved != (last_outcome == "Win")
        ):
            raise BotStateError("The bot range and decision history disagree.")

        if self.solved and self._pending is not None:
            raise BotStateError("A solved bot cannot have a pending decision.")

    def observe(self, outcome: str | None) -> None:
        """Apply feedback for the pending guess without receiving the secret."""
        self.validate_state()

        if self._pending is None:
            if outcome is not None:
                raise BotStateError("The bot received an outcome without a guess.")
            return
        if not isinstance(outcome, str) or outcome not in VALID_OUTCOMES:
            raise BotStateError("The bot received an invalid outcome.")
        if self.solved:
            raise BotStateError("The bot received feedback after solving the game.")

        guess = self._pending["guess"]
        next_low, next_high = self.low, self.high
        if outcome == "Too Low":
            next_low = guess + 1
        elif outcome == "Too High":
            next_high = guess - 1
        if next_low > next_high:
            raise BotStateError("The bot received contradictory feedback.")

        entry = {
            **self._pending,
            "outcome": outcome,
            "range_after": (next_low, next_high),
        }
        self.low, self.high = next_low, next_high
        self.solved = outcome == "Win"
        self.decision_log.append(entry)
        self._pending = None
        self.validate_state()

    def plan_guess(self) -> int:
        """Plan and return the midpoint of the currently narrowed range."""
        self.validate_state()
        if self.solved:
            raise BotStateError("The bot has already solved the game.")
        if self._pending is not None:
            raise BotStateError("The bot must observe its previous outcome first.")
        if self.turn >= self.max_turns:
            raise BotStateError("The bot has reached its maximum turn limit.")
        if self.low > self.high:
            raise BotStateError("The bot's narrowed range is invalid.")

        self.turn += 1
        guess = (self.low + self.high) // 2
        self._pending = {
            "turn": self.turn,
            "range_before": (self.low, self.high),
            "guess": guess,
            "reason": "midpoint of narrowed range",
        }
        self.validate_state()
        return guess
