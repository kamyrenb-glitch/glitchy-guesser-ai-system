# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

<!-- Describe the goal you asked the agent to accomplish -->

**What did the agent do?**

<!-- List the steps the agent took (files edited, commands run, etc.) -->

**What did you have to verify or fix manually?**

<!-- Describe anything the agent got wrong or that required human review -->

---

## Test Generation (SF7)

> Document how you used AI to help generate or improve tests.

| Edge Case | Prompt Used | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------|-------------------|--------------|----------------|
| | | | | |
| | | | | |
| | | | | |

---

## Linting & Style (SF9)

> Document your use of AI for linting or code style improvements.

**Prompt used:**

```
<!-- Paste the prompt you gave the AI -->
```

**Linting output before:**

```
<!-- Paste relevant linter warnings/errors -->
```

**Changes applied:**

<!-- Describe what you changed based on the AI's suggestions -->

---

## Model Comparison (SF11)

> Compare two AI models on the same task.

**Task given to both models:**

<!-- Describe what you asked each model to do -->

| | Model A | Model B |
|-|---------|---------|
| **Model name** | | |
| **Response summary** | | |
| **More Pythonic?** | | |
| **Clearer explanation?** | | |

**Which did you prefer and why?**

<!-- Your conclusion -->

## Applied AI System — Agent and Evaluation Evidence

### Agentic Workflow Enhancement

`GuesserBot` follows a multi-step decision chain:

1. **Observe** only “Too High,” “Too Low,” or “Win.”
2. **Narrow** its known range based on that outcome.
3. **Plan** the midpoint of the current range.
4. **Act** by submitting a guess that is validated against the current range and turn limit.
5. **Record** the turn, prior range, guess, reason, outcome, and updated range.

The secret remains in the game or evaluation layer and is never passed into the bot. To produce the following reproducible trace, I ran the public bot methods (`observe` and `plan_guess`) together with the game-logic `check_guess` method for Normal difficulty. Secret 37 was known only to the evaluation harness; the bot received only outcome feedback.

| Turn | Range Before | Planned Guess | Reason | Outcome | Range After |
|---:|---|---:|---|---|---|
| 1 | (1, 100) | 50 | midpoint of narrowed range | Too High | (1, 49) |
| 2 | (1, 49) | 25 | midpoint of narrowed range | Too Low | (26, 49) |
| 3 | (26, 49) | 37 | midpoint of narrowed range | Win | (26, 49) |

### Test Harness and Evaluation Script

`evaluate_bot.py` is the stretch test harness. It evaluates every possible secret in each difficulty range rather than relying on a small sample. Run it with:

```text
python evaluate_bot.py
```

| Difficulty | Secrets | Win Rate | Average Turns | Worst-Case Turns | Violations |
|---|---:|---:|---:|---:|---:|
| Easy | 20 | 100% | 3.70 | 5 | 0 |
| Normal | 100 | 100% | 5.80 | 7 | 0 |
| Hard | 200 | 100% | 6.76 | 8 | 0 |

The harness checks whether the bot solves each secret within its turn limit, validates the guesses and decision-log state, and counts guardrail violations. Since it uses the same deterministic loop for every secret, the results are repeatable.

### Human Review of AI-Assisted Development

I used Claude to inspect the original project and propose an implementation plan. I used GitHub Copilot to implement and revise the agent, tests, evaluation script, documentation, and architecture diagram.

I accepted the outcome-only binary-search design because it is transparent, testable, reproducible, usable offline, and consistent with data minimization and least privilege. I rejected the suggestion to leave the secret in the player-facing Developer Debug Info panel. Even though the bot could not see that panel, a player could use the displayed secret to cheat, undermining fairness, trust, and the validity of the evaluation.

I manually tested invalid input, valid turns, logs, secret isolation, reset behavior, and UI readability. These checks kept human judgment involved in reviewing both the system behavior and AI-assisted recommendations.
