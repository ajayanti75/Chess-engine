# Stores information about current state of game and also determines the valid moves at the current state
# and keeps a move log
import numpy as np


class GameState:
    def __init__(self):
        self.board = np.empty([8, 8], dtype='U2')
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
                        self.board[r, c] = 'wR'
                    elif c == 1 or c == 6:
                        self.board[r, c] = 'wN'
                    elif c == 2 or c == 5:
                        self.board[r, c] = 'wB'
                    elif c == 3:
                        self.board[r, c] = 'wK'
                    else:
                        self.board[r, c] = 'wQ'
                else:
                    self.board[r, c] = '--'
        self.whiteToMove = True
        self.moveLog = []

    # takes a Move object and executes it
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = '--'
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

    # undoes a move
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

    # generates all valid moves out of all possible moves
    def getValidMoves(self):
        return self.getAllMoves()  # to be changed

    # generates all possible moves
    def getAllMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) and (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    if piece == 'p':
                        self.getPawnMoves(r, c, moves)
                    elif piece == 'R':
                        self.getRookMoves(r, c, moves)
                    elif piece == 'N':
                        self.getKnightMoves(r, c, moves)
                    elif piece == 'B':
                        self.getBishopMoves(r, c, moves)
                    elif piece == 'K':
                        self.getKingMoves(r, c, moves)
                    else:
                        self.getQueenMoves(r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        pass

    def getRookMoves(self, r, c, moves):
        pass

    def getKnightMoves(self, r, c, moves):
        pass

    def getBishopMoves(self, r, c, moves):
        pass

    def getKingMoves(self, r, c, moves):
        pass

    def getQueenMoves(self, r, c, moves):
        pass


# A move class to help with executing moves
class Move:
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board):
        self.startRow = start_sq[0]
        self.startCol = start_sq[1]
        self.endRow = end_sq[0]
        self.endCol = end_sq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.cols_to_files[c] + self.rows_to_files[r]
