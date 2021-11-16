# driver file that handles user input and displays the GameState object
import pygame as p
from Engine import ChessEngine
from Engine import AI
from Engine import ChessMove
from multiprocessing import Process, Queue

WIDTH = HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


# initialize a global dictionary of images
def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def main():
    p.init()
    screen = p.display.set_mode((WIDTH+MOVE_LOG_PANEL_WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    valid_moves = gs.getValidMoves()
    move_made = False
    animate = False  # flag variable for when we should animate a move
    loadImages()
    running = True
    current_sq = ()
    player_clicks = []
    gameOver = False
    moveLogFont = p.font.SysFont("Calibri", 12, False, False)
    playerOne = True  # True if a human is playing white
    playerTwo = False  # True if a human is playing black
    AIThinking = False
    move_finder_process = None
    move_undone = False
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if current_sq == (row, col) or col >= 8:  # user clicks same sq 2 times or move log click
                        current_sq = ()
                        player_clicks = []
                    else:
                        current_sq = (row, col)
                        player_clicks.append(current_sq)
                    if len(player_clicks) == 2:
                        move = ChessMove.Move(player_clicks[0], player_clicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.makeMove(valid_moves[i])
                                move_made = True
                                animate = True
                                current_sq = ()  # reset move
                                player_clicks = []
                        if not move_made:
                            player_clicks = [current_sq]
                    # key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo when z is pressed
                    gs.undoMove()  # possible improvement is storing undone move and being able to redo it
                    move_made = True
                    animate = False
                    gameOver = False
                    if AIThinking:
                        move_finder_process.terminate()
                        AIThinking = False
                    move_undone = True
                if e.key == p.K_r:  # reset when r is pressed
                    gs = ChessEngine.GameState()
                    valid_moves = gs.getValidMoves()
                    current_sq = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    gameOver = False
                    if AIThinking:
                        move_finder_process.terminate()
                        AIThinking = False
                    move_undone = True
        #AI move finder
        if not gameOver and not humanTurn and not move_undone:
            if not AIThinking:
                AIThinking = True
                returnQueue = Queue()  #used to pass data between threads
                move_finder_process = Process(target=AI.findBestMove, args=(gs, valid_moves, returnQueue))
                move_finder_process.start()
            if not move_finder_process.is_alive():
                AIMove = returnQueue.get()
                if AIMove is None:
                    AIMove = AI.findRandomMove()
                gs.makeMove(AIMove)
                move_made = True
                animate = True
                AIThinking = False
        if move_made:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            valid_moves = gs.getValidMoves()
            move_made = False
            animate = False
        drawGameState(screen, gs, valid_moves, current_sq, moveLogFont)
        if gs.checkmate or gs.stalemate:
            gameOver = True
            drawEndgameText(screen, "Stalemate" if gs.stalemate else "Black wins" if gs.whiteToMove else "White wins")
        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, gs, valid_moves, current_sq, move_log_font):
    drawBoard(screen)
    highlightSquares(screen, gs, valid_moves, current_sq)
    drawPieces(screen, gs.board)
    drawMoveLog(screen, gs, move_log_font)


def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def highlightSquares(screen, gs, valid_moves, current_sq):
    """Function for square highlighting"""
    if (len(gs.moveLog)) > 0:
        last_move = gs.moveLog[-1]
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(p.Color('blue'))
        screen.blit(s, (last_move.endCol * SQ_SIZE, last_move.endRow * SQ_SIZE))
    if current_sq != ():
        row, col = current_sq
        if gs.board[row][col][0] == ('w' if gs.whiteToMove else 'b'):  # current_sq is a piece that can be moved
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # transparency value 0 -> transparent, 255 -> opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (col * SQ_SIZE, row * SQ_SIZE))
            # highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.startRow == row and move.startCol == col:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawMoveLog(screen, gs, font):
    move_log_rect = p.Rect(WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color('black'), move_log_rect)
    move_log = gs.moveLog
    move_texts = []
    for i in range(0, len(move_log), 2):
        move_string = str(i // 2 + 1) + '. ' + str(move_log[i]) + " "
        if i + 1 < len(move_log):
            move_string += str(move_log[i + 1]) + "  "
        move_texts.append(move_string)
    moves_per_row = 3
    padding = 5
    line_spacing = 2
    text_y = padding
    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i + j]

        text_object = font.render(text, True, p.Color('white'))
        text_location = move_log_rect.move(padding, text_y)
        screen.blit(text_object, text_location)
        text_y += text_object.get_height() + line_spacing


def animateMove(move, screen, board, clock):
    """
    Animating a move
    """
    global colors
    d_row = move.endRow - move.startRow
    d_col = move.endCol - move.startCol
    frames_per_square = 10  # frames to move one square
    frame_count = (abs(d_row) + abs(d_col)) * frames_per_square
    for frame in range(frame_count + 5):
        row, col = (move.startRow + d_row * frame / frame_count, move.startCol + d_col * frame / frame_count)
        drawBoard(screen)
        drawPieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        end_square = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)
        # draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            if move.isEnpassantMove:
                enpassant_row = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                end_square = p.Rect(move.endCol * SQ_SIZE, enpassant_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], end_square)
        # draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def drawEndgameText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, False, p.Color("black"))
    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - text_object.get_width() / 2,
                                                     HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, False, p.Color('black'))
    screen.blit(text_object, text_location.move(2, 2))


if __name__ == '__main__':
    main()
