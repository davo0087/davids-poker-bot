# --- Streamlit Poker Decision Dashboard ---

import streamlit as st
from treys import Card, Deck, Evaluator
import random

suits = {'♥️': 'h', '♦️': 'd', '♣️': 'c', '♠️': 's'}
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']

st.title("♠️ Poker Decision Dashboard")
st.markdown("""
    <style>
    .stApp {
        background-color: #35654d;
        background-image: radial-gradient(circle, #35654d 0%, #234936 100%);
        background-attachment: fixed;
        background-size: cover;
        color: white;
    }
    .stMarkdown, .css-10trblm, .css-1v3fvcr, .css-1d391kg, .css-ffhzg2 {
        color: white !important;
    }
    img {
        border: 2px solid black;
        border-radius: 4px;
    }
</style>
    """, unsafe_allow_html=True)

if st.button("🔄 Reset All Cards"):
    st.session_state.my_cards = []
    st.session_state.table_cards = []
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

def card_image(card):
    suit_map = {'h': 'hearts', 'd': 'diamonds', 'c': 'clubs', 's': 'spades'}
    rank_map = {'T': '10', 'J': 'jack', 'Q': 'queen', 'K': 'king', 'A': 'ace'}
    rank = rank_map.get(card[0], card[0])
    suit = suit_map[card[1]]
    return f"https://raw.githubusercontent.com/hayeah/playing-cards-assets/master/png/{rank}_of_{suit}.png"

if st.session_state.my_cards:
    st.write("My Cards:")
    cols = st.columns(len(st.session_state.my_cards))
    for i, card in enumerate(st.session_state.my_cards):
        with cols[i]:
            st.image(card_image(card), width=80)

if st.session_state.table_cards:
    st.write("Table Cards:")
    cols = st.columns(len(st.session_state.table_cards))
    for i, card in enumerate(st.session_state.table_cards):
        with cols[i]:
            st.image(card_image(card), width=80)

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

def simulate_stronger_hands(hole, board):
    evaluator = Evaluator()
    deck = Deck()
    known = hole + board
    for c in known:
        if c in deck.cards:
            deck.cards.remove(c)

    stronger_hands = []
    current_score = evaluator.evaluate(board, hole)
    for i in range(500):
        random.shuffle(deck.cards)
        opp_hole = deck.cards[:2]
        opp_score = evaluator.evaluate(board, opp_hole)
        if opp_score < current_score:
            desc = evaluator.class_to_string(evaluator.get_rank_class(opp_score))
            pretty = [Card.int_to_pretty_str(c) for c in opp_hole]
            stronger_hands.append((desc, pretty))
        if len(stronger_hands) >= 5:
            break
    return stronger_hands

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
            st.warning("🔥 Aggression Index: Error calculating index")

        likely_beaters = simulate_stronger_hands(hole, board)
        st.write("💀 Likely Hands That Beat You:")
        for hand_type, cards in likely_beaters:
            st.write(f"{hand_type}: {' '.join(cards)}")
    else:
        st.error("Select exactly 2 cards for 'My Cards'.")
