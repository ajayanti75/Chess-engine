# Stores information about current state of game and also determines the valid moves at the current state
# and keeps a move log
import numpy as np


class GameState:
    def __init__(self):
        self.board = np.empty([8, 8], dtype="S10")
        for r in range(8):
            for c in range(8):
                if r == 0:
                    if c == 0 or c == 7:
                        self.board[r, c] = 'bR'
                    elif c == 1 or c == 6:
                        self.board[r, c] = 'bN'
                    elif c == 2 or c == 5:
                        self.board[r, c] = 'bB'
                    elif c == 3:
                        self.board[r, c] = 'bK'
                    else:
                        self.board[r, c] = 'bQ'
                elif r == 1:
                    self.board[r, c] = 'bp'
                elif r == 6:
                    self.board[r, c] = 'wp'
                elif r == 7:
                    if c == 0 or c == 7:
                        self.board[r, c] = 'bR'
                    elif c == 1 or c == 6:
                        self.board[r, c] = 'bN'
                    elif c == 2 or c == 5:
                        self.board[r, c] = 'bB'
                    elif c == 3:
                        self.board[r, c] = 'bK'
                    else:
                        self.board[r, c] = 'bQ'
                else:
                    self.board[r, c] = '--'

        self.whiteToMove = True
        self.moveLog = []
