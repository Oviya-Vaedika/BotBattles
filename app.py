import streamlit as st
from google import genai
import random
import chess  # Handles our strict chess rules engine

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="BotBattles Arcade", layout="centered", page_icon="🎮")

# --- 2. INITIALIZE GEMINI CLIENT ---
try:
    # Pulls the key safely from Streamlit Cloud Secrets or local secrets.toml
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.error("⚠️ Gemini API Key missing! Please add GEMINI_API_KEY to your Streamlit Secrets.")
    st.stop()

# --- 3. GEMINI BOT BRAIN ---
def ask_gemini(game_name, board_state, event):
    """Sends game data to Gemini 2.5 Flash to get a snappy, funny chat response."""
    system_instruction = (
        f"You are a funny, trash-talking arcade chatbot playing {game_name} against a human. "
        "Keep your response to exactly 1 or 2 short sentences max. Be witty, reactive, and highly competitive."
    )
    prompt = f"Game: {game_name}. Current Layout: {board_state}. The human player just: {event}."
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={'system_instruction': system_instruction}
        )
        return response.text
    except Exception:
        return "🤖 Focus up! Nice move, let's keep playing."

# --- 4. SIDEBAR NAVIGATION MENU ---
st.sidebar.title("🎮 BotBattles Menu")
game_choice = st.sidebar.radio("Select an AI Opponent:", ["Tic-Tac-Toe", "Hangman", "Chess"])

st.title(f"👾 Playing: {game_choice}")

# =====================================================================
# GAME 1: TIC-TAC-TOE
# =====================================================================
if game_choice == "Tic-Tac-Toe":
    if "ttt_board" not in st.session_state:
        st.session_state.ttt_board = [" " for _ in range(9)]
        st.session_state.ttt_chat = "🤖 Let's play Tic-Tac-Toe! Click any box to start."
        st.session_state.ttt_over = False

    st.info(st.session_state.ttt_chat)
    st.write("---")

    def check_ttt_win(b, p):
        wins =, [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]
        return any(all(b[i] == p for i in c) for c in wins)

    def ttt_click(idx):
        if st.session_state.ttt_board[idx] == " " and not st.session_state.ttt_over:
            st.session_state.ttt_board[idx] = "X"
            
            if check_ttt_win(st.session_state.ttt_board, "X"):
                st.session_state.ttt_chat = "😭 Impossible! You won! You must have cheated."
                st.session_state.ttt_over = True
                return
            
            empty = [i for i, x in enumerate(st.session_state.ttt_board) if x == " "]
            if not empty:
                st.session_state.ttt_chat = "😐 A tie game. Try again, human!"
                st.session_state.ttt_over = True
                return

            ai_move = random.choice(empty)
            st.session_state.ttt_board[ai_move] = "O"

            if check_ttt_win(st.session_state.ttt_board, "O"):
                st.session_state.ttt_chat = "🏆 I win! Bow down to the robot master!"
                st.session_state.ttt_over = True
            else:
                st.session_state.ttt_chat = ask_gemini("Tic-Tac-Toe", str(st.session_state.ttt_board), f"placed an X on square index {idx}")

    # Render 3x3 Clickable Grid
    rows = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
    for row in rows:
        cols = st.columns(3)
        for i, idx in enumerate(row):
            val = st.session_state.ttt_board[idx]
            cols[i].button(
                label=val if val != " " else "➕", 
                key=f"t_{idx}", 
                on_click=ttt_click, 
                args=(idx,),
                disabled=st.session_state.ttt_over or val != " "
            )

    if st.session_state.ttt_over:
        if st.button("Reset Tic-Tac-Toe 🔄"):
            del st.session_state.ttt_board
            st.rerun()

# =====================================================================
# GAME 2: HANGMAN
# =====================================================================
elif game_choice == "Hangman":
    WORD_LIST = ["PYTHON", "STREAMLIT", "GEMINI", "ARCADE", "ROBOT", "KEYBOARD", "GAMING"]
    
    if "hm_word" not in st.session_state:
        st.session_state.hm_word = random.choice(WORD_LIST)
        st.session_state.hm_guesses = set()
        st.session_state.hm_lives = 6
        st.session_state.hm_chat = "🤖 I've picked a secret gaming word. Click letters below to guess!"

    st.info(st.session_state.hm_chat)
    st.write(f"❤️ Lives Left: {st.session_state.hm_lives} / 6")

    display_word = " ".join([letter if letter in st.session_state.hm_guesses else "_" for letter in st.session_state.hm_word])
    st.subheader(f"Word:  {display_word}")
    st.write("---")

    def guess_letter(ltr):
        st.session_state.hm_guesses.add(ltr)
        if ltr not in st.session_state.hm_word:
            st.session_state.hm_lives -= 1
            event_text = f"guessed the WRONG letter '{ltr}'"
        else:
            event_text = f"guessed the CORRECT letter '{ltr}'"
        
        st.session_state.hm_chat = ask_gemini("Hangman", display_word, event_text)

    won = all(l in st.session_state.hm_guesses for l in st.session_state.hm_word)
    lost = st.session_state.hm_lives <= 0

    if won:
        st.success(f"🎉 You won! The secret word was indeed {st.session_state.hm_word}!")
        if st.button("Play Next Word 🔄"):
            del st.session_state.hm_word
            st.rerun()
    elif lost:
        st.error(f"💀 Game Over! The word was {st.session_state.hm_word}. Better luck next time!")
        if st.button("Try Again 🔄"):
            del st.session_state.hm_word
            st.rerun()
    else:
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        cols = st.columns(7)
        for i, letter in enumerate(alphabet):
            col_idx = i % 7
            is_guessed = letter in st.session_state.hm_guesses
            cols[col_idx].button(
                label=letter, 
                key=f"h_{letter}", 
                on_click=guess_letter, 
                args=(letter,), 
                disabled=is_guessed
            )

# =====================================================================
# GAME 3: CHESS (Fully Functional Visual 8x8 Grid)
# =====================================================================
elif game_choice == "Chess":
    if "chess_board" not in st.session_state:
        st.session_state.chess_board = chess.Board()
        st.session_state.chess_chat = "🤖 Think you can outsmart an AI in Chess? Touch a piece to select it!"
        st.session_state.selected_square = None

    st.info(st.session_state.chess_chat)

    def handle_square_click(sq_idx):
        board = st.session_state.chess_board
        selected = st.session_state.selected_square
        
        if selected is None:
            piece = board.piece_at(sq_idx)
            if piece and piece.color == chess.WHITE:
                st.session_state.selected_square = sq_idx
        else:
            move = chess.Move(selected, sq_idx)
            promotion_move = chess.Move(selected, sq_idx, promotion=chess.QUEEN)
            
            if move in board.legal_moves:
                board.push(move)
                st.session_state.selected_square = None
                trigger_ai_chess_turn()
            elif promotion_move in board.legal_moves:
                board.push(promotion_move)
                st.session_state.selected_square = None
                trigger_ai_chess_turn()
            else:
                piece = board.piece_at(sq_idx)
                if piece and piece.color == chess.WHITE:
                    st.session_state.selected_square = sq_idx
                else:
                    st.session_state.selected_square = None

    def trigger_ai_chess_turn():
        board = st.session_state.chess_board
        if not board.is_game_over():
            ai_moves = list(board.legal_moves)
            chosen_move = random.choice(ai_moves)
            board.push(chosen_move)
            st.session_state.chess_chat = ask_gemini("Chess", board.fen(), f"moved a piece. Your move was: {chosen_move}")

    PIECE_ICONS = {
        'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔',
        'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚',
        None: ' '
    }
    
    board = st.session_state.chess_board
    
    # Draw the visual board from Rank 8 down to Rank 1
    for rank in reversed(range(8)):
        cols = st.columns(8)
        for file in range(8):
            sq_idx = chess.square(file, rank)
            piece = board.piece_at(sq_idx)
            icon = PIECE_ICONS[piece.symbol() if piece else None]
            
            is_selected = (st.session_state.selected_square == sq_idx)
            display_label = f"[{icon}]" if is_selected and icon != ' ' else icon if icon != ' ' else '🔲'
            
            cols[file].button(
                label=display_label,
                key=f"sq_{sq_idx}",
                on_click=handle_square_click,
                args=(sq_idx,),
                disabled=board.is_game_over()
            )

    if board.is_game_over():
        st.error(f"🏁 Game Over! Result: {board.result()}")
    
    if st.button("Reset Chess Match 🔄"):
        del st.session_state.chess_board
        st.session_state.selected_square = None
        st.rerun()
