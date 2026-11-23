# Game Glitch Investigator — Presentation and Demo

**Target duration: 6 minutes 30 seconds**

## 1. Title and Project Purpose — 30 seconds

**Display:** Project title and the running Streamlit game.

**Speaker notes:** “This is Game Glitch Investigator, an educational number-guessing game where a person competes against a deterministic binary-search agent. I used the project to explore how an agent can make decisions transparently while being constrained by validation and state guardrails.”

## 2. Original Glitchy Guesser and What Changed — 45 seconds

**Display:** The game UI and a brief view of the project structure.

**Speaker notes:** “The original Modules 1–3 project, Glitchy Guesser, was a human-only guessing game with difficulty settings, hints, scoring, attempt limits, and tests. I kept that core and added an outcome-only agent, explicit guardrails, decision logs, and an exhaustive evaluator. The system is still a small rule-based game, not a generative-AI runtime.”

## 3. System Architecture and Information Boundary — 60 seconds

**Display:** `diagrams/architecture.mmd`, then `bot_agent.py` and the game-logic outcome check.

**Speaker notes:** “Player input flows through the Streamlit UI and validation before the game layer checks it. The game layer retains the secret. The bot is initialized with its range and turn limit, then receives only Too High, Too Low, or Win feedback. It observes that outcome, narrows its range, plans a midpoint, and submits a guess. This boundary limits access while keeping its decisions inspectable.”

## 4. Live Demo — 2 minutes

**Display:** Streamlit app at Normal difficulty, with its scoreboard and input.

**Speaker notes and actions:**

1. **Show invalid input:** Enter `hello` and click **Submit Guess**. Expected: “That is not a whole number.” Attempts left remains 8 and bot turns remains 0.
2. **Show one valid competitive turn:** Enter `25` and click **Submit Guess**. Expected: player hint “Go HIGHER!”, attempts left changes from 8 to 7, player score becomes -5, bot turns changes from 0 to 1, and bot score becomes -5. The bot’s planned midpoint is 50; its outcome is “Too High,” narrowing the bot range from 1–100 to 1–49.
3. **Open Bot Decision Log:** Show the turn, prior range, guess, reason, outcome, and updated range. Confirm the log has no secret field.
4. **Open Developer Debug Info:** Show the non-secret state—attempts, scores, bot turns, winner, status, difficulty, and player history—and confirm the secret is not displayed.
5. **Click New Game:** Expected: a fresh round with scores and bot turns at 0, and winner, player history, and bot decision log cleared.

**Fallback if the live demo fails:** Show the reproducible execution evidence and the exhaustive evaluation results in `README.md` instead of claiming an unobserved live result.

## 5. Reliability and Evaluation — 60 seconds

**Display:** The README test output and evaluator table, or run `python -m pytest` and `python evaluate_bot.py`.

**Speaker notes:** “The automated suite reports 18 passing tests. The evaluator checks all 320 possible secrets: Easy tests 20, Normal 100, and Hard 200. It reports a 100% win rate within each difficulty’s turn limit and zero guardrail violations. This exhaustive check is stronger evidence for this deterministic strategy than a few hand-picked rounds, though it does not cover every device or unusual session failure.”

## 6. Ethics and Human–AI Collaboration — 60 seconds

**Display:** The Model Card and the Developer Debug Info / bot-log boundary.

**Speaker notes:** “I used Claude to inspect the original project and propose a plan, and GitHub Copilot to implement and revise the agent, tests, evaluation, documentation, and diagram. I accepted the outcome-only binary-search design because it is reproducible and limits information access. I rejected the suggestion to keep the secret in the player-facing debug panel: a player could use it to cheat, even if the bot could not see it. I reviewed the behavior and made the final decisions.”

## 7. Lessons Learned and Closing — 15 seconds

**Display:** The project title and the architecture diagram.

**Speaker notes:** “I learned that reliable agent behavior depends on its surrounding validation, state management, logs, and tests—not only its decision rule.”

**Closing statement:** “Responsible AI means making the system’s boundaries and behavior clear, testing its claims, and keeping a human accountable for the final design.”
