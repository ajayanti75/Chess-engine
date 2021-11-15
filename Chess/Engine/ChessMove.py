# A move class to help with executing moves
class Move:
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, is_enpassant_move=False, is_castle_move=False):
        self.startRow = start_sq[0]
        self.startCol = start_sq[1]
        self.endRow = end_sq[0]
        self.endCol = end_sq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # pawn promotion
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (
                    self.pieceMoved == 'bp' and self.endRow == 7)
        # TODO in main, add if pawn promotion, take promotion choice and store in a field here promotion choice, using optional parameters
        self.isEnpassantMove = is_enpassant_move
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        self.is_castle_move = is_castle_move
        self.is_capture = self.pieceCaptured != "--"
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]

    def __str__(self):
        if self.is_castle_move:
            return "0-0" if self.endCol == 6 else "0-0-0"

        end_square = self.getRankFile(self.endRow, self.endCol)

        if self.pieceMoved[1] == "p":
            if self.is_capture:
                return self.cols_to_files[self.startCol] + "x" + end_square
            else:
                return end_square + "Q" if self.isPawnPromotion else end_square

        move_string = self.pieceMoved[1]
        if self.is_capture:
            move_string += "x"
        return move_string + end_square
