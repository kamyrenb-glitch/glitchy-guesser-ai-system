# Game Glitch Investigator

Game Glitch Investigator is a Streamlit number-guessing game where a human competes against a deterministic, outcome-only AI guessing agent. Both try to identify the same secret number, and each valid player guess is followed by one bot turn.

The project emphasizes a transparent agent, explicit input and state guardrails, and decision logs that can be reviewed through the UI. Exhaustive evaluation checks the bot against every possible secret on every difficulty, making its behavior reproducible and its safety claims testable.

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

The latest verified results are:

| Difficulty | Secrets tested | Win rate | Average turns | Worst-case turns | Guardrail violations |
|---|---:|---:|---:|---:|---:|
| Easy | 20 | 100% | 3.70 | 5 | 0 |
| Normal | 100 | 100% | 5.80 | 7 | 0 |
| Hard | 200 | 100% | 6.76 | 8 | 0 |

`python -m pytest` reports **18 passed**. An initial import-path issue with plain `pytest` was resolved by adding the root `conftest.py`.

The manual UI review checklist covers invalid input leaving both turn counts unchanged, a valid input triggering exactly one bot turn, inspection of bot decision logs, checking that the secret is not exposed to the bot or its logs, and confirming that **New Game** resets the round state. The exhaustive evaluation tests every possible secret and records wins, turn counts, and guardrail violations.

This project reinforced the importance of separating an agent from secret game state and testing deterministic behavior across the entire input space, rather than relying only on a few sample rounds.

## Repository Structure

```text
.
├── app.py                    # Streamlit UI and game/session orchestration
├── logic_utils.py            # Difficulty settings, parsing, outcomes, hints, scoring
├── bot_agent.py              # Outcome-only binary-search GuesserBot
├── evaluate_bot.py           # Exhaustive per-difficulty evaluation
├── conftest.py               # Shared pytest fixtures
├── requirements.txt          # Runtime and test dependencies
├── diagrams/
│   └── architecture.mmd      # System and verification flowchart
└── tests/
    ├── test_bot_agent.py     # Agent, guardrail, and evaluation-related behavior
    └── test_game_logic.py    # Core game logic tests
```
