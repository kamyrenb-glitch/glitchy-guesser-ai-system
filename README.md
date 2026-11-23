# Game Glitch Investigator

Game Glitch Investigator is a Streamlit number-guessing game where a human competes against a deterministic, outcome-only AI guessing agent. Both try to identify the same secret number, and each valid player guess is followed by one bot turn.

The project emphasizes a transparent agent, explicit input and state guardrails, and decision logs that can be reviewed through the UI. Exhaustive evaluation checks the bot against every possible secret on every difficulty, making its behavior reproducible and its safety claims testable.

## Portfolio

- **GitHub repository:** [kamyrenb-glitch/glitchy-guesser-ai-system](https://github.com/kamyrenb-glitch/glitchy-guesser-ai-system)
- [Architecture diagram](./diagrams/architecture.mmd)
- [Model card](./model_card.md)
- [AI interactions log](./ai_interactions.md)
- [Presentation and demo plan](./presentation.md)

### What This Project Says About Me as an AI Engineer

I do not treat AI as a black box: I design clear information boundaries, validate inputs and state, add guardrails, and make decisions inspectable through logs. I test performance claims rather than assuming a system works, including by checking every possible secret in the supported ranges. I use AI coding tools as collaborators, but I keep human review and final decisions in the process. I also consider whether the experience is usable and fair, whether its behavior is transparent, and what ethical limitations or failure cases remain.

## Project Background

The original Modules 1–3 project, **“Glitchy Guesser,”** was a human number-guessing game with difficulty settings, input validation, directional hints, scoring, attempt limits, and tests. It focused on fixing game-state and feedback behavior while keeping the game logic testable. This version evolves that project with a competitive AI agent, safety guardrails, decision logging, and exhaustive evaluation.

## Architecture

The flow is **player input → Streamlit UI (`app.py`) → input and state guardrails → game engine (`logic_utils.py`) → player feedback and bot turn → UI output**. The secret stays in the game layer; it is never passed to `GuesserBot`. The bot receives only the outcomes **“Too High,” “Too Low,” or “Win,”** then uses that feedback to narrow its range.

The [architecture diagram](./diagrams/architecture.mmd) shows the component and testing flows. Human reviewers can inspect the scores, turns, winner, and bot decision log in the UI. `pytest` exercises the game and agent tests, while `evaluate_bot.py` exhaustively evaluates the bot and checks its guardrails.

## Features

- Three difficulties: Easy (1–20), Normal (1–100), and Hard (1–200).
- Human-versus-bot play, with one bot turn after each valid player guess.
- A binary-search agent loop: observe the outcome, narrow the range, plan the midpoint, and act.
- Five guardrails for valid input, range bounds, turn limits, secret isolation, and invalid state.
- A bot decision log and visible, readable handling of guardrail failures.
- Player and bot scores, turns remaining, hints, winner display, and New Game reset behavior.
- No external API key or network service required to play or evaluate the bot.

## Setup and Running

1. **Clone the repository:**

   ```powershell
   git clone https://github.com/kamyrenb-glitch/glitchy-guesser-ai-system.git
   ```

2. **Enter the project folder:**

   ```powershell
   cd glitchy-guesser-ai-system
   ```

3. **Optionally create and activate a virtual environment** in Windows PowerShell:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. **Install the requirements:**

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. **Start the Streamlit app:**

   ```powershell
   python -m streamlit run app.py
   ```

   Open the local URL printed by Streamlit, typically [http://localhost:8501](http://localhost:8501).

6. **Run the test suite:**

   ```powershell
   python -m pytest
   ```

7. **Run the exhaustive bot evaluation:**

   ```powershell
   python evaluate_bot.py
   ```

## Sample Interactions

| Scenario | Input/Action | Result |
|---|---|---|
| Invalid player input | Enter `hello` | Shows “That is not a whole number.” Neither the player attempt count nor the bot turn count changes. |
| Valid turn on Normal | Enter `25` | Uses one player attempt and triggers exactly one bot turn. The bot starts at midpoint `50` and narrows its range using only the reported outcome. |
| Start a fresh round | Click **New Game** | Resets the round, player and bot scores, turns, winner, player history, and bot decision log. |

## Design Decisions and Trade-offs

The bot is a deterministic binary-search agent rather than an LLM. This makes its guesses reproducible, keeps the game usable offline without API costs, makes its reasoning easy to review, and allows exhaustive testing over every possible secret. The trade-off is less conversational or adaptive behavior than a language-model-based opponent.

`GuesserBot` is isolated in `bot_agent.py` and receives only its range, turn limit, and outcome feedback—not the secret. The game layer checks each bot guess and returns a constrained outcome. This boundary limits what the agent can know and makes the game engine responsible for deciding whether a guess is correct.

The decision log records only `turn`, `range_before`, `guess`, `reason`, `outcome`, and `range_after`. Logging these decisions makes the agent’s range updates and choices reviewable without adding the secret to the log.

## Guardrails

| Guardrail | Behavior |
|---|---|
| Whole-number input | Rejects missing, non-numeric, and non-integer guesses without consuming a turn. |
| Game and narrowed ranges | Keeps player guesses inside the selected game range and bot guesses inside its current narrowed range. |
| Maximum turns | Enforces each difficulty’s attempt limit for the player and bot. |
| Secret isolation | Keeps the secret in the game layer; the bot receives only “Too High,” “Too Low,” or “Win,” and the decision log has no secret field. |
| Invalid or contradictory state | Detects invalid bot/game state, safely starts a new game, and displays a readable error. |

## Testing and Evaluation

### Reliability Summary

- **Automated tests:** 18 of 18 passed with `python -m pytest`.
- **Exhaustive evaluation:** all 320 possible secrets were tested across Easy, Normal, and Hard.
- **Bot performance:** a 100% win rate within each difficulty's turn limit.
- **Guardrails:** zero violations were recorded.
- **Human evaluation:** five of five manual checks passed.
- **Plain pytest:** the original import-path failure was fixed with `conftest.py`.

### Exhaustive Evaluation Results

| Difficulty | Secrets tested | Win rate | Average turns | Worst-case turns | Guardrail violations |
|---|---:|---:|---:|---:|---:|
| Easy | 20 | 100% | 3.70 | 5 | 0 |
| Normal | 100 | 100% | 5.80 | 7 | 0 |
| Hard | 200 | 100% | 6.76 | 8 | 0 |

### Human Evaluation

| Test | Input or Action | Evaluation Criteria | Observed Result | Status |
|---|---|---|---|---|
| Invalid input | Enter `hello` and submit. | Reject non-numeric input without consuming a player attempt or bot turn. | The UI displayed “That is not a whole number.” Attempts remained at 8 and bot turns remained at 0. | Pass |
| Valid competitive turn | Enter `25` on Normal difficulty. | Use one player attempt and trigger exactly one bot turn. | Attempts changed from 8 to 7 and bot turns changed from 0 to 1. The bot began with midpoint guess 50. | Pass |
| Outcome-only bot log | Open the Bot Decision Log after the valid turn. | Record the bot's reasoning and outcome without exposing the secret. | The log recorded turn, range before, guess 50, midpoint reason, outcome, and range after. It contained no secret field. | Pass |
| Player-facing debug information | Open Developer Debug Info. | Show non-secret state while keeping the secret hidden. | It displayed attempts, scores, bot turns, winner, status, difficulty, and player history without displaying the secret. | Pass |
| Reset behavior | Click **New Game**. | Safely reset the player and bot state for a fresh round. | Attempts, scores, turns, winner, player history, and bot decision log reset successfully. | Pass |

Reliability improved through strict input validation, secret isolation, deterministic behavior, exhaustive testing, and human review. Separating the bot from secret game state and checking every possible secret made its behavior easier to verify and reproduce.

## Reproducible Execution Evidence

This evidence is sufficient to review the automated checks, game behavior, and agent trace without watching a video.

### Automated Test Command

Command: `python -m pytest`

```text
collected 18 items

tests\test_bot_agent.py ..............                                     [ 77%]
tests\test_game_logic.py ....                                               [100%]

============================= 18 passed in 0.13s =============================
```

### Exhaustive Evaluation Command

Command: `python evaluate_bot.py`

```text
Difficulty | Secrets | Win rate | Average turns | Worst-case turns | Guardrail violations
Easy | 20 | 100.00% | 3.70 | 5 | 0
Normal | 100 | 100.00% | 5.80 | 7 | 0
Hard | 200 | 100.00% | 6.76 | 8 | 0
```

### End-to-End Example Runs

#### Example 1 — Invalid Input

```text
Difficulty: Normal
Input: hello
Output: That is not a whole number.
Attempts left: 8
Bot turns: 0
Guardrail: Rejected without consuming either turn.
```

#### Example 2 — Valid Competitive Turn

```text
Difficulty: Normal
Input: 25
Player output: Go HIGHER!
Attempts left: 8 -> 7
Player score: -5
Bot turns: 0 -> 1
Bot score: -5
Bot planned midpoint: 50
Bot outcome: Too High
Bot range: 1-100 -> 1-49
Bot log: No secret field.
```

#### Example 3 — Reset

```text
Action: Click New Game
Output: A fresh round
Player and bot scores: 0
Bot turns: 0
Winner, player history, and bot decision log: cleared
Guardrail: State reset safely.
```

### AI Agent Decision Trace

The evaluation harness held secret 37; the bot received only outcome feedback.

| Turn | Range Before | Guess | Reason | Outcome | Range After |
|---:|---|---:|---|---|---|
| 1 | 1-100 | 50 | midpoint of narrowed range | Too High | 1-49 |
| 2 | 1-49 | 25 | midpoint of narrowed range | Too Low | 26-49 |
| 3 | 26-49 | 37 | midpoint of narrowed range | Win | 26-49 |

### Reliability and Guardrail Result

- **Automated tests:** 18/18 passed.
- **Exhaustive evaluation:** 320/320 possible secrets solved.
- **Win rate:** 100% on every difficulty, within its turn limit.
- **Guardrail violations:** 0.
- **Human evaluation:** 5/5 checks passed.

## Repository Structure

```text
.
├── README.md                 # Project overview and reproducible evidence
├── app.py                    # Streamlit UI and game/session orchestration
├── logic_utils.py            # Difficulty settings, parsing, outcomes, hints, scoring
├── bot_agent.py              # Outcome-only binary-search GuesserBot
├── evaluate_bot.py           # Exhaustive per-difficulty evaluation
├── conftest.py               # Shared pytest fixtures
├── requirements.txt          # Runtime and test dependencies
├── model_card.md             # Responsible-AI reflection
├── ai_interactions.md        # Agent workflow and evaluation evidence
├── presentation.md           # Timed presentation and demo plan
├── diagrams/
│   └── architecture.mmd      # System and verification flowchart
└── tests/
    ├── test_bot_agent.py     # Agent, guardrail, and evaluation-related behavior
    └── test_game_logic.py    # Core game logic tests
```
