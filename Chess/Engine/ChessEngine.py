# Stores information about current state of game and also determines the valid moves at the current state
# and keeps a move log
import numpy as np
from Engine import ChessMove
from Engine import CastleRights


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
                        self.board[r, c] = 'bQ'
                    else:
                        self.board[r, c] = 'bK'
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
                        self.board[r, c] = 'wQ'
                    else:
                        self.board[r, c] = 'wK'
                else:
                    self.board[r, c] = '--'
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                              'B': self.getBishopMoves, 'K': self.getKingMoves, 'Q': self.getQueenMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.in_check = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        self.enpassantPossible = ()  # coordinates for the square where en passant is possible
        self.currentCastlingRights = CastleRights.CastleRights(True, True, True, True)
        self.castlingLog = [CastleRights.CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                         self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]

    # takes a Move object and executes it
    def makeMove(self, move):
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.board[move.startRow][move.startCol] = '--'
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)
        # pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[
                                                       0] + 'Q'  # TODO change to promotion choice once promotion choice implemented
        # en passant
        if move.isEnpassantMove:
            self.board[move.endRow][move.endCol] = move.pieceMoved  # capturing the pawn
            if self.whiteToMove:
                self.board[move.endRow + 1][move.endCol] = '--'
            else:
                self.board[move.endRow - 1][move.endCol] = '--'
        # update enpassantPossible
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, (move.startCol + move.endCol) // 2)
        else:
            self.enpassantPossible = ()
        # castle move
        if move.is_castle_move:
            if move.endCol - move.startCol == 2:  # king-side castle move
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][
                    move.endCol + 1]  # moves the rook to its new square
                self.board[move.endRow][move.endCol + 1] = '--'  # erase old rook
            else:  # queen-side castle move
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][
                    move.endCol - 2]  # moves the rook to its new square
                self.board[move.endRow][move.endCol - 2] = '--'  # erase old rook
        # update castling rights
        self.updateCastleRights(move)
        self.castlingLog.append(CastleRights.CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                             self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

    # undoes a move
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.endRow, move.endCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.endRow, move.endCol)
            # undo enpassant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            # undo a 2 square pawn advance
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()
            self.checkmate = False
            self.stalemate = False
            # undo castle move
            if move.is_castle_move:
                if move.endCol - move.startCol == 2:  # king-side
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:  # queen-side
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'
            # undo castling rights
            self.castlingLog.pop()
            self.currentCastlingRights = self.castlingLog[-1]

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRights.bks = False

    # generates all valid moves out of all possible moves
    def getValidMoves(self):
        moves = []
        temp_castle_rights = CastleRights.CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                          self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)
        self.in_check, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.in_check:
            if len(self.checks) == 1:  # king attacked only by one piece, check should be blocked, or king should be moved
                moves = self.getAllMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                # if the piece causing a check is a knight, it must be captured or the king must be moved
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)  # check[2/3] are the check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                # get rid of any moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1):  # go backwards through list
                    if moves[i].pieceMoved[1] != 'K':  # king not moved so the check causing piece must be blocked or captured
                        if not (moves[i].endRow,
                                moves[i].endCol) in validSquares:  # move doesnt block check or capture piece
                            moves.remove(moves[i])
            else:  # double check, king must move
                self.getKingMoves(kingRow, kingCol, moves)
        else:  # not in check
            moves = self.getAllMoves()
            if self.whiteToMove:
                self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
            else:
                self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        if len(moves) == 0:
            if self.inCheck():
                self.checkmate = True
            else:
                # TODO stalemate on repeated moves
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.currentCastlingRights = temp_castle_rights
        return moves

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove  # switch to opponent's point of view
        opponents_moves = self.getAllMoves()
        self.whiteToMove = not self.whiteToMove
        for move in opponents_moves:
            if move.endRow == r and move.endCol == c:  # square is under attack
                return True
        return False

    # generates all possible moves
    def getAllMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        if self.whiteToMove:  # white pawn moves
            if self.board[r - 1][c] == '--':  # forward
                if not piece_pinned or pin_direction == (-1, 0):
                    moves.append(ChessMove.Move((r, c), (r - 1, c), self.board))
                    if r == 6 and self.board[r - 2][c] == '--':
                        moves.append(ChessMove.Move((r, c), (r - 2, c), self.board))

            if c - 1 >= 0:  # left capture
                if self.board[r - 1][c - 1][0] == 'b':
                    if not piece_pinned or pin_direction == (-1, -1):
                        moves.append(ChessMove.Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enpassantPossible:
                    if not piece_pinned or pin_direction == (-1, -1):
                        moves.append(ChessMove.Move((r, c), (r - 1, c - 1), self.board, is_enpassant_move=True))

            if c + 1 <= 7:  # right capture
                if self.board[r - 1][c + 1][0] == 'b':
                    if not piece_pinned or pin_direction == (-1, 1):
                        moves.append(ChessMove.Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassantPossible:
                    if not piece_pinned or pin_direction == (-1, 1):
                        moves.append(ChessMove.Move((r, c), (r - 1, c + 1), self.board, is_enpassant_move=True))

        else:  # black pawn moves
            if self.board[r + 1][c] == '--':  # forward
                if not piece_pinned or pin_direction == (1, 0):
                    moves.append(ChessMove.Move((r, c), (r + 1, c), self.board))
                    if r == 1 and self.board[r + 2][c] == '--':
                        moves.append(ChessMove.Move((r, c), (r + 2, c), self.board))

            if c - 1 >= 0:  # left capture
                if self.board[r + 1][c - 1][0] == 'w':
                    if not piece_pinned or pin_direction == (1, -1):
                        moves.append(ChessMove.Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassantPossible:
                    if not piece_pinned or pin_direction == (1, -1):
                        moves.append(ChessMove.Move((r, c), (r + 1, c - 1), self.board, is_enpassant_move=True))

            if c + 1 <= 7:  # right capture
                if self.board[r + 1][c + 1][0] == 'w':
                    if not piece_pinned or pin_direction == (1, 1):
                        moves.append(ChessMove.Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassantPossible:
                    if not piece_pinned or pin_direction == (1, 1):
                        moves.append(ChessMove.Move((r, c), (r + 1, c + 1), self.board, is_enpassant_move=True))

    def getRookMoves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        opp_color = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--':
                            moves.append(ChessMove.Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == opp_color:
                            moves.append(ChessMove.Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # friendly piece
                            break
                else:  # out of bounds
                    break

    def getKnightMoves(self, r, c, moves):
        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, 1), (2, -1))
        ally_color = 'w' if self.whiteToMove else 'b'
        for m in knight_moves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piece_pinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != ally_color:
                        moves.append(ChessMove.Move((r, c), (endRow, endCol), self.board))

    def getBishopMoves(self, r, c, moves):
        # Get all the bishop moves for the bishop located at row col and add the moves to the list.
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (-1, 1), (1, 1), (1, -1))  # diagonals: up/left up/right down/right down/left
        opp_color = "b" if self.whiteToMove else "w"
        for direction in directions:
            for i in range(1, 8):
                end_row = r + direction[0] * i
                end_col = c + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:  # check if the move is on board
                    if not piece_pinned or pin_direction == direction or pin_direction == (
                            -direction[0], -direction[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--":  # empty space is valid
                            moves.append(ChessMove.Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == opp_color:  # capture enemy piece
                            moves.append(ChessMove.Move((r, c), (end_row, end_col), self.board))
                            break
                        else:  # friendly piece
                            break
                else:  # off board
                    break

    def getKingMoves(self, r, c, moves):
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = "w" if self.whiteToMove else "b"
        for i in range(8):
            end_row = r + row_moves[i]
            end_col = c + col_moves[i]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:  # not an ally piece - empty or enemy
                    # place king on end square and check for checks
                    if ally_color == "w":
                        self.whiteKingLocation = (end_row, end_col)
                    else:
                        self.blackKingLocation = (end_row, end_col)
                    in_check, pins, checks = self.checkForPinsAndChecks()
                    if not in_check:
                        moves.append(ChessMove.Move((r, c), (end_row, end_col), self.board))
                    # place king back on original location
                    if ally_color == "w":
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)

    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return
        if (self.whiteToMove and self.currentCastlingRights.wks) or (
                not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (
                not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                moves.append(ChessMove.Move((r, c), (r, c + 2), self.board, is_castle_move=True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(ChessMove.Move((r, c), (r, c - 2), self.board, is_castle_move=True))

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    # returns list of all the pieces that are pinned, all the pieces that are causing a check and whether or not the king is in check
    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        in_check = False
        if self.whiteToMove:
            opp_color = 'b'
            ally_color = 'w'
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            opp_color = 'w'
            ally_color = 'b'
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == ally_color and endPiece[1] != 'K':
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    elif endPiece[0] == opp_color:
                        type = endPiece[1]
                        # the following if checks for 5 possibilities to determine whether a piece moving would cause a check
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'p' and (
                                        (opp_color == 'w' and 6 <= j <= 7) or (opp_color == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblePin == ():
                                in_check = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:
                                pins.append(possiblePin)
                                break
                        else:
                            break
        # check for knight attacks
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, 1), (2, -1))
        for m in knight_moves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == opp_color and endPiece[1] == 'N':
                    in_check = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return in_check, pins, checks

