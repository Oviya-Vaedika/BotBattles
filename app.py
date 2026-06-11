import streamlit as st
import streamlit.components.v1 as components
import random

# Set up a professional page layout
st.set_page_config(page_title="PentaPlay Arcade", page_icon="🎮", layout="centered")

# Initialize state screens
if "screen" not in st.session_state:
    st.session_state.screen = "main-menu"
if "ttt_board" not in st.session_state:
    st.session_state.ttt_board = [""] * 9
if "ttt_turn" not in st.session_state:
    st.session_state.ttt_turn = "X"
if "mem_deck" not in st.session_state:
    items = ["🥁", "🎸", "🎺", "🎹", "🎵", "🎨", "🎮", "🧩"] * 2
    random.shuffle(items)
    st.session_state.mem_deck = items
    st.session_state.mem_revealed = [False] * 16
    st.session_state.mem_selected = []

try:
    import chess
    if "chess_board" not in st.session_state:
        st.session_state.chess_board = chess.Board()
    CHESS_AVAILABLE = True
except ImportError:
    CHESS_AVAILABLE = False

# Navigation Header
if st.session_state.screen != "main-menu":
    if st.button("← Back to Home Menu"):
        st.session_state.screen = "main-menu"
        st.rerun()

# ==========================================
# SCREEN 1: MAIN MENU
# ==========================================
if st.session_state.screen == "main-menu":
    st.title("🎮 PENTAPLAY ARCADE")
    st.caption("A premium suite of high-fidelity responsive board games.")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("♟️ Play HD Chess Board", use_container_width=True):
            st.session_state.screen = "chess"
            st.rerun()
        if st.button("❌ Play Neon Tic-Tac-Toe", use_container_width=True):
            st.session_state.screen = "ttt"
            st.rerun()
    with col2:
        if st.button("🥁 Play Drum Card Match", use_container_width=True):
            st.session_state.screen = "memory"
            st.rerun()

# ==========================================
# SCREEN 2: CHESS (CHESS.COM STYLED BOARD)
# ==========================================
elif st.session_state.screen == "chess":
    st.title("♟️ Premium Chess Board")
    
    if not CHESS_AVAILABLE:
        st.error("Please add 'python-chess' to requirements.txt")
    else:
        board = st.session_state.chess_board
        
        # Build pure HTML/CSS representation matching Chess.com palettes
        board_html = """
        <div style="display: grid; grid-template-columns: repeat(8, 1fr); width: 100%; max-width: 400px; margin: 0 auto; border: 4px solid #2d3748; border-radius: 8px; overflow: hidden; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);">
        """
        
        # Chess.com piece unicode mapping
        pieces_unicode = {
            'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔', 'P': '♙',
            'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚', 'p': '♟',
            '.': ''
        }
        
        rows = str(board).split("\n")
        for r_idx, row in enumerate(rows):
            cells = row.split()
            for c_idx, cell in enumerate(cells):
                # Alternating Chess.com light (#eeeed2) and dark (#769656) squares
                is_dark = (r_idx + c_idx) % 2 == 1
                bg_color = "#769656" if is_dark else "#eeeed2"
                text_color = "#000000" if cell.isupper() else "#1a202c"
                piece_icon = pieces_unicode.get(cell, '')
                
                board_html += f"""
                <div style="background-color: {bg_color}; color: {text_color}; aspect-ratio: 1; display: flex; align-items: center; justify-content: center; font-size: 32px; font-weight: bold; user-select: none;">
                    {piece_icon}
                </div>
                """
        board_html += "</div>"
        
        # Inject the stunning HTML board rendering
        components.html(board_html, height=420)
        
        # Real move controls below
        st.info(f"Current System Move Turn: {'White (Uppercase)' if board.turn == chess.WHITE else 'Black (Lowercase)'}")
        move_input = st.text_input("Enter Legal Coordinate Move (e.g., e2e4, g1f3):").strip()
        
        col_sub, col_res = st.columns(2)
        with col_sub:
            if st.button("Execute Move", use_container_width=True):
                try:
                    move = chess.Move.from_uci(move_input)
                    if move in board.legal_moves:
                        board.push(move)
                        st.rerun()
                    else:
                        st.error("Illegal move!")
                except ValueError:
                    st.error("Invalid syntax structure.")
        with col_res:
            if st.button("Reset Chess Game", use_container_width=True):
                st.session_state.chess_board = chess.Board()
                st.rerun()

# ==========================================
# SCREEN 3: MIXED BLUE & RED TIC-TAC-TOE
# ==========================================
elif st.session_state.screen == "ttt":
    st.title("❌ Neon Blue & Red Tic-Tac-Toe")
    st.caption("Mixed Player Turns: X is Vibrant Blue | O is Crimson Red")
    
    # State validation
    def get_winner(b):
        lines = [[0,1,2], [3,4,5], [6,7,8], [0,3,6], [1,4,7], [2,5,8], [0,4,8], [2,4,6]]
        for l in lines:
            if b[l[0]] == b[l[1]] == b[l[2]] != "": return b[l[0]]
        return "Draw" if "" not in b else None

    winner = get_winner(st.session_state.ttt_board)
    if winner:
        st.success(f"Game Finished: {winner}")
    
    # Grid UI generation using Streamlit columns dynamically styled
    for i in range(0, 9, 3):
        cols = st.columns(3)
        for j in range(3):
            idx = i + j
            val = st.session_state.ttt_board[idx]
            
            # Change box button colors on the fly based on current markers
            if val == "X":
                btn_type = "primary" # Cyan/Blue accent theme
                label = "🔵 X"
            elif val == "O":
                btn_type = "secondary" # Red contrast element
                label = "🔴 O"
            else:
                btn_type = "secondary"
                label = "⬛"
                
            if cols[j].button(label, key=f"ttt_{idx}", type=btn_type, disabled=(val != "" or winner is not None), use_container_width=True):
                st.session_state.ttt_board[idx] = st.session_state.ttt_turn
                st.session_state.ttt_turn = "O" if st.session_state.ttt_turn == "X" else "X"
                st.rerun()
                
    if st.button("Reset Match Grid"):
        st.session_state.ttt_board = [""] * 9
        st.session_state.ttt_turn = "X"
        st.rerun()

# ==========================================
# SCREEN 4: DRUM CARD (EMERALD CASINO THEME)
# ==========================================
elif st.session_state.screen == "memory":
    st.title("Drum Card Match Matrix")
    st.caption("A matching game using high-contrast slate buttons.")
    
    for i in range(0, 16, 4):
        cols = st.columns(4)
        for j in range(4):
            idx = i + j
            revealed = st.session_state.mem_revealed[idx]
            label = st.session_state.mem_deck[idx] if revealed else "🟢 ❓"
            
            # Matched pairs stay highlighted while closed cards display deep green pins
            if cols[j].button(label, key=f"mem_{idx}", use_container_width=True, type="primary" if revealed else "secondary"):
                st.session_state.mem_revealed[idx] = True
                st.session_state.mem_selected.append(idx)
                
                if len(st.session_state.mem_selected) == 2:
                    idx1, idx2 = st.session_state.mem_selected
                    if st.session_state.mem_deck[idx1] != st.session_state.mem_deck[idx2]:
                        st.toast("❌ No match! Hiding cards...")
                        st.session_state.mem_revealed[idx1] = False
                        st.session_state.mem_revealed[idx2] = False
                    else:
                        st.toast("✨ Pair Matched Successfully!")
                    st.session_state.mem_selected = []
                st.rerun()

    if st.button("Reshuffle Audio Deck"):
        items = ["🥁", "🎸", "🎺", "🎹", "🎵", "🎨", "🎮", "🧩"] * 2
        random.shuffle(items)
        st.session_state.mem_deck = items
        st.session_state.mem_revealed = [False] * 16
        st.session_state.mem_selected = []
        st.rerun()

