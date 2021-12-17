from typing import List
from pieces import Column

import pieces

#    King,
#    Queen,
#    Pawn,
#    Rook,
#    Bishop,
#    Castle,


class Board:
    def __init__(self, pieces: List[pieces.AllPieces]):

        self.board = [[None for _ in range(8)] for _ in range(8)]
        for piece in pieces:
            self.set_piece(piece, piece.x, piece.y)

    def _is_legal_move(self, x: Column, y: int):
        """Simple bounds check"""
        if x > Column.H:
            raise ValueError(f"Invalid move: {x} > H")
        if x < Column.A:
            raise ValueError(f"Invalid move: {x} < A")
        if y > 7:
            raise ValueError(f"Invalid move: {y} > 7")
        if y < 0:
            raise ValueError(f"Invalid move: {y} < 0")

    def set_piece(self, piece: pieces.AllPieces, x: Column, y: int):
        # A1 correlates to index [0][0]
        # enums handle the A->0 conversio, but row conversion needs to be done
        # here since no enum
        index = y - 1

        self._is_legal_move(x, index)
        self.board[x][index] = piece
        piece.move_to(x, index)

    @staticmethod
    def to_color(string, color):
        RESET = "\u001b[0m"
        terminal_colors = {
            "RED": "\u001b[31m",
            "BLACK": "\u001b[30m",
            "GREEN": "\u001b[32m",
            "YELLOW": "\u001b[33m",
            "BLUE": "\u001b[34m",
            "MAGENTA": "\u001b[35m",
            "CYAN": "\u001b[36m",
            "WHITE": "\u001b[37m",
        }
        return "{}{}{}".format(terminal_colors[color], string, RESET)

    def prettify(self, assume_dark_term=True) -> str:
        def color(string):
            if not string:
                return " "
            if string.color == pieces.Color.BLACK:
                if assume_dark_term:
                    return self.to_color(string, "RED")
                else:
                    return self.to_color(string, "BLACK")
            elif string.color == pieces.Color.WHITE:
                if assume_dark_term:
                    return self.to_color(string, "WHITE")
                else:
                    return self.to_color(string, "GREEN")
            else:
                raise ValueError("Invalid color")

        string = self.to_string(color=color)
        arr = []
        for i, line in enumerate(string.split("\n")):
            arr.append("{} {}".format(self.to_color(str(7 - i) + "|", "BLUE"), line))
        arr.append(self.to_color(" +----------------", "BLUE"))
        arr.append(self.to_color("   A B C D E F G H", "BLUE"))
        return "\n".join(arr)

    def to_string(self, color=lambda i: str(i) if i else " "):
        """Pay no attention to the man behind the curtain"""
        lines = []
        for i in range(8):
            lines.append(
                " ".join(
                    map(
                        color,
                        #                [self.board[7-j][i] for j in range(8)]
                        [self.board[j][7 - i] for j in range(8)],
                    )
                )
            )
        return "\n".join(lines)

    def __str__(self):
        return self.to_string()
