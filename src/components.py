from enum import Enum, IntEnum
from typing import Union, List, Any, Tuple


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


class Piece:
    def __init__(self, x: Column, y: int, color: Color):
        """Initialize to index
        """
        self.x = x
        self.y = y - 1
        self.index_valid_or_raise(self.x, self.y)
        self.color = color

    """Base class for all pieces

    param x: holds the index
    param y: holds the index
    param color: piece color

    The following creates a new black Piece on A1 and moves it to H2
    ```
    a = Piece(A, 1, BLACK)
    a.move_to_position(H, 2)
    ```
    """
    def get_possible_moves(self):
        raise NotImplementedError()

    def __str__(self) -> str:
        """For testing"""
        return "X"

    @classmethod
    def is_index_valid(cls, x: int, y: int) -> bool:
        return x >= 0 and x < 8 and y >= 0 and y < 8

    @classmethod
    def index_valid_or_raise(cls, x: int, y: int):
        if not Piece.is_index_valid(x, y):
            raise ValueError(f"invalid index [{x}][{y}]")

    def move_to_index(self, x: int, y: int) -> None:
        """Takes index values to move to
        """
        if not Piece.is_index_valid(x, y):
            ValueError("invalid x value")
        self.x = x
        self.y = y

    def move_to_position(self, x: Column, y: int) -> None:
        self.index_valid_or_raise(x, y - 1)
        self.move_to_index(x, y - 1)

    def get_relative_index(self, b, x: int, y: int):
        return b.board[self.x + x][self.y + y]

    def get_relative_index_color(self, b, x: int, y: int):
        piece = self.get_relative_index(b, x, y)
        if piece:
            return piece.color


class Pawn(Piece):
    def __str__(self) -> str:
        return "P"

    def get_possible_moves_index(self, b) -> Union[List[Tuple[int, int]], None]:
        moves = []
        if self.color == Color.BLACK:
            y_direction = 1
        else:
            y_direction = -1

        # if not blocked, move forward
        if not self.get_relative_index(b, 0, y_direction):
            moves.append((self.x,  self.y + y_direction))

        # attack
        if (
                Piece.is_index_valid(self.x - 1, self.y + y_direction)
                and self.get_relative_index(b, -1, y_direction)
                and self.color is not self.get_relative_index_color(
                b, -1, y_direction)
        ):
            moves.append((self.x - 1, self.y + y_direction))
        # attack
        if (
                Piece.is_index_valid(self.x + 1, self.y + y_direction)
                and self.get_relative_index(b, 1, y_direction)
                and self.color is not self.get_relative_index_color(
                b, 1, y_direction)
        ):
            moves.append((self.x + 1, self.y + y_direction))
        return moves

    def get_possible_moves_position(self, b) -> Union[List[Tuple[int, int]], None]:
        return [(x, y + 1) for x,y in self.get_possible_moves_index(b)]


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
AllPieces = Union[King, Queen, Castle, Rook, Bishop, Pawn, Piece]


class Board:

    def __init__(self, pieces: List[AllPieces]):

        self.board = [[None for _ in range(8)] for _ in range(8)]
        for piece in pieces:
            self.init_piece(piece, piece.x, piece.y)

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

    def init_piece(self, piece: Piece, x: Column, y: int):

        self._is_legal_move(x, y)
        self.board[int(x)][y] = piece


    def set_piece(self, piece: Piece, x: Column, y: int):
        # A1 correlates to index [0][0]
        # enums handle the A->0 conversio, but row conversion needs to be done
        # here since no enum
        index = y - 1

        self._is_legal_move(x, y)
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
