# --- Streamlit Poker Decision Dashboard ---

import streamlit as st
from treys import Card, Deck, Evaluator
import random

suits = {'♥️': 'h', '♦️': 'd', '♣️': 'c', '♠️': 's'}
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']

st.title("♠️ Poker Decision Dashboard")
st.write("Select your cards by clicking them in the 52-card grid. Choose a holder above first.")

# --- Define Card Holders ---
holders = ["My Cards", "Table Cards"]
if "selected_holder" not in st.session_state:
    st.session_state.selected_holder = holders[0]

holder_selection = st.radio("Select a card holder:", holders, horizontal=True)
st.session_state.selected_holder = holder_selection

# --- Track assigned cards ---
if "my_cards" not in st.session_state:
    st.session_state.my_cards = []
if "table_cards" not in st.session_state:
    st.session_state.table_cards = []

# --- Card Deck UI ---
st.subheader("🃏 Full 52 Card Deck")
deck_cols = st.columns(13)
for i, rank in enumerate(ranks):
    for suit_icon, suit_char in suits.items():
        label = rank + suit_char
        pretty = rank + suit_icon
        if deck_cols[i].button(pretty, key=label):
            if st.session_state.selected_holder == "My Cards" and label not in st.session_state.my_cards and len(st.session_state.my_cards) < 2:
                st.session_state.my_cards.append(label)
            elif st.session_state.selected_holder == "Table Cards" and label not in st.session_state.table_cards and len(st.session_state.table_cards) < 5:
                st.session_state.table_cards.append(label)

# --- Show selected cards ---
st.markdown("---")
st.subheader("🗃️ Selected Cards")
st.write(f"My Cards: {st.session_state.my_cards}")
st.write(f"Table Cards: {st.session_state.table_cards}")

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

# --- Analyze Button ---
st.markdown("---")
if st.button("Analyze Hand"):
    hole = parse_cards(st.session_state.my_cards)
    board = parse_cards(st.session_state.table_cards)
    if len(hole) == 2:
        category = hand_category(hole, board)
        st.success(f"🏆 Hand Category: {category}")
        st.info(f"🔢 Outs Count: {get_outs(hole, board)}")
        try:
        rank_list = ['High Card', 'One Pair', 'Two Pair', 'Three of a Kind', 'Straight', 'Flush', 'Full House', 'Four of a Kind', 'Straight Flush', 'Royal Flush']
        if category in rank_list:
            index = rank_list.index(category)
            st.warning(f"🔥 Aggression Index: {round(2.0 * (index + 1), 2)}")
        else:
            st.warning("🔥 Aggression Index: Unknown")
    except Exception as e:
        st.warning(f"🔥 Aggression Index: Error calculating index") + 1), 2)}")
        best_turns = simulate_turn_impact(hole, board)
        st.write("🃏 Top Potential Turn Cards:")
        for val, score in best_turns:
            st.write(f"{val} → Rank Score: {score}")
    else:
        st.error("Select exactly 2 cards for 'My Cards'.")
