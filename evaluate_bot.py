"""Exhaustively evaluate the GuesserBot on every secret in each difficulty."""

from __future__ import annotations

import inspect

from bot_agent import GuesserBot, LOG_FIELDS
from logic_utils import (
    DIFFICULTY_SETTINGS,
    check_guess,
)


def evaluate_difficulty(difficulty: str) -> dict[str, int | float]:
    settings = DIFFICULTY_SETTINGS[difficulty]
    low, high = settings["range"]
    max_turns = settings["attempts"]
    turns_by_secret = []
    wins = 0
    violations = 0

    for secret in range(low, high + 1):
        bot = GuesserBot(low, high, max_turns)
        if hasattr(bot, "secret") or "secret" in inspect.signature(GuesserBot).parameters:
            violations += 1

        while not bot.solved and bot.turn < max_turns:
            bot.observe(None)
            range_before = (bot.low, bot.high)
            guess = bot.plan_guess()
            if (
                type(guess) is not int
                or not range_before[0] <= guess <= range_before[1]
                or bot.turn > max_turns
            ):
                violations += 1
                break

            outcome = check_guess(guess, secret)
            bot.observe(outcome)
            entry = bot.decision_log[-1]
            if (
                set(entry) != set(LOG_FIELDS)
                or entry["range_before"] != range_before
                or entry["guess"] != guess
                or entry["outcome"] != outcome
                or entry["range_after"] != (bot.low, bot.high)
            ):
                violations += 1

        turns_by_secret.append(bot.turn)
        if bot.solved:
            wins += 1
        else:
            violations += 1

    sample_count = high - low + 1
    return {
        "secrets": sample_count,
        "wins": wins,
        "win_rate": wins / sample_count,
        "average_turns": sum(turns_by_secret) / sample_count,
        "worst_case_turns": max(turns_by_secret),
        "guardrail_violations": violations,
    }


def main() -> None:
    print(
        "Difficulty | Secrets | Win rate | Average turns | "
        "Worst-case turns | Guardrail violations"
    )
    for difficulty in DIFFICULTY_SETTINGS:
        result = evaluate_difficulty(difficulty)
        print(
            f"{difficulty} | {result['secrets']} | "
            f"{result['win_rate']:.2%} | {result['average_turns']:.2f} | "
            f"{result['worst_case_turns']} | {result['guardrail_violations']}"
        )


if __name__ == "__main__":
    main()
