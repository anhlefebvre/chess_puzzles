import pygame
import chess
import pandas as pd
import time  

###SETTINGS###
N_BLOCKS = 10
CUE_MS = 500
FEEDBACK_MS = 500
BLANK_MS = 500

BG_COLOR = (30, 30, 30)
LIGHT_SQ = (240, 217, 181)
DARK_SQ = (181, 136, 99)
TEXT_COLOR = (220, 220, 220)
CORRECT_COLOR = (0, 150, 0)
WRONG_COLOR = (200, 0, 0)

###FUNCTIONS###
def grid_to_square(row, col, flipped):
    if flipped:
        square = chess.square(7-col, row)
    else:
        square = chess.square(col, 7-row)
    return square

def draw_board(board, flipped):
        for row in range(8):
            y = BOARD_Y + row * SQUARE
            for col in range(8):
                x = BOARD_X + col*SQUARE
                if (col+row) % 2 ==0:
                    pygame.draw.rect(screen, LIGHT_SQ, (x, y, SQUARE, SQUARE))
                else:
                    pygame.draw.rect(screen, DARK_SQ, (x, y, SQUARE, SQUARE))
    
                square = grid_to_square(row, col, flipped)
                piece = board.piece_at(square)                     
                if piece is not None:                               
                    glyph = GLYPHS[piece.symbol()]          # "K" → "♔"
                    text = piece_font.render(glyph, True, (0, 0, 0))
                    rect = text.get_rect(center=(x + SQUARE //2, y + SQUARE//2))
                    screen.blit(text, rect)
                    
def run_trial(puzzle):
    #Setup
    board = chess.Board(puzzle["FEN"])
    moves = puzzle["Moves"].split()
    board.push_uci(moves[0])
    flipped = board.turn == chess.BLACK

    if puzzle["condition"] == "mate1":
        label = "Mate in 1"
    else:
        label = "Mate in 3"

    label_text = inst_font.render(label, True, TEXT_COLOR)
    label_rect = label_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.fill(BG_COLOR)
    screen.blit(label_text, label_rect)
    pygame.display.flip()
    pygame.time.wait(CUE_MS)

    selected = None
    move_index = 1
    finished = False
    played = []
    first_error = None

    t_start = time.perf_counter()
    clock_start = time.time()
    
    #Running    
    while not finished:    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:        #Close window
                return None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                col = (mouse_x - BOARD_X) // SQUARE
                row = (mouse_y - BOARD_Y) // SQUARE
                if 0 <= row < 8 and 0 <= col < 8:
                    square = grid_to_square(row, col, flipped)
                    piece = board.piece_at(square)
                    if piece is not None and piece.color == board.turn:
                        selected = square
                        
            if event.type == pygame.MOUSEBUTTONUP and selected is not None:
                mouse_x, mouse_y = event.pos
                col = (mouse_x - BOARD_X) // SQUARE
                row = (mouse_y - BOARD_Y) // SQUARE
                if 0 <= row < 8 and 0 <= col < 8:
                    target = grid_to_square(row, col, flipped)
                    move = chess.Move(selected, target)
                    if target == selected:
                        pass
                    elif move in board.legal_moves:
                        board.push(move)
                        played.append(move.uci())
                        if move.uci() != moves[move_index] and first_error is None:
                            first_error = move_index
                        if move_index == 1: 
                            t_first_move = time.perf_counter()
                        move_index += 1
                        if move_index == len(moves) or board.is_game_over():
                            finished = True
                            t_end = time.perf_counter()
                            clock_end = time.time()
                selected = None
            
        screen.fill(BG_COLOR)    
        draw_board(board, flipped)
        pygame.display.flip()                      

    draw_board(board, flipped)
    if first_error is None:
        text = font.render("Correct", True, CORRECT_COLOR)
    else:
        text = font.render("Wrong", True, WRONG_COLOR)
    rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, rect)    
    pygame.display.flip()
    pygame.time.wait(FEEDBACK_MS)

    screen.fill(BG_COLOR)
    pygame.display.flip()
    pygame.time.wait(BLANK_MS)
    
    result={
        "PuzzleId": puzzle["PuzzleId"],
        "played": " ".join(played),
        "first_error": first_error, 
        "rt1": t_first_move - t_start,
        "rt2": t_end - t_first_move,
        "clock_start": clock_start,
        "clock_end": clock_end,
        "solution": " ".join(moves[1:]),
        "correct": first_error is None
    }

    return result


def show_screen(lines):

    screen.fill(BG_COLOR)
    start_y = HEIGHT // 2 - len(lines) * LINE_H // 2
    
    for i, line in enumerate(lines):
        text = inst_font.render(line, True, TEXT_COLOR)
        rect = text.get_rect(center=(WIDTH // 2, start_y + i * LINE_H))
        screen.blit(text, rect)


    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False
    

def make_block(block_number, used_ids):
    if block_number % 2 == 1:
        order = ["mate1", "mate3", "mate1"]
    else:
        order = ["mate3", "mate1", "mate3"]

    parts = []
    for part_number, condition in enumerate(order, start=1):
        if condition == "mate1":
            pool = mate1_table
        else:
            pool = mate3_table
        pool = pool[~pool["PuzzleId"].isin(used_ids)]

        seed = block_number * 10 + part_number
        part = pool.sample(n=5, random_state=seed).copy()
        used_ids.extend(part["PuzzleId"])

        part["block"] = block_number
        part["part"] = part_number
        part["trial"] = range(1, 6)
        part["condition"] = condition
        part["seed"] = seed
        parts.append(part)

    return pd.concat(parts)


def make_plan():
    used_ids = []
    blocks = []
    for b in range(1, N_BLOCKS + 1):
        blocks.append(make_block(b, used_ids))
    return pd.concat(blocks)

### MAIN ###
pygame.init()
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
SQUARE = int(min(WIDTH, HEIGHT) * 0.9) // 8    
BOARD_X = (WIDTH - 8 * SQUARE) // 2
BOARD_Y = (HEIGHT - 8 * SQUARE) // 2

pygame.display.set_caption("Chess puzzle")
font = pygame.font.SysFont(None, 60)
inst_font = pygame.font.SysFont(None, HEIGHT // 28)   
LINE_H = inst_font.get_linesize() + 6 
piece_font = pygame.font.Font("/System/Library/Fonts/Apple Symbols.ttf", int(SQUARE * 0.9))
GLYPHS = {
    "K": "♔", "Q": "♕", "R": "♖", "B": "♗", "N": "♘", "P": "♙",   # White
    "k": "♚", "q": "♛", "r": "♜", "b": "♝", "n": "♞", "p": "♟",   # Black
}

mate1_table = pd.read_csv("pool_mate1.csv")
mate3_table = pd.read_csv("pool_mate3.csv")

stamp = time.strftime("%Y%m%d_%H%M%S")
plan = make_plan()
plan.to_csv(f"plan_{stamp}.csv", index=False)

start_lines = [
    "Chess puzzles",
    "",
    f"This session has {N_BLOCKS} blocks of 15 puzzles.",
    "You can rest between blocks.",
    "",
    "Find the checkmate by dragging the pieces with the mouse.",
    "You play the side at the bottom of the board.",
    "",
    "Before each puzzle you will see Mate in 1 or Mate in 3.",
    "In mate-in-1 puzzles, deliver checkmate in 1 move.",
    "In mate-in-3 puzzles, deliver checkmate in 3 moves,",
    "and also play the opponent's replies:",
    "your move, their move, your move, their move, your mate.",
    "",
    "After each puzzle you will see Correct or Wrong.",
    "Keep your other hand still on the table.",
    "",
    "Press SPACE to start.",
]

end_lines = [
    "Session complete.",
    "",
    "Thank you!",
    "",
    "Press SPACE to exit.",
]

results = []
if show_screen(start_lines):
    for i in range(len(plan)):
        puzzle = plan.iloc[i]
        result = run_trial(puzzle)
    
        if result is None:
            break
        result["trial"] = puzzle["trial"]
        result["condition"] = puzzle["condition"]
        result["seed"] = puzzle["seed"]
        result["block"] = puzzle["block"]
        result["part"] = puzzle["part"]
        results.append(result)
log = pd.DataFrame(results)

if len(results) == len(plan):
    log_file = f"log_{stamp}.csv"
else:
    log_file = f"aborted_{stamp}.csv"
log.to_csv(log_file, index=False)

if len(results) == len(plan):
    show_screen(end_lines)
    
pygame.quit()