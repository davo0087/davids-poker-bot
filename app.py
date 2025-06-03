# --- Streamlit Poker EV Dashboard ---

import streamlit as st
from treys import Card, Deck, Evaluator
import random

suits = {'♥️': 'h', '♦️': 'd', '♣️': 'c', '♠️': 's'}
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']

st.title("♠️ Poker EV & Odds Dashboard")
st.write("Click your cards and chips to calculate win odds and expected value.")

# --- Initialize session state for cards ---
for label in ["Hole 1", "Hole 2", "Flop 1", "Flop 2", "Flop 3", "Turn", "River"]:
    if label not in st.session_state:
        st.session_state[label] = None

# --- Interactive Card Pickers ---
def card_grid(label):
    st.markdown(f"**{label}**")
    suit_choice = st.radio(f"Choose Suit for {label}", list(suits.keys()), horizontal=True, key=f"suit_{label}")
    cols = st.columns(13)
    for i, rank in enumerate(ranks):
        if cols[i].button(rank, key=f"{label}_{rank}"):
            st.session_state[label] = rank + suits[suit_choice]
    return st.session_state[label]

hole1 = card_grid("Hole 1")
hole2 = card_grid("Hole 2")

st.markdown("---")
st.subheader("Community Cards")

flop1 = card_grid("Flop 1")
flop2 = card_grid("Flop 2")
flop3 = card_grid("Flop 3")
turn = card_grid("Turn")
river = card_grid("River")

# --- Chip Selectors with Session State ---
st.markdown("---")
st.subheader("\U0001FA99 Pot & Call Chips")

# Initialize session state for chips
if "pot" not in st.session_state:
    st.session_state.pot = 100.0
if "call" not in st.session_state:
    st.session_state.call = 20.0

# Clear All button
if st.button("🧼 Clear All (Pot & Call)", key="clear_all"):
    st.session_state.pot = 0.0
    st.session_state.call = 0.0

chip_values = [0.25, 0.5, 1, 5]
chip_emojis = {0.25: "🟤", 0.5: "🔵", 1: "🟢", 5: "🔴"}

pot_col, call_col = st.columns(2)

with pot_col:
    st.write("Pot Chips")
    for val in chip_values:
        if st.button(f"{chip_emojis[val]} Add ${val} to Pot", key=f"pot_{val}"):
            st.session_state.pot += val
    st.session_state.pot = st.number_input("Pot Total ($):", value=st.session_state.pot, step=0.25)

with call_col:
    st.write("Call Chips")
    for val in chip_values:
        if st.button(f"{chip_emojis[val]} Add ${val} to Call", key=f"call_{val}"):
            st.session_state.call += val
    st.session_state.call = st.number_input("Call Amount ($):", value=st.session_state.call, step=0.25)

# --- Display Selected Cards ---
st.markdown("---")
st.subheader("🃏 Your Current Hand")
st.write(f"Hole Cards: {st.session_state['Hole 1']} {st.session_state['Hole 2']}")
st.write(f"Board: {st.session_state['Flop 1']} {st.session_state['Flop 2']} {st.session_state['Flop 3']} {st.session_state['Turn']} {st.session_state['River']}")

# --- Calculations ---
def parse_cards(card_strs):
    return [Card.new(c) for c in card_strs if c]

def calculate_win_and_tie_odds(hole_strs, board_strs, num_players=2, simulations=1000):
    evaluator = Evaluator()
    wins, ties = 0, 0

    if len(hole_strs) != 2 or len(board_strs) > 5:
        return None, None

    hole = parse_cards(hole_strs)
    board = parse_cards(board_strs)

    for _ in range(simulations):
        deck = Deck()
        for c in hole + board:
            if c in deck.cards:
                deck.cards.remove(c)

        full_board = board[:]
        while len(full_board) < 5:
            full_board.append(deck.draw(1)[0])

        opp_scores = []
        for _ in range(num_players - 1):
            opp = [deck.draw(1)[0], deck.draw(1)[0]]
            opp_scores.append(evaluator.evaluate(full_board, opp))

        player_score = evaluator.evaluate(full_board, hole)

        if all(player_score < s for s in opp_scores):
            wins += 1
        elif any(player_score == s for s in opp_scores):
            ties += 1

    return round((wins / simulations) * 100, 2), round((ties / simulations) * 100, 2)

def calculate_ev(pot, call_amt, win_pct, tie_pct):
    win_chance = win_pct / 100
    tie_chance = tie_pct / 100
    lose_chance = 1 - win_chance - tie_chance
    ev = (win_chance * pot) + (tie_chance * pot / 2) - (lose_chance * call_amt)
    return round(ev, 2)

# --- Run Button ---
st.markdown("---")
if st.button("Calculate EV & Odds"):
    hole = [st.session_state['Hole 1'], st.session_state['Hole 2']]
    board = [st.session_state['Flop 1'], st.session_state['Flop 2'], st.session_state['Flop 3'], st.session_state['Turn'], st.session_state['River']]
    win, tie = calculate_win_and_tie_odds(hole, board)
    if win is not None:
        ev = calculate_ev(st.session_state.pot, st.session_state.call, win, tie)
        st.success(f"🧠 Win Odds: {win}%")
        st.info(f"🤝 Tie Odds: {tie}%")
        st.warning(f"{'✅ Positive' if ev >= 0 else '❌ Negative'} EV: ${ev}")
    else:
        st.error("Invalid card input. Please check selections.")
