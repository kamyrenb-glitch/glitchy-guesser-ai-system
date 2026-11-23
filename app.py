import random
import streamlit as st

from bot_agent import BotStateError, GuesserBot
from logic_utils import (
    check_guess,
    get_attempt_limit,
    get_hint,
    get_range_for_difficulty,
    parse_guess,
    update_score,
)

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("A number guessing game, debugged.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

low, high = get_range_for_difficulty(difficulty)
attempt_limit = get_attempt_limit(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

def start_new_game():
    """Reset every piece of game state for a fresh round."""
    st.session_state.secret = random.randint(low, high)
    st.session_state.attempts = 0
    st.session_state.score = 0
    st.session_state.bot_score = 0
    st.session_state.bot_turns = 0
    st.session_state.status = "playing"
    st.session_state.winner = None
    st.session_state.history = []
    st.session_state.difficulty = difficulty
    st.session_state.bot = GuesserBot(low, high, attempt_limit)
    # The guess box is a keyed widget, so its value lives in session state and
    # survives this reset. Streamlit forbids writing to a widget's key after
    # the widget exists, so leave a note for the top of the next run instead.
    st.session_state.clear_guess_input = True


if "secret" not in st.session_state or "difficulty" not in st.session_state:
    start_new_game()

# Switching difficulty changes the range, so the old secret may no longer be
# reachable. Start a fresh round instead of leaving a stale secret behind.
if st.session_state.difficulty != difficulty:
    start_new_game()

state_error = None
try:
    bot = st.session_state.get("bot")
    if not isinstance(bot, GuesserBot):
        raise BotStateError("The bot state is missing or invalid.")
    bot.validate_state(low, high, attempt_limit)
    required_state = (
        "attempts",
        "bot_turns",
        "score",
        "bot_score",
        "secret",
        "history",
        "status",
        "winner",
    )
    if any(key not in st.session_state for key in required_state):
        raise BotStateError("The saved game state is incomplete.")
    if (
        type(st.session_state.attempts) is not int
        or not 0 <= st.session_state.attempts <= attempt_limit
        or not isinstance(st.session_state.history, list)
        or len(st.session_state.history) != st.session_state.attempts
        or st.session_state.bot_turns != st.session_state.attempts
        or any(
            type(guess) is not int or not low <= guess <= high
            for guess in st.session_state.history
        )
        or st.session_state.bot_turns != bot.turn
        or type(st.session_state.bot_turns) is not int
        or type(st.session_state.score) is not int
        or type(st.session_state.bot_score) is not int
        or type(st.session_state.secret) is not int
        or not low <= st.session_state.secret <= high
        or st.session_state.status not in ("playing", "finished")
        or st.session_state.winner not in (None, "Player", "Bot", "Tie")
        or (st.session_state.status == "playing" and st.session_state.winner is not None)
        or (st.session_state.status == "finished" and st.session_state.winner is None)
    ):
        raise BotStateError("The saved game state is inconsistent.")
except BotStateError as error:
    start_new_game()
    bot = st.session_state.bot
    state_error = f"{error} A new game has been started."

# FIX: New Game left my last guess in the box. Claude diagnosed the keyed widget
# as session state the reset missed, and proposed this deferred clear.
# Runs before the text input is created, which is the only point where its
# stored value may be changed.
if st.session_state.get("clear_guess_input"):
    st.session_state.guess_input = ""
    st.session_state.clear_guess_input = False

st.subheader("Make a guess")

# These render now but are filled in at the bottom of the script, after this
# run's guess has been processed, so they never show stale counts.
attempts_slot = st.empty()
debug_slot = st.empty()

raw_guess = st.text_input("Enter your guess:", key="guess_input")

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    start_new_game()
    st.rerun()

if state_error:
    st.error(state_error)

if state_error is None and st.session_state.status == "playing" and submit:
    ok, guess_int, err = parse_guess(raw_guess, low, high)

    if not ok:
        # An invalid entry is not a guess, so it does not burn an attempt.
        st.error(err)
    else:
        st.session_state.attempts += 1
        st.session_state.history.append(guess_int)

        outcome = check_guess(guess_int, st.session_state.secret)

        if show_hint and outcome != "Win":
            st.warning(get_hint(outcome))

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        try:
            bot.observe(None)
            bot_guess = bot.plan_guess()
            bot_outcome = check_guess(bot_guess, st.session_state.secret)
            bot.observe(bot_outcome)
        except BotStateError as error:
            start_new_game()
            bot = st.session_state.bot
            state_error = f"{error} A new game has been started."
            st.error(state_error)
        else:
            st.session_state.bot_turns = bot.turn
            st.session_state.bot_score = update_score(
                current_score=st.session_state.bot_score,
                outcome=bot_outcome,
                attempt_number=st.session_state.bot_turns,
            )

            if outcome == "Win" and bot_outcome == "Win":
                st.session_state.winner = "Tie"
            elif outcome == "Win":
                st.session_state.winner = "Player"
            elif bot_outcome == "Win":
                st.session_state.winner = "Bot"
            elif (
                st.session_state.attempts >= attempt_limit
                or st.session_state.bot_turns >= attempt_limit
            ):
                if st.session_state.score > st.session_state.bot_score:
                    st.session_state.winner = "Player"
                elif st.session_state.score < st.session_state.bot_score:
                    st.session_state.winner = "Bot"
                else:
                    st.session_state.winner = "Tie"

            if st.session_state.winner is not None:
                st.session_state.status = "finished"
                if st.session_state.winner in ("Player", "Tie"):
                    st.balloons()

if st.session_state.status == "finished" and st.session_state.winner == "Player":
    st.success(
        f"You won! The secret was {st.session_state.secret}. "
        f"Player score: {st.session_state.score} | Bot score: {st.session_state.bot_score}"
    )
elif st.session_state.status == "finished" and st.session_state.winner == "Bot":
    st.error(
        f"The bot won. The secret was {st.session_state.secret}. "
        f"Player score: {st.session_state.score} | Bot score: {st.session_state.bot_score}"
    )
elif st.session_state.status == "finished":
    st.info(
        f"It's a tie. The secret was {st.session_state.secret}. "
        f"Player score: {st.session_state.score} | Bot score: {st.session_state.bot_score}"
    )

attempts_left = max(attempt_limit - st.session_state.attempts, 0)
attempts_slot.caption(f"Guess a number between {low} and {high}")
scoreboard = st.columns(4)
scoreboard[0].metric("Attempts Left", attempts_left)
scoreboard[1].metric("Player Score", st.session_state.score)
scoreboard[2].metric("Bot Turns", st.session_state.bot_turns)
scoreboard[3].metric("Bot Score", st.session_state.bot_score)

with debug_slot.expander("Developer Debug Info"):
    st.write("Attempts:", st.session_state.attempts)
    st.write("Player score:", st.session_state.score)
    st.write("Bot turns:", st.session_state.bot_turns)
    st.write("Bot score:", st.session_state.bot_score)
    st.write("Winner:", st.session_state.winner)
    st.write("Status:", st.session_state.status)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

with st.expander("Bot Decision Log"):
    st.write(bot.decision_log)

st.divider()
st.caption("Built by an AI. Debugged by a human.")
