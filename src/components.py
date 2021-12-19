from enum import Enum, IntEnum
from typing import Union, List, Any
from collections import namedtuple

Index = namedtuple("Index", ("x", "y"))


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


def is_index_valid(x: int, y: int) -> bool:
    return x >= 0 and x < 8 and y >= 0 and y < 8


def is_position_valid(x: Column, y: int) -> bool:
    return is_index_valid(int(x), y - 1)


def index_valid_or_raise(x: int, y: int):
    if not is_index_valid(x, y):
        raise ValueError(f"invalid index [{x}][{y}]")


def position_valid_or_raise(x: Column, y: int):
    if not position_valid_or_raise(x, y):
        raise ValueError(f"invalid index [{x}][{y}]")


def get_index(b, x: int, y: int):
    return b.board[x][y]


def get_position(b, x: Column, y: int):
    return b.board[int(x)][y - 1]


class Color(Enum):
    BLACK = 1
    WHITE = 2


def get_other_color(color: Color):
    if Color.BLACK == color:
        return Color.WHITE
    elif Color.WHITE == color:
        return Color.BLACK
    else:
        raise ValueError("Invalid color")


class Piece:
    """Base class for all pieces

    param x: holds the index
    param y: holds the index
    param color: which team

    The following creates a new black Piece on A1 and moves it to H2
    ```
    a = Piece(A, 1, BLACK)
    a.move_to_position(H, 2)

    Note: Since there are two ways to reference a piece "location": array
    index, and the standard chess coordinate notation (A1-H8). Several helper
    functions exist to switch between the two. Functions that
    deal with the internal array index use the name "index" and have integer
    parameter type hinting. Functions that use chess coordinates use the name
    "position" in the function name and have one "Column" type hinted parameter
    ```
    """

    def __init__(self, x: Column, y: int, color: Color):
        self.x = x
        self.y = y - 1
        index_valid_or_raise(self.x, self.y)
        self.color = color

    def get_possible_moves_index(self, _b) -> List:
        """Get list of available moves by this piece"""
        raise NotImplementedError()

    def get_attacking_moves_index(self, b) -> List:
        """Get list of attacking moves by this piece"""
        return self.get_possible_moves_index(b)

    def __str__(self) -> str:
        """For testing"""
        return "X"

    def is_relative_index_valid(self, x: int, y: int) -> bool:
        """Check validity of index relative to current position"""
        return is_index_valid(self.x + x, self.y + y)

    def relative_index_valid_or_raise(self, x: int, y: int):
        """Check validity and raise if invalid"""
        index_valid_or_raise(self.x + x, self.y + y)

    def move_to_index(self, x: int, y: int) -> None:
        index_valid_or_raise(x, y)
        self.x = x
        self.y = y

    def move_to_relative_index(self, x: int, y: int) -> None:
        self.move_to_index(self.x + x, self.y + y)

    def move_to_position(self, x: Column, y: int) -> None:
        """Move to board position using standard chess naming: A1-H8"""
        index_valid_or_raise(x, y - 1)
        self.move_to_index(x, y - 1)

    def get_relative_index(self, b, x: int, y: int):
        return get_index(b, self.x + x, self.y + y)

    def get_relative_index_color(self, b, x: int, y: int):
        """Get color of piece"""
        piece = self.get_relative_index(b, x, y)
        if piece:
            return piece.color

    def get_possible_moves_position(self, b) -> List[Index]:
        return [Index(x, y + 1) for x, y in self.get_possible_moves_index(b)]


# TODO: en passante, promotion
class Pawn(Piece):
    def __str__(self) -> str:
        return "P"

    def get_attacking_moves_index(self, b) -> List:
        """Can only attack left or right"""
        moves = []
        if self.color == Color.BLACK:
            y_direction = -1
        else:
            y_direction = 1
        # attack
        if (
            is_index_valid(self.x - 1, self.y + y_direction)
            and self.get_relative_index(b, -1, y_direction)
            and self.color
            is not self.get_relative_index_color(b, -1, y_direction)
        ):
            moves.append(Index(self.x - 1, self.y + y_direction))
        # attack
        if (
            is_index_valid(self.x + 1, self.y + y_direction)
            and self.get_relative_index(b, 1, y_direction)
            and self.color
            is not self.get_relative_index_color(b, 1, y_direction)
        ):
            moves.append(Index(self.x + 1, self.y + y_direction))
        return moves

    def get_possible_moves_index(self, b) -> List[Index]:
        moves = []
        if self.color == Color.BLACK:
            y_direction = -1
        else:
            y_direction = 1

        # if not blocked, move forward
        if not self.get_relative_index(b, 0, y_direction):
            moves.append(Index(self.x, self.y + y_direction))

        # attack
        if (
            is_index_valid(self.x - 1, self.y + y_direction)
            and self.get_relative_index(b, -1, y_direction)
            and self.color
            is not self.get_relative_index_color(b, -1, y_direction)
        ):
            moves.append(Index(self.x - 1, self.y + y_direction))
        # attack
        if (
            is_index_valid(self.x + 1, self.y + y_direction)
            and self.get_relative_index(b, 1, y_direction)
            and self.color
            is not self.get_relative_index_color(b, 1, y_direction)
        ):
            moves.append(Index(self.x + 1, self.y + y_direction))

        # if not blocked, move forward
        if self.color == Color.WHITE:
            if (
                1 == self.y
                and not self.get_relative_index(b, 0, y_direction)
                and not self.get_relative_index(b, 0, 2 * y_direction)
            ):
                moves.append(Index(self.x, self.y + 2 * y_direction))
        else:
            if (
                6 == self.y
                and not self.get_relative_index(b, 0, y_direction)
                and not self.get_relative_index(b, 0, 2 * y_direction)
            ):
                moves.append(Index(self.x, self.y + 2 * y_direction))

        return moves

    def promote(self):
        # phoenix time
        pass


class Rook(Piece):
    def __str__(self) -> str:
        return "R"

    def get_possible_moves_index(self, b) -> List:
        return []


def check_line_for_pieces(
    b,
    x: int,
    y: int,
    color: Color,
    x_mult: int = 0,
    y_mult: int = 0,
    max_depth: int = 8,
) -> List[Index]:
    """Return valid moves in a straight line. Multiplier may be used to
    manipulate application of iterator to index values
    """
    o = []
    for i in range(1, max_depth):
        index_x = x + i * x_mult
        index_y = y + i * y_mult
        if is_index_valid(index_x, index_y):
            piece = get_index(b, index_x, index_y)
            if piece:
                # blocked by own color
                if piece.color == color:
                    break
                # attack
                else:
                    o.append(Index(index_x, index_y))
                    break
            else:
                o.append(Index(index_x, index_y))
        else:
            break

    return o


def diagonal(b, x: int, y: int, color, max_depth: int = 8) -> List[Index]:
    out = []

    # up right
    out.extend(
        check_line_for_pieces(
            b, x, y, color, x_mult=1, y_mult=1, max_depth=max_depth
        )
    )

    # down right
    out.extend(
        check_line_for_pieces(
            b, x, y, color, x_mult=1, y_mult=-1, max_depth=max_depth
        )
    )

    # down left
    out.extend(
        check_line_for_pieces(
            b, x, y, color, x_mult=-1, y_mult=-1, max_depth=max_depth
        )
    )

    # up left
    out.extend(
        check_line_for_pieces(
            b, x, y, color, x_mult=-1, y_mult=1, max_depth=max_depth
        )
    )
    return out


def perpendicular(
    b, x: int, y: int, color: Color, max_depth: int = 8
) -> List[Index]:

    out = []

    # up
    out.extend(
        check_line_for_pieces(b, x, y, color, y_mult=1, max_depth=max_depth)
    )

    # down
    out.extend(
        check_line_for_pieces(b, x, y, color, y_mult=-1, max_depth=max_depth)
    )

    # left
    out.extend(
        check_line_for_pieces(b, x, y, color, x_mult=-1, max_depth=max_depth)
    )

    # right
    out.extend(
        check_line_for_pieces(b, x, y, color, x_mult=1, max_depth=max_depth)
    )
    return out


class Bishop(Piece):
    def __str__(self) -> str:
        return "B"

    def get_possible_moves_index(self, b) -> List[Index]:
        return diagonal(b, self.x, self.y, self.color)


class Castle(Piece):
    def __str__(self) -> str:
        return "C"

    def get_possible_moves_index(self, b) -> List[Index]:
        return perpendicular(b, self.x, self.y, self.color)


class King(Piece):
    def __str__(self) -> str:
        return "K"

    def in_check(self, b, p) -> bool:
        """Verify if king is in check

        param b: board object, required
        param p: opposite color player object
        """
        if p.color == self.color:
            raise ValueError("Need opposite player to verify checkness")
        return p.is_attacking_index(Index(self.x, self.y))

    def get_possible_moves_index(self, b) -> List[Index]:
        out = perpendicular(b, self.x, self.y, self.color, max_depth=1)
        out.extend(diagonal(b, self.x, self.y, self.color, max_depth=1))
        for move in out:
            if b.is_under_attack(move, get_other_color(self.color)):
                out.remove(move)
        return out


class Queen(Piece):
    def __str__(self) -> str:
        return "Q"

    def get_possible_moves_index(self, b) -> List[Index]:
        out = perpendicular(b, self.x, self.y, self.color)
        out.extend(diagonal(b, self.x, self.y, self.color))
        return out


# For type hints
AllPieces = Union[King, Queen, Castle, Rook, Bishop, Pawn, Piece]


class Board:
    def __init__(self, pieces: List[AllPieces]):
        self.board: List[List]
        self.board = [[None for _ in range(8)] for _ in range(8)]
        for piece in pieces:
            self.init_piece(piece, Column(piece.x), piece.y)

    def init_piece(self, piece, x: Column, y: int):
        index_valid_or_raise(x, y)
        self.board[x][y] = piece

    def is_index_under_attack(self, index: Index, attacking_color: Color):
        pass

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
        """Add color and stuff"""
        fill = "."

        def color(string):
            if not string:
                return fill
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
            arr.append(
                "{} {}".format(self.to_color(str(8 - i) + "|", "BLUE"), line)
            )
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


class Player:
    """Represents one side, used to track the location of pieces for iterating
    over, rather than iterating over the entire board
    """

    def __init__(self, color: Color):
        self.index_list: List[Index] = []
        self.color: Color = color

    def get_score(self, board: Board):
        """Intended for player strategy"""
        pass

    def is_attacking_index(self, b: Board, index: Index):
        for index in self.index_list:
            piece = b.board[index.x][index.y]
            for move in piece.get_attacking_moves_index(b):
                if index in move:
                    return True
        return False

    def set_piece_index(self, index: Index):
        """TODO: ordering? LRU vs MRU"""
        self.index_list.append(index)

    def remove_piece_index(self, index: Index):
        """Remove index from list"""
        self.index_list.remove(index)

    def update_piece_index(self, piece: Piece, new_index: Index):
        self.remove_piece_index(Index(piece.x, piece.y))
        self.set_piece_index(new_index)
