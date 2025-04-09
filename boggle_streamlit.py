import streamlit as st
import random
import nltk
import time
from itertools import product

nltk.download('words')
from nltk.corpus import words

english_words = set(words.words())

# Boggle dice
BOGGLE_DICE = [
    ["A", "A", "E", "E", "G", "N"],
    ["E", "L", "R", "T", "T", "Y"],
    ["A", "O", "O", "T", "T", "W"],
    ["A", "B", "B", "J", "O", "O"],
    ["E", "H", "R", "T", "V", "W"],
    ["C", "I", "M", "O", "T", "U"],
    ["D", "I", "S", "T", "T", "Y"],
    ["E", "I", "O", "S", "S", "T"],
    ["D", "E", "L", "R", "V", "Y"],
    ["A", "C", "H", "O", "P", "S"],
    ["H", "I", "M", "N", "Qu", "U"],
    ["E", "E", "I", "N", "S", "U"],
    ["E", "E", "G", "H", "N", "W"],
    ["A", "F", "F", "K", "P", "S"],
    ["H", "L", "N", "N", "R", "Z"],
    ["D", "E", "I", "L", "R", "X"]
]

def generate_board():
    random.shuffle(BOGGLE_DICE)
    return [[random.choice(die) for die in BOGGLE_DICE[i*4:(i+1)*4]] for i in range(4)]

def in_bounds(x, y):
    return 0 <= x < 4 and 0 <= y < 4

def is_valid_on_board(board, word):
    word = word.upper()
    def dfs(x, y, idx, visited):
        if idx == len(word):
            return True
        for dx, dy in product([-1, 0, 1], repeat=2):
            nx, ny = x + dx, y + dy
            if (dx == dy == 0) or not in_bounds(nx, ny) or (nx, ny) in visited:
                continue
            cell = board[nx][ny].upper()
            target = word[idx:idx+len(cell)]
            if target == cell:
                if dfs(nx, ny, idx + len(cell), visited | {(nx, ny)}):
                    return True
        return False

    for x in range(4):
        for y in range(4):
            if word.startswith(board[x][y].upper()):
                if dfs(x, y, len(board[x][y]), {(x, y)}):
                    return True
    return False

def score_word(word):
    length = len(word)
    if length < 3:
        return 0
    elif length <= 4:
        return 1
    elif length == 5:
        return 2
    elif length == 6:
        return 3
    elif length == 7:
        return 5
    else:
        return 11

# Session state
if 'board' not in st.session_state:
    st.session_state.board = generate_board()
    st.session_state.submitted = []
    st.session_state.feedback = ""
    st.session_state.end_time = time.time() + 180
    st.session_state.running = True
    st.session_state.score = 0

def reset_game():
    st.session_state.board = generate_board()
    st.session_state.submitted = []
    st.session_state.feedback = ""
    st.session_state.end_time = time.time() + 180
    st.session_state.running = True
    st.session_state.score = 0

# UI Config
st.set_page_config(page_title="Boggle", layout="wide")
st.title("🔠 Boggle Game")
st.markdown("[How to play Boggle](https://en.wikipedia.org/wiki/Boggle)", unsafe_allow_html=True)

# Custom Styles
st.markdown(
    """
    <style>
    .grid {
        display: grid;
        grid-template-columns: repeat(4, 60px);
        grid-gap: 10px;
        margin-top: 15px;
        padding: 10px;
        background-color: #fafafa;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        width: fit-content;
    }
    .cell {
        width: 60px;
        height: 60px;
        background-color: #f8f9fa;
        border: 2px solid #444;
        border-radius: 8px;
        text-align: center;
        font-size: 24px;
        font-weight: 600;
        line-height: 60px;
        transition: background-color 0.2s ease, transform 0.2s ease;
    }
    .cell:hover {
        background-color: #e1f5fe;
        transform: scale(1.05);
        cursor: pointer;
    }
    .success { color: green; font-weight: bold; }
    .error { color: crimson; font-weight: bold; }
    .warning { color: orange; font-weight: bold; }
    </style>
    """,
    unsafe_allow_html=True
)

col1, col2 = st.columns([1, 2])

with col1:
    html = '<div class="grid">'
    for row in st.session_state.board:
        for letter in row:
            html += f'<div class="cell">{letter}</div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

with col2:
    if st.button("🔁 Start New Game"):
        reset_game()

    if st.button("🔀 Shuffle Letters") and time.time() < st.session_state.end_time:
        st.session_state.board = generate_board()

    word_input = st.text_input("Enter a word")
    if st.button("✅ Submit Word"):
        if time.time() > st.session_state.end_time:
            st.session_state.feedback = "⏰ Time is up!"
            st.session_state.running = False
        elif len(word_input) < 3:
            st.session_state.feedback = f"❌ '{word_input}' is too short."
        elif word_input.lower() not in english_words:
            st.session_state.feedback = f"❌ '{word_input}' is not a valid English word."
        elif word_input.upper() in st.session_state.submitted:
            st.session_state.feedback = f"⚠️ You already submitted '{word_input}'."
        elif not is_valid_on_board(st.session_state.board, word_input):
            st.session_state.feedback = f"❌ '{word_input}' can't be formed on the board."
        else:
            score = score_word(word_input)
            st.session_state.submitted.append(word_input.upper())
            st.session_state.score += score
            st.session_state.feedback = f"✅ '{word_input}' accepted! (+{score} points)"

    if "✅" in st.session_state.feedback:
        st.markdown(f"<p class='success'>{st.session_state.feedback}</p>", unsafe_allow_html=True)
    elif "❌" in st.session_state.feedback:
        st.markdown(f"<p class='error'>{st.session_state.feedback}</p>", unsafe_allow_html=True)
    elif "⚠️" in st.session_state.feedback:
        st.markdown(f"<p class='warning'>{st.session_state.feedback}</p>", unsafe_allow_html=True)

    st.markdown("### 📝 Submitted Words:")
    st.write(", ".join(st.session_state.submitted))
    st.markdown(f"### 🏆 Total Score: **{st.session_state.score}**")

# Timer
remaining = int(st.session_state.end_time - time.time())
if remaining > 0:
    mins, secs = divmod(remaining, 60)
    st.info(f"⏳ Time left: {mins:02}:{secs:02}")
else:
    st.warning("⏰ Time is up!")