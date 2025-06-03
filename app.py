# --- Streamlit Poker Decision Dashboard ---

import streamlit as st
from treys import Card, Deck, Evaluator
import random

suits = {'♥️': 'h', '♦️': 'd', '♣️': 'c', '♠️': 's'}
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']

st.title("♠️ Poker Decision Dashboard")
st.write("Click your cards and chips to analyze hand strength and potential.")

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

if "pot" not in st.session_state:
    st.session_state.pot = 100.0
if "call" not in st.session_state:
    st.session_state.call = 20.0

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

# --- Utilities ---
def parse_cards(card_strs):
    return [Card.new(c) for c in card_strs if c]

def get_outs(hole, board):
    known = hole + board
    deck = Deck()
    for c in known:
        if c in deck.cards:
            deck.cards.remove(c)

    evaluator = Evaluator()
    current_rank = evaluator.evaluate(board, hole)
    outs = 0
    for card in deck.cards:
        trial_board = board + [card] if len(board) < 5 else board
        rank = evaluator.evaluate(trial_board[:5], hole)
        if rank < current_rank:
            outs += 1
    return outs

def hand_category(hole, board):
    evaluator = Evaluator()
    try:
        score = evaluator.evaluate(board, hole)
        return evaluator.class_to_string(evaluator.get_rank_class(score))
    except:
        return "Incomplete Hand"

def aggression_index(pot, call_amt, hand_strength):
    level = {"High Card": 0.5, "One Pair": 1, "Two Pair": 1.5, "Three of a Kind": 2, "Straight": 2.5,
             "Flush": 3, "Full House": 3.5, "Four of a Kind": 4, "Straight Flush": 4.5, "Royal Flush": 5}
    base = level.get(hand_strength, 1)
    ratio = pot / call_amt if call_amt else 1
    return round(base * ratio, 2)

def simulate_turn_impact(hole, board):
    evaluator = Evaluator()
    deck = Deck()
    known = hole + board
    for c in known:
        if c in deck.cards:
            deck.cards.remove(c)

    results = []
    for card in deck.cards:
        trial_board = board + [card]
        if len(trial_board) > 5:
            trial_board = trial_board[:5]
        score = evaluator.evaluate(trial_board, hole)
        results.append((Card.int_to_pretty_str(card), score))
    results.sort(key=lambda x: x[1])
    return results[:5]  # top 5 best turn cards

# --- Run Button ---
st.markdown("---")
if st.button("Analyze Hand"):
    hole = parse_cards([st.session_state['Hole 1'], st.session_state['Hole 2']])
    board = parse_cards([st.session_state['Flop 1'], st.session_state['Flop 2'], st.session_state['Flop 3'],
                         st.session_state['Turn'], st.session_state['River']])
    if len(hole) == 2:
        st.success(f"🏆 Hand Category: {hand_category(hole, board)}")
        st.info(f"🔢 Outs Count: {get_outs(hole, board)}")
        st.warning(f"🔥 Aggression Index: {aggression_index(st.session_state.pot, st.session_state.call, hand_category(hole, board))}")
        best_turns = simulate_turn_impact(hole, board)
        st.write("🃏 Top Potential Turn Cards:")
        for val, score in best_turns:
            st.write(f"{val} → Rank Score: {score}")
    else:
        st.error("Select two hole cards to begin analysis.")
