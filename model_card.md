# Model Card: Game Glitch Investigator

## 1. System Overview and Intended Use

Game Glitch Investigator is an educational Streamlit number-guessing game in which a human competes with a deterministic binary-search agent. The game layer keeps the secret and checks guesses. The bot receives only “Too High,” “Too Low,” or “Win” feedback; it is not given the secret number.

I built this project to demonstrate an agent loop, practical guardrails, transparent decision logging, exhaustive testing, and human review in a small system that is easy to inspect. The bot observes an outcome, narrows its range, plans a midpoint, and acts. This is a fixed rule-based agent, not an LLM or a general-purpose intelligent system, and I would not describe it as either.

## 2. Limitations and Potential Biases

The bot always follows the same binary-search strategy. That makes its behavior predictable and testable, but it cannot adapt its communication or strategy to a particular player. Its efficiency can also make the game uneven or frustrating for beginners: it can solve every supported range within the turn limit, even if a human player is still learning how the ranges and hints work.

The system does not use training data or personal or demographic data, so it avoids many kinds of learned demographic bias. That does not make it bias-free. Its rules favor players who are comfortable reasoning about number ranges and interpreting directional hints. Fairness requires me to examine how those design choices affect different users, not only ask whether a training dataset was biased.

The evaluator checks every possible secret in each supported difficulty, but that is not the same as testing every browser, device, accessibility need, or unusual Streamlit session failure. The bot decision log lives only in the current session; it is useful for immediate review but is not a permanent audit trail. Finally, the bot makes deterministic decisions and does not produce probabilistic confidence scores.

## 3. Possible Misuse and Prevention

A player could try to expose or use the secret to cheat. Someone could also modify this open-source game's engine, feedback, or logs and then make misleading claims about the bot's performance. Another risk is describing the deterministic rule-based agent as a sophisticated generative-AI model. Future developers could also accidentally expose sensitive state if they add fields to the decision log without considering what those fields reveal.

The main protection is data minimization: the bot receives only the outcome needed to narrow its range. The player-facing Developer Debug Info panel and the bot decision log do not display the secret. Whole-number validation, game- and narrowed-range enforcement, turn limits, contradictory-state detection, and readable safe resets reduce errors and make invalid states less likely to produce confusing behavior. These safeguards help avoid harm in the context of the game, but they are not tamper-proof security. A user with access to the open-source code can alter the local system.

I use transparent documentation and exhaustive results to make performance claims checkable rather than asking readers to trust a headline. Human review remains important: a person can inspect the code, decision log, and UI behavior, and should question claims made about modified versions. This supports honesty and trustworthiness by accurately naming what the bot is and what it can do; it supports privacy by limiting information access; and it supports accountability through visible decisions and repeatable tests. Evaluating all secrets is useful, but responsible review also asks what the tests omit and how the system might be changed or misrepresented.

## 4. What Surprised Me During Testing

I was surprised that a simple deterministic agent achieved a 100% win rate for all 320 possible secrets while staying within each difficulty's turn limit. Exhaustive testing was more convincing to me than trying a few sample games because it covered every secret in the supported ranges rather than relying on selected examples.

I also confirmed that invalid input produces neither a player attempt nor a bot turn. Plain `pytest` originally failed because of an import-path issue even though `python -m pytest` passed; adding `conftest.py` made both invocation methods reliable. Testing corrupt or incomplete bot state showed why a readable error and safe reset matter: otherwise a stale state could lead to confusing or contradictory gameplay. Overall, I learned that reliable AI behavior depends on the surrounding software, input validation, state management, and evaluation—not only on the agent's decision rule.

## 5. Human–AI Collaboration

I used Claude to inspect the original project and propose a structured implementation plan. I used GitHub Copilot to implement and revise the bot, guardrails, tests, evaluation script, documentation, and architecture diagram. I then reviewed the changes, ran the tests, played the game, inspected both logs, checked that the secret was hidden, requested a clearer scoreboard layout, and decided which suggestions to accept.

One suggestion I accepted was to use a separate deterministic binary-search `GuesserBot` that receives outcome-only feedback. I accepted it because its reasoning is transparent, reproducible, testable across every possible secret, and usable offline. Keeping the secret out of the agent also follows data-minimization and least-privilege principles: the bot receives only the information it needs for its task.

I rejected an initial suggestion to keep the secret visible in Developer Debug Info on the grounds that the panel was not bot-facing. Even if the bot could not see the value, a player could use it to cheat, undermining fairness, trust, and the validity of the evaluation. Removing the secret from that panel was a deliberate human decision, not an automatic acceptance of AI-generated recommendations. I also revised the initial one-line scoreboard into four clear metric columns because readability and usability are part of responsible system design.

## 6. Responsible-AI Takeaway

I learned that responsible AI requires more than producing a correct output. It includes limiting information access, validating inputs and state, making decisions inspectable, testing performance claims, being honest about limitations, and keeping a human responsible for final decisions. These practices help avoid harm while making the system more transparent and trustworthy.
