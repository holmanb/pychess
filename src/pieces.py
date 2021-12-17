from enum import Enum, IntEnum
from typing import Union


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

    def __init__(self, x: Column, y: int, color: Color):
        self.x = x
        self.y = y
        self.color = color

    def move_to(self, x: Column, y: int) -> None:
        self.x = x
        self.y = y

    def get_possible_moves(self):
        raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()


class Pawn(Piece):
    def __str__(self):
        return "P"

    pass


class Rook(Piece):
    def __str__(self):
        return "R"

    pass


class Bishop(Piece):
    def __str__(self):
        return "B"

    pass


class Castle(Piece):
    def __str__(self):
        return "C"

    pass


class King(Piece):
    def __str__(self):
        return "K"

    pass


class Queen(Piece):
    def __str__(self):
        return "Q"

    pass


# For type hints
AllPieces = Union[King, Queen, Castle, Rook, Bishop, Pawn]
