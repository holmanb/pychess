from enum import Enum, IntEnum
from typing import Union, List, Tuple, Any


class Column(IntEnum):
    """Index the array using enums

    reference position A1 on the board using:
    ```
    board[Column.A, 1]
    ```
    """
    A = 0
    B = 1
    C = 2
    D = 3
    E = 4
    F = 5
    G = 6
    H = 7


class Color(Enum):
    BLACK = 1
    WHITE = 2


def x_in_bounds(x: int):
    return x >= 0 and x < 8


def y_in_bounds(y: int):
    return y >= 1 and y < 9


class Piece:
    def __init__(self, x: Column, y: int, color: Color):
        self.x = x
        self.y = y
        self.color = color

    """Base class for all pieces

    param x: coordinates param
    param y: coordinates param
    param color: piece color

    The following creates a new black Piece on A1 and moves it to H2
    ```
    a = Piece(A, 1, BLACK)
    a.move_to(H, 2)
    ```
    """
    def get_possible_moves(self):
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()

    def move_to(self, x: Column, y: int) -> None:
        self.x = x
        self.y = y

    def get_relative_position(self, b, x: int, y: int):
        return b.board[self.x + x][self.y + y]

    def get_relative_position_color(self, b, x: int, y: int):
        piece = self.get_relative_position(b, x, y)
        if piece:
            return piece.color


class PieceBase(Piece):
    pass


class Pawn(Piece):
    def __str__(self) -> str:
        return "P"

    def get_possible_moves(self, b) -> Union[List[Tuple[int, int]], None]:
        moves = []
        if self.color == Color.BLACK:
            y_direction = 1
        else:
            y_direction = -1

        # if not blocked, move forward
        if not self.get_relative_position(b, self.x, self.y + y_direction):
            moves.append((self.x,  self.y + y_direction))

        # attack
        if (
                x_in_bounds(self.x - 1)
                and y_in_bounds(self.y + y_direction)
                and self.color is not self.get_relative_position_color(
                    b, self.x - 1, self.y + y_direction)
        ):
            moves.append((self.x - 1, self.y + y_direction))
        # attack
        if (
                x_in_bounds(self.x + 1)
                and y_in_bounds(self.y + y_direction)
                and self.color is not self.get_relative_position(
                    b, self.x + 1, self.y + y_direction)
        ):
            moves.append((self.x + 1, self.y + y_direction))


class Rook(Piece):
    def __str__(self) -> str:
        return "R"

class Bishop(Piece):
    def __str__(self) -> str:
        return "B"

    pass


class Castle(Piece):
    def __str__(self) -> str:
        return "C"

    pass


class King(Piece):
    def __str__(self) -> str:
        return "K"

    pass


class Queen(Piece):
    def __str__(self) -> str:
        return "Q"

    pass


# For type hints
AllPieces = Union[King, Queen, Castle, Rook, Bishop, Pawn]


class Board:

    def __init__(self, pieces: List[AllPieces]):

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

    def set_piece(self, piece: Piece, x: Column, y: int):
        # A1 correlates to index [0][0]
        # enums handle the A->0 conversio, but row conversion needs to be done
        # here since no enum
        index = y - 1

        self._is_legal_move(x, index)
        self.board[int(x)][index] = piece
        piece.move_to(x, index)

    @staticmethod
    def to_color(string: Any, color: str):
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
            if string.color == Color.BLACK:
                if assume_dark_term:
                    return self.to_color(string, "RED")
                else:
                    return self.to_color(string, "BLACK")
            elif string.color == Color.WHITE:
                if assume_dark_term:
                    return self.to_color(string, "WHITE")
                else:
                    return self.to_color(string, "GREEN")
            else:
                raise ValueError("Invalid color")

        string = self.to_string(color=color)
        arr = []
        for i, line in enumerate(string.split("\n")):
            arr.append("{} {}".format(self.to_color(str(8 - i) + "|", "BLUE"), line))
        arr.append(self.to_color(" +----------------", "BLUE"))
        arr.append(self.to_color("   A B C D E F G H", "BLUE"))
        return "\n".join(arr)

    def to_string(self, color=lambda i: str(i) if i else " ") -> str:
        """Pay no attention to the man behind the curtain"""
        lines = []
        for i in range(8):
            lines.append(
                " ".join(
                    map(
                        color,
                        [self.board[j][7 - i] for j in range(8)],
                    )
                )
            )
        return "\n".join(lines)

    def __str__(self) -> str:
        return self.to_string()
