import time
import copy
import random
from enum import Enum, IntEnum
from typing import Union, List, Any, Tuple
from collections import namedtuple

import uci

Index = namedtuple("Index", ("x", "y"))
Position = namedtuple("Position", ("x", "y"))
INF = 1 << 9
NINF = 1 >> 9


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


class Row(IntEnum):
    """Index the array using enums

    reference A1 on the board using:
    ```
    board[Column.A, Row._1]
    ```
    """

    _1 = 0
    _2 = 1
    _3 = 2
    _4 = 3
    _5 = 4
    _6 = 5
    _7 = 6
    _8 = 7


piece_str_to_column = {
    "a": Column.A,
    "b": Column.B,
    "c": Column.C,
    "d": Column.D,
    "e": Column.E,
    "f": Column.F,
    "g": Column.G,
    "h": Column.H,
}

piece_str_to_row = {
    "1": Row._1,
    "2": Row._2,
    "3": Row._3,
    "4": Row._4,
    "5": Row._5,
    "6": Row._6,
    "7": Row._7,
    "8": Row._8,
}

piece_column_to_str = {
    Column.A: "a",
    Column.B: "b",
    Column.C: "c",
    Column.D: "d",
    Column.E: "e",
    Column.F: "f",
    Column.G: "g",
    Column.H: "h",
}

piece_row_to_str = {
    Row._1: "1",
    Row._2: "2",
    Row._3: "3",
    Row._4: "4",
    Row._5: "5",
    Row._6: "6",
    Row._7: "7",
    Row._8: "8",
}

class IndexType(IntEnum):
    # King may not move into defended Indexes
    # one piece may defend another of the same color
    DEFENDED = 1

    # Possible moves for a piece
    ATTACKED = 2

    ALL = 3


class Color(Enum):
    BLACK = 1
    WHITE = 2


def is_index_valid(index: Index) -> bool:
    return index.x >= 0 and index.x < 8 and index.y >= 0 and index.y < 8


def index_valid_or_raise(index: Index):
    if not is_index_valid(index):
        raise ValueError(f"invalid index {index}")


def get_index(b, index: Index):
    return b.board[index.x][index.y]


def get_index_distance(i1: Index, i2: Index) -> Index:
    return Index(abs(i1.x - i2.x), abs(i1.y - i2.y))


def get_other_color(color: Color):
    if Color.BLACK == color:
        return Color.WHITE
    elif Color.WHITE == color:
        return Color.BLACK
    else:
        raise ValueError("Invalid color")


class Piece:
    """Base class for all pieces

    param index: coordinates in array
    param color: which team

    The following creates a new black Piece on A1 and moves it to H2
    ```
    a = Piece(Column.A, Row._1, BLACK)
    a.move_to_index(Column.H, Row._2)
    ```
    """

    value = None
    __slots__ = ["index", "color", "has_moved"]

    def __init__(self, x: Column, y: Row, color: Color):
        self.index = Index(x, y)
        index_valid_or_raise(self.index)
        self.color = color
        self.has_moved = False

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return (
                self.index == other.index
                and self.color == other.color
                and self.has_moved == other.has_moved
            )
        return False

    def __hash__(self):
        return hash((self.index, self.color, self.has_moved))

    def in_check(self, b, player, other_player) -> bool:
        raise AttributeError(
            f"Attempting to verify checkness for {self.color} "
            f"at {self.index} is of type {type(self)}\n{b}"
        )

    def diff(self, other):
        if not isinstance(other, type(self)):
            print("diff type")

        if not self.index == other.index:
            print("diff index")
        if not self.color == other.color:
            print("diff color")
        if not self.has_moved == other.has_moved:
            print("has moved")
        return self == other

    def get_possible_moves_index(
        self,
        b,
        player=None,
        other_player=None,
    ) -> List[Index]:
        """Get list of available moves by this piece"""
        raise NotImplementedError()

    def get_attacking_moves_index(
        self, b, player=None, other_player=None
    ) -> List[Index]:
        """Get list of attacking moves by this pieces

        This is identical to get_attacking_moves_index() for all pieces except
        Pawn, which has asymetric moves and attack positions
        """
        # TODO: implement this by checking player index rather than returning
        # objects?
        return self.get_possible_moves_index(
            b, player=player, other_player=other_player
        )

    def get_defended_moves_index(self, b, *_args) -> List[Index]:
        """Indices that the king may not move into"""
        raise NotImplementedError()

    def __str__(self) -> str:
        """For testing"""
        return "X"

    def is_relative_index_valid(self, x: int, y: int) -> bool:
        """Check validity of index relative to current position"""
        return is_index_valid(Index(self.index.x + x, self.index.y + y))

    def relative_index_valid_or_raise(self, x: int, y: int):
        """Check validity and raise if invalid"""
        index_valid_or_raise(Index(self.index.x + x, self.index.y + y))

    def move_to_index(self, index: Index) -> None:
        index_valid_or_raise(index)
        self.index = index
        self.has_moved = True

    def move_to_relative_index(self, x: int, y: int) -> None:
        self.move_to_index(Index(self.index.x + x, self.index.y + y))

    def get_relative_index(self, b, x: int, y: int):
        return b.board[self.index.x + x][self.index.y + y]

    def get_relative_index_color(self, b, x: int, y: int):
        """Get color of piece"""
        piece = self.get_relative_index(b, x, y)
        if piece:
            return piece.color


# TODO: en passante
class Pawn(Piece):
    value = 1

    def __str__(self) -> str:
        return "♙" if self.color == Color.WHITE else "♟︎"

    def get_attacking_moves_index(self, b, *_args) -> List:
        """Attack left or right"""
        moves = []
        if self.color == Color.BLACK:
            y_direction = -1
        else:
            y_direction = 1

        # attack
        if (
            self.is_relative_index_valid(-1, y_direction)
            and self.get_relative_index(b, -1, y_direction)
            and self.color
            is not self.get_relative_index_color(b, -1, y_direction)
        ):
            moves.append(Index(self.index.x - 1, self.index.y + y_direction))
        # attack
        if (
            self.is_relative_index_valid(1, y_direction)
            and self.get_relative_index(b, 1, y_direction)
            and self.color
            is not self.get_relative_index_color(b, 1, y_direction)
        ):
            moves.append(Index(self.index.x + 1, self.index.y + y_direction))
        return moves

    def get_defended_moves_index(self, b, *args) -> List[Index]:
        """Defend left or right"""

        moves = []
        if self.color == Color.BLACK:
            y_direction = -1
        else:
            y_direction = 1

        index_l = Index(self.index.x + 1, self.index.y + y_direction)
        index_r = Index(self.index.x - 1, self.index.y + y_direction)

        # defend
        if is_index_valid(index_l):
            moves.append(index_l)
        # defend
        if is_index_valid(index_r):
            moves.append(index_r)
        return moves

    def get_possible_moves_index(
        self, b, player=None, other_player=None
    ) -> List[Index]:
        moves = self.get_attacking_moves_index(b)
        if self.color == Color.BLACK:
            y_direction = -1
        else:
            y_direction = 1

        # if not blocked, move forward
        if not self.get_relative_index(b, 0, y_direction):
            moves.append(Index(self.index.x, self.index.y + y_direction))

        # if not blocked, move forward
        if self.color == Color.WHITE:
            if (
                1 == self.index.y
                and not self.get_relative_index(b, 0, y_direction)
                and not self.get_relative_index(b, 0, 2 * y_direction)
            ):
                moves.append(
                    Index(self.index.x, self.index.y + 2 * y_direction)
                )
        else:
            if (
                6 == self.index.y
                and not self.get_relative_index(b, 0, y_direction)
                and not self.get_relative_index(b, 0, 2 * y_direction)
            ):
                moves.append(
                    Index(self.index.x, self.index.y + 2 * y_direction)
                )

        return moves

    def promote(self):
        # phoenix time
        pass


class Knight(Piece):
    value = 3
    __slots__ = ["index", "color", "has_moved", "potential_cache"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.potential_cache = None

    def __str__(self) -> str:
        return "♘" if self.color == Color.WHITE else "♞"

    def move_to_index(self, *args, **kwargs) -> None:
        super().move_to_index(*args, **kwargs)
        self.potential_cache = None

    def get_potentials(self) -> List[Index]:

        # caching potentials cuts time in this function by 80%
        # this function is currently ~6.5% of total runtime
        if self.potential_cache:
            return self.potential_cache
        legal = []
        x = self.index.x
        y = self.index.y
        possible = [
            Index(x + 1, y + 2),
            Index(x - 1, y + 2),
            Index(x - 1, y - 2),
            Index(x + 1, y - 2),
            Index(x + 2, y + 1),
            Index(x - 2, y + 1),
            Index(x - 2, y - 1),
            Index(x + 2, y - 1),
        ]
        for index in possible:
            if is_index_valid(index):
                legal.append(index)
        self.potential_cache = legal
        return legal

    def get_possible_moves_index(
        self, b, player=None, other_player=None
    ) -> List[Index]:
        out = []
        for index in self.get_potentials():
            value = b.board[index.x][index.y]
            if not value or self.color != value.color:
                out.append(index)
        return out

    def get_defended_moves_index(self, b, *_args) -> List[Index]:
        return self.get_potentials()


def get_indices_in_line(
    b,
    index: Index,
    color: Color,
    o: List,
    x_mult: int = 0,
    y_mult: int = 0,
    max_depth: int = 7,
    index_type: IndexType = IndexType.ATTACKED,
) -> List[Index]:
    """Return valid moves in a straight line. Multiplier may be used to
    manipulate application of iterator to index values

    param b: board
    param x, y: starting index
    param x_mult: multiplier maps iterable to index for y index
    param y_mult: multiplier maps iterable to index for y index

    Example:
    ```
    get_indices_in_line(b, 1, 1, color)
    ```
    """
    for i in range(1, max_depth):
        index_x = index.x + i * x_mult
        index_y = index.y + i * y_mult

        # Inlined is_index_valid saves ~1s from benchmark
        if index_x >= 0 and index_x < 8 and index_y >= 0 and index_y < 8:
            derived_index = Index(index_x, index_y)

            piece = b.board[index_x][index_y]
            if piece:
                # blocked by own color
                if piece.color == color:
                    if index_type == IndexType.DEFENDED:
                        o.append(derived_index)
                # attack
                else:
                    o.append(derived_index)
                break
            else:
                o.append(derived_index)
        else:
            break
    return o


def diagonal(
    b,
    index: Index,
    color,
    out: List,
    max_depth: int = 7,
    index_type: IndexType = IndexType.ATTACKED,
) -> List[Index]:

    get_indices_in_line(
        b,
        index,
        color,
        out,
        x_mult=1,
        y_mult=1,
        max_depth=max_depth,
        index_type=index_type,
    )

    get_indices_in_line(
        b,
        index,
        color,
        out,
        x_mult=1,
        y_mult=-1,
        max_depth=max_depth,
        index_type=index_type,
    )
    get_indices_in_line(
        b,
        index,
        color,
        out,
        x_mult=-1,
        y_mult=-1,
        max_depth=max_depth,
        index_type=index_type,
    )
    get_indices_in_line(
        b,
        index,
        color,
        out,
        x_mult=-1,
        y_mult=1,
        max_depth=max_depth,
        index_type=index_type,
    )
    return out


def perpendicular(
    b,
    index: Index,
    color: Color,
    out: List,
    max_depth: int = 7,
    index_type: IndexType = IndexType.ATTACKED,
) -> List[Index]:

    out = []

    # up
    get_indices_in_line(
        b,
        index,
        color,
        out,
        y_mult=1,
        max_depth=max_depth,
        index_type=index_type,
    )

    # down
    get_indices_in_line(
        b,
        index,
        color,
        out,
        y_mult=-1,
        max_depth=max_depth,
        index_type=index_type,
    )

    # left
    get_indices_in_line(
        b,
        index,
        color,
        out,
        x_mult=-1,
        max_depth=max_depth,
        index_type=index_type,
    )

    # right
    get_indices_in_line(
        b,
        index,
        color,
        out,
        x_mult=1,
        max_depth=max_depth,
        index_type=index_type,
    )
    return out


class Bishop(Piece):
    value = 3

    def __str__(self) -> str:
        return "♗" if self.color == Color.WHITE else "♝"

    def get_possible_moves_index(
        self, b, player=None, other_player=None
    ) -> List[Index]:
        return diagonal(b, self.index, self.color, [])

    def get_defended_moves_index(self, b, *args) -> List[Index]:
        return diagonal(
            b, self.index, self.color, [], index_type=IndexType.DEFENDED
        )


class Rook(Piece):
    value = 5

    def __str__(self) -> str:
        return "♖" if self.color == Color.WHITE else "♜"

    def get_possible_moves_index(
        self, b, player=None, other_player=None
    ) -> List[Index]:
        return perpendicular(b, self.index, self.color, [])

    def get_defended_moves_index(self, b, *args) -> List[Index]:
        return perpendicular(
            b, self.index, self.color, [], index_type=IndexType.DEFENDED
        )


class King(Piece):
    def __str__(self) -> str:
        return "♔" if self.color == Color.WHITE else "♚"

    def get_attacking_moves_index(
        self, board, player=None, other_player=None
    ) -> List[Index]:
        """Get list of attacking moves by this pieces

        This is identical to get_attacking_moves_index() for all pieces except
        Pawn, which has asymetric moves and attack positions
        """
        if other_player.color == self.color:
            raise ValueError("Need opposite player to verify checkness")
        out = perpendicular(board, self.index, self.color, [], max_depth=2)
        out = diagonal(board, self.index, self.color, out, max_depth=2)
        return list(
            set(out) - set(other_player.get_defended_indices(board, player))
        )

    def in_check(self, b, player, other_player) -> bool:
        """Verify if king is in check

        param b: board object, required
        param p: opposite color player object
        """
        if other_player.color == self.color:
            raise ValueError("Need opposite player to verify checkness")
        return other_player.is_defending_index(b, self.index, player)

    def get_possible_moves_index(
        self, board, player=None, other_player=None
    ) -> List[Index]:
        """Getting possible moves for the king requires checking which indices
        the other player is attacking.
        """
        if other_player.color == self.color:
            raise ValueError("Need opposite player to verify checkness")
        out = perpendicular(board, self.index, self.color, [], max_depth=2)
        out = diagonal(board, self.index, self.color, out, max_depth=2)

        # castle
        if not self.has_moved and not self.in_check(
            board, player, other_player
        ):
            if Color.WHITE == self.color:
                # KCastle
                k_rook = get_index(board, Index(Column.H, Row._1))

                # Check that kingside rook hasn't moved and squares are open
                # and not under attack
                indices = [Index(Column.F, Row._1), Index(Column.G, Row._1)]
                if k_rook and not k_rook.has_moved:
                    legal = True
                    for index in indices:
                        if get_index(
                            board, index
                        ) or other_player.is_attacking_index(
                            board, index, player
                        ):
                            legal = False
                            break

                    if not isinstance(k_rook, Rook):
                        raise ValueError(
                            "Not rook: this shouldn't be possible"
                        )
                    if legal:
                        out.append(Index(Column.G, Row._1))

                # QCastle
                q_rook = get_index(board, Index(Column.A, Row._1))

                indices = [Index(Column.C, Row._1), Index(Column.D, Row._1)]
                if q_rook and not q_rook.has_moved:
                    legal = True
                    for index in indices:
                        if get_index(
                            board, index
                        ) or other_player.is_attacking_index(
                            board, index, player
                        ):
                            legal = False
                            break
                    if get_index(board, Index(Column.B, Row._1)):
                        legal = False

                    if not isinstance(q_rook, Rook):
                        raise ValueError(
                            "Not rook: this shouldn't be possible"
                        )
                    if legal:
                        out.append(Index(Column.C, Row._1))

            elif Color.BLACK == self.color:
                # KCastle
                k_rook = get_index(board, Index(Column.H, Row._8))
                q_rook = get_index(board, Index(Column.A, Row._8))

                # Check that kingside rook hasn't moved and squares are open
                # and not under attack
                indices = [Index(Column.F, Row._8), Index(Column.G, Row._8)]
                if k_rook and not k_rook.has_moved:
                    legal = True
                    for index in indices:
                        if get_index(
                            board, index
                        ) or other_player.is_attacking_index(
                            board, index, player
                        ):
                            legal = False
                            break

                    if not isinstance(k_rook, Rook):
                        raise ValueError(
                            "Not rook: this shouldn't be possible"
                        )
                    if legal:
                        out.append(Index(Column.G, Row._8))

                # QCastle
                indices = [Index(Column.C, Row._8), Index(Column.D, Row._8)]
                if q_rook and not q_rook.has_moved:
                    legal = True
                    for index in indices:
                        if get_index(
                            board, index
                        ) or other_player.is_attacking_index(
                            board, index, player
                        ):
                            legal = False
                            break
                    if get_index(board, Index(Column.B, Row._8)):
                        legal = False

                    if not isinstance(q_rook, Rook):
                        raise ValueError(
                            "Not rook: this shouldn't be possible"
                        )
                    if legal:
                        out.append(Index(Column.C, Row._8))
        return list(
            set(out) - set(other_player.get_defended_indices(board, player))
        )

    def get_defended_moves_index(self, board, player) -> List[Index]:
        if player.color == self.color:
            raise ValueError("Need opposite player to verify checkness")
        out = perpendicular(
            board,
            self.index,
            self.color,
            [],
            max_depth=2,
            index_type=IndexType.DEFENDED,
        )
        out = diagonal(
            board,
            self.index,
            self.color,
            out,
            max_depth=2,
            index_type=IndexType.DEFENDED,
        )
        return out


class Queen(Piece):
    value = 9

    def __str__(self) -> str:
        return "♕" if self.color == Color.WHITE else "♛"

    def get_possible_moves_index(
        self, b, player=None, other_player=None
    ) -> List[Index]:
        out = perpendicular(b, self.index, self.color, [])
        out = diagonal(b, self.index, self.color, out)
        return out

    def get_defended_moves_index(self, b, *_args) -> List[Index]:
        out = perpendicular(
            b, self.index, self.color, [], index_type=IndexType.DEFENDED
        )
        out = diagonal(
            b, self.index, self.color, out, index_type=IndexType.DEFENDED
        )
        return out


piece_notation_to_class = {
    "K": King,
    "Q": Queen,
    "N": Knight,
    "B": Bishop,
    "R": Rook,
    "P": Pawn,
}


# For type hints
AllPieces = Union[King, Queen, Rook, Bishop, Pawn, Piece]


class Board:
    __slots__ = ["board"]

    def __init__(self, pieces: List):

        self.board: List[List]
        self.board = [[None for _ in range(8)] for _ in range(8)]
        for piece in copy.deepcopy(pieces):
            self.init_piece(piece, piece.index)

    def __eq__(self, other):
        for left, right in zip(self.board, other.board):
            for l_piece, r_piece in zip(left, right):
                if l_piece != r_piece:
                    return False
        return True

    def diff(self, other):
        for left, right in zip(self.board, other.board):
            for l_piece, r_piece in zip(left, right):
                if l_piece != r_piece:
                    return (l_piece, r_piece)

    def init_piece(self, piece, index: Index):
        index_valid_or_raise(index)
        self.board[piece.index.x][piece.index.y] = piece

    def is_index_under_attack(self, player, index: Index, other_player):
        """Attacking indexes are ones which a king may not move into"""
        player.is_attacking_index(player, self, index, other_player)

    def is_defending_index(self, player, index: Index, other_player):
        """Defended indexes are ones which a king may not move into"""
        player.is_defending_index(self, index, other_player)

    def get_index(self, index: Index):
        return self.board[index.x][index.y]

    def set_index(self, index: Index, piece: Piece) -> None:
        self.board[index.x][index.y] = piece

    def clear_index(self, index: Index) -> None:
        self.board[index.x][index.y] = None

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
        rows = []
        for c in [7, 6, 5, 4, 3, 2, 1, 0]:
            row = []
            for r in [
                Column.A,
                Column.B,
                Column.C,
                Column.D,
                Column.E,
                Column.F,
                Column.G,
                Column.H,
            ]:
                row.append(color(self.board[r][c]))
            rows.append(" ".join(row))
        return "\n".join(rows)

    def __str__(self) -> str:
        return self.to_string()



def indices_to_cmd(src_index: Index, dst_index: Index):
    return {
        "start": {
            "file": piece_column_to_str[src_index.x],
            "rank": piece_row_to_str[src_index.y],
        },
        "end": {
            "file": piece_column_to_str[dst_index.x],
            "rank": piece_row_to_str[dst_index.y],
        },
        "promote": None,
    }


def indices_to_uci_str(src_index: Index, dst_index: Index) -> str:
    return "{}{}{}{}".format(
        piece_column_to_str[src_index.x],
        piece_row_to_str[src_index.y],
        piece_column_to_str[dst_index.x],
        piece_row_to_str[dst_index.y],
    )


def cmd_to_index(cmd: dict):
    """Map command notation to index"""
    file = piece_str_to_column[cmd["file"]]
    rank = piece_str_to_row[cmd["rank"]]
    return Index(file, rank)


class Player:
    """Represents one side, used to track the location of pieces for iterating
    over, rather than iterating over the entire board
    """

    __slots__ = ["king_index", "index_list", "color"]

    def __init__(self, color: Color, pieces: List):
        # Seed randomness for move selection
        self.king_index: Index
        self.index_list: List[Index] = []
        self.color: Color = color

        random.seed()
        for piece in pieces:
            if piece.color is not self.color:
                raise ValueError("Invalid piece color added to player")
            self.set_piece_index(piece.index)
            # Save king coordinate
            if isinstance(piece, King):
                self.king_index = piece.index

    def __eq__(self, other):
        """do_move() and undo_move() change list order, but we don't care:
        use set comparasin

        TODO: Should the index_list just be a set?
        """
        if isinstance(other, type(self)):
            return (
                self.king_index == other.king_index
                and self.color == other.color
                and (set(self.index_list) == set(other.index_list))
            )
        return False

    def diff(self, other):
        """do_move() and undo_move() change list order, but we don't care:
        use set comparasin

        TODO: Should the index_list just be a set?
        """
        if not isinstance(other, type(self)):
            print("diff type")

        if self.king_index != other.king_index:
            print("diff king index")
        if self.color != other.color:
            print("diff color")
        if set(self.index_list) != set(other.index_list):
            print(
                "diff list:\n{}\n{}".format(
                    set(self.index_list), set(other.index_list)
                )
            )
            print(
                "diff list diff:{}".format(
                    set(self.index_list) - set(other.index_list)
                )
            )
            print(
                "diff list diff:{}".format(
                    set(other.index_list) - set(self.index_list)
                )
            )
        return self == other

    def in_check(self, b, other_player) -> bool:
        return b.get_index(self.king_index).in_check(b, self, other_player)

    def get_best_move(self, board: Board, other_player, depth=3) -> str:
        """Current strategy: material

        TODO: something is wrong here or in minimax
        """
        possible_moves = self.get_possible_moves_index(board, other_player)
        best_move = []
        node_count = 0
        move_score = 0
        start = time.time()
        for move in possible_moves:
            undo = self.do_move(
                indices_to_cmd(move[0], move[1]), board, other_player
            )
            move_score, count = self.minimax(
                board, other_player, depth - 1, True
            )
            node_count = node_count + count
            self.undo_move(
                indices_to_cmd(move[0], move[1]), board, other_player, undo
            )
            print(
                "nodes: {} move score: {} ({}, {})".format(
                    count, move_score, move[0], move[1]
                )
            )

            # First score add
            if not best_move:
                best_move.append((move_score, move))

            # Better score replace
            elif move_score > best_move[0][0]:
                del best_move
                best_move = [(move_score, move)]

            # Equivalent score add
            elif move_score == best_move[0][0]:
                best_move.append((move_score, move))
        total_time = time.time() - start
        nps = node_count / total_time
        print(
            f"nps: {nps:.0f} evaluated {node_count} nodes in {total_time:.2f}s"
        )
        uci.uci(f"info nps {nps:.0f}")
        uci.uci(f"info depth {depth:.0f}")
        uci.uci(f"info nodes {node_count}")
        uci.uci(f"info score cp {move_score*100}")

        # Randomly select from equivalent bestmoves
        match = best_move[0][0]
        print("selecting between scores of value: {}".format(match))
        for move in best_move:
            if match != move[0]:
                raise ValueError("Scores don't match")
        select = random.randrange(len(best_move))
        print("best moves")
        print(best_move)
        moves = best_move[select]
        return indices_to_uci_str(moves[1][0], moves[1][1])

    def value(self, board: Board, other_player) -> int:
        """Difference in material"""
        return self.get_material(self, board) - self.get_material(
            other_player, board
        )

    def minimax(
        self, board: Board, other_player, depth: int, maximizing_player: bool
    ) -> Tuple[int, int]:

        if maximizing_player:
            # Base case
            if 0 == depth:
                return (self.value(board, other_player), 1)
            nodes = 0

            possible_moves = self.get_possible_moves_index(board, other_player)
            value = NINF
            for src, dst in possible_moves:
                undo = self.do_move(
                    indices_to_cmd(src, dst), board, other_player
                )
                minimax, count = self.minimax(
                    board, other_player, depth - 1, False
                )
                value = max(value, minimax)
                self.undo_move(
                    indices_to_cmd(src, dst), board, other_player, undo
                )
                nodes = nodes + count
            return (value, nodes)
        else:
            # Base case
            if 0 == depth:
                return (other_player.value(board, self), 1)
            nodes = 0

            possible_moves = other_player.get_possible_moves_index(board, self)
            value = INF
            for src, dst in possible_moves:
                undo = other_player.do_move(
                    indices_to_cmd(src, dst), board, self
                )
                minimax, count = other_player.minimax(
                    board, self, depth - 1, True
                )
                value = min(value, minimax)
                other_player.undo_move(
                    indices_to_cmd(src, dst), board, self, undo
                )
                nodes = nodes + count
            return (value, nodes)

    def prune_checking_moves(
        self, moves: List[Tuple[Index, Index]], b, other_player
    ) -> List[Tuple[Index, Index]]:
        """Remove moves that could possibly induce check"""

        unpruned = []

        # Discovery on own turn can only happen diagonally and perpendicularly
        # Don't check for pieces that don't fall in line with king
        out = []
        perpendicular(
            b, self.king_index, self.color, out, index_type=IndexType.DEFENDED
        )
        diagonal(
            b, self.king_index, self.color, out, index_type=IndexType.DEFENDED
        )
        in_check = self.in_check(b, other_player)
#        print(f"in check: {in_check}")
        for src, dst in moves:
            if not in_check and src not in out:
                unpruned.append((src, dst))
            else:
                undo = self.do_move(indices_to_cmd(src, dst), b, other_player)

                # Remove move from list if it induces check
                if not self.in_check(b, other_player):
                    unpruned.append((src, dst))

                self.undo_move(indices_to_cmd(src, dst), b, other_player, undo)
        return unpruned

    def get_possible_moves_index(
        self, b, other_player=None
    ) -> List[Tuple[Index, Index]]:
        """Iterate over all pieces and get a list of Tuples with (src, dst)"""
        moves: List[Tuple[Index, Index]] = []

        for src in self.index_list:
            piece = b.board[src.x][src.y]
            piece_moves = piece.get_possible_moves_index(
                b, player=self, other_player=other_player
            )
            for piece in piece_moves:

                # Can't actually move to king
                if not isinstance(b.get_index(piece), King):
                    moves.append((src, piece))

        pruned = self.prune_checking_moves(moves, b, other_player)
        if not pruned:
            import pprint
            pprint.pprint(moves)
            print(b)
            raise ValueError(
                f"{self.color} has no valid moves after pruning. "
            )
        return pruned

    @staticmethod
    def get_material(player, board: Board) -> int:
        score = 0
        for index in player.index_list:
            piece = board.board[index.x][index.y]
            if not piece:
                raise ValueError(
                    "Accounting error, no piece at index: {}".format(index)
                )

            if piece.value:
                score += piece.value
        return score

    def is_attacking_index(self, b: Board, index: Index, other_player):
        return index in self.get_attacking_indices(b, other_player)

    def get_attacking_indices(self, b: Board, other_player) -> List[Index]:
        if other_player.color == self.color:
            raise ValueError("Need opposite player to verify checkness")
        out = []
        for index in self.index_list:
            piece = b.board[index.x][index.y]
            for move in piece.get_attacking_moves_index(b, self, other_player):
                out.append(move)

        # Todo: Maybe don't remove dups for detecting double check?
        return list(set(out))

    def get_defended_indices(self, b: Board, other_player) -> List[Index]:
        if other_player.color == self.color:
            raise ValueError("Need opposite player to verify checkness")
        out = []
        for piece_index in self.index_list:
            piece_obj: Piece
            piece_obj = b.board[piece_index.x][piece_index.y]
            for move in piece_obj.get_defended_moves_index(b, other_player):
                out.append(move)
        return list(set(out))

    def print_defended_indices(self, b: Board, other_player) -> None:
        print("Defended Positions:")
        print("===================")
        pieces = []
        for piece in self.get_defended_indices(b, other_player):
            pieces.append(Piece(piece.x, piece.y, Color.BLACK))
        print(Board(pieces))

    def is_defending_index(self, b: Board, index: Index, other_player) -> bool:
        if other_player.color == self.color:
            raise ValueError("Need opposite player to verify checkness")
        return index in self.get_defended_indices(b, other_player)

    def set_piece_index(self, index: Index):
        """TODO: ordering? LRU vs MRU"""
        self.index_list.append(index)

    def remove_piece_index(self, index: Index):
        """Remove index from list"""
        self.index_list.remove(index)

    def update_piece_index(self, piece: Piece, new_index: Index):
        self.remove_piece_index(piece.index)
        self.set_piece_index(new_index)

    def _verify_do_move(
        self,
        move: dict,
        board: Board,
        other_player,
        dst_index: Index,
        src_piece: Piece,
        dst_piece: Piece,
    ):
        start = move["start"]

        # Shouldn't actually take the king
        if isinstance(dst_piece, King):
            raise ValueError("Cannot take the king")

        # Check that source piece exists
        if not src_piece:
            raise ValueError(
                "No piece at {}{}\n{}".format(
                    start["file"], start["rank"], board
                )
            )
        # Check that piece is correct type
        elif move.get("piece") and not isinstance(
            src_piece, piece_notation_to_class[move["piece"]]
        ):
            raise ValueError(
                "Piece at {}{} is not of type {}".format(
                    start["file"], start["rank"], start["piece"]
                )
            )

        # Check that source piece is owned by this player
        elif src_piece.color is not self.color:
            print(board)
            raise ValueError(
                "Piece at {}{} is not {}".format(
                    start["file"], start["rank"], self.color
                )
            )

        # Get all moves the source piece can do
        moves = src_piece.get_possible_moves_index(
            board, player=self, other_player=other_player
        )

        # Check that requested destination is legal
        if dst_index not in moves:
            raise ValueError(
                f"Requested move {dst_index} for piece {src_piece} "
                f"is not in legal movelist: {moves}"
            )

        # Check that not moving to same color
        elif dst_piece and dst_piece.color is self.color:
            raise ValueError(
                "Piece {} at {} is same color({}),"
                " can't move there!".format(
                    dst_piece, dst_index, dst_piece.color
                )
            )

    def undo_castle(
        self, board: Board, other_player, dst_index: Index, rank: str, undo
    ):
        if dst_index == Index(Column.G, piece_str_to_row[rank]):
            self.undo_move(
                {
                    "start": {
                        "file": "h",
                        "rank": rank,
                    },
                    "end": {
                        "file": "f",
                        "rank": rank,
                    },
                    "promote": None,
                },
                board,
                other_player,
                undo,
            )
        elif dst_index == Index(Column.C, piece_str_to_row[rank]):
            self.undo_move(
                {
                    "start": {
                        "file": "a",
                        "rank": rank,
                    },
                    "end": {
                        "file": "d",
                        "rank": rank,
                    },
                    "promote": None,
                },
                board,
                other_player,
                undo,
            )
        else:
            raise ValueError(f"Invalid castling destination: {dst_index}")

    def do_castle(
        self, board: Board, other_player, dst_index: Index, rank: str
    ):
        """king move done, need to move the rook
        position rules are identical besides rank

        Mock user input and call do_move() without verification
        This should only ever cause recursion one level deep, since do_castle()
        is called by do_move(), but subsequent do_moves() should never call
        do_castle()
        """
        if dst_index == Index(Column.G, piece_str_to_row[rank]):
            return self.do_move(
                {
                    "start": {
                        "file": "h",
                        "rank": rank,
                    },
                    "end": {
                        "file": "f",
                        "rank": rank,
                    },
                    "promote": None,
                },
                board,
                other_player,
                verify=False,
            )
        elif dst_index == Index(Column.C, piece_str_to_row[rank]):
            return self.do_move(
                {
                    "start": {
                        "file": "a",
                        "rank": rank,
                    },
                    "end": {
                        "file": "d",
                        "rank": rank,
                    },
                    "promote": None,
                },
                board,
                other_player,
                verify=False,
            )
        else:
            raise ValueError(f"Invalid castling destination: {dst_index}")

    def do_move(
        self, move: dict, board: Board, other_player, verify=True
    ) -> dict:
        """Move piece and update accounting in board, players, and piece"""
        castle_undo = None
        start = move["start"]
        end = move["end"]

        # Source index
        src_index = cmd_to_index(start)

        # Destination index
        dst_index = cmd_to_index(end)

        # Get piece at source index
        src_piece = get_index(board, src_index)
        src_piece_has_moved = src_piece.has_moved

        # Get piece at destination index
        dst_piece = get_index(board, dst_index)

        # Skip move verification for castling - we already did that
        if verify:
            # Check for errors
            self._verify_do_move(
                move, board, other_player, dst_index, src_piece, dst_piece
            )

        # Handle taking opponent's piece
        if dst_piece is not None:

            # Remove piece from other player's index
            other_player.remove_piece_index(dst_index)

        # Pawn promotion
        if move["promote"]:
            old_src = src_piece
            src_piece = piece_notation_to_class[move["promote"].upper()](
                src_index.x, src_index.y, old_src.color
            )

            # Replace old piece
            board.set_index(src_index, src_piece)

        # Update this player's accounting
        self.update_piece_index(src_piece, dst_index)

        # Update piece accounting
        src_piece.move_to_index(dst_index)

        # Set piece to new piece
        board.set_index(dst_index, src_piece)

        # Delete the old board piece
        board.clear_index(src_index)

        # Save king coordinate
        if isinstance(src_piece, King):
            self.king_index = dst_index
            distance = get_index_distance(src_index, dst_index)

            # Castling, do rook move too, legality checked already
            if distance.x > 1:
                if Color.WHITE == self.color:
                    castle_undo = self.do_castle(
                        board, other_player, dst_index, "1"
                    )
                elif Color.BLACK == self.color:
                    castle_undo = self.do_castle(
                        board, other_player, dst_index, "8"
                    )

        return {
            "src_piece_moved": src_piece_has_moved,
            "dst_piece": dst_piece,
            "castle_undo": castle_undo,
        }

    def undo_move(self, move: dict, board: Board, other_player, undo) -> None:
        """Move piece and update accounting in board, players, and piece"""

        end = move["start"]
        start = move["end"]

        # Source index
        src_index = cmd_to_index(start)

        # Destination index
        dst_index = cmd_to_index(end)

        # Get piece at source index
        src_piece = get_index(board, src_index)
        if not src_piece:
            print(board)
            raise ValueError(f"Expected src index, {src_piece} {src_index}")

        # Handle taking opponent's piece
        if undo["dst_piece"] is not None:

            # Remove piece from other player's index
            other_player.set_piece_index(src_index)

        # Pawn promotion
        if move["promote"]:
            src_piece = Pawn(src_index.x, src_index.y, src_piece.color)

            # Replace old piece
            board.set_index(src_index, src_piece)

        # Update this player's accounting
        self.update_piece_index(src_piece, dst_index)

        # Update piece accounting
        src_piece.move_to_index(dst_index)

        # Set piece to new index
        board.set_index(dst_index, src_piece)

        if undo["dst_piece"] is not None:
            board.set_index(undo["dst_piece"].index, undo["dst_piece"])
        else:
            board.clear_index(src_index)

        # Save king coordinate
        if isinstance(src_piece, King):
            self.king_index = dst_index
            distance = get_index_distance(src_index, dst_index)

            # Castling, do rook move too, legality checked already
            if distance.x > 1:
                if Color.WHITE == self.color:
                    self.undo_castle(
                        board,
                        other_player,
                        src_index,
                        "1",
                        undo["castle_undo"],
                    )
                elif Color.BLACK == self.color:
                    self.undo_castle(
                        board,
                        other_player,
                        src_index,
                        "8",
                        undo["castle_undo"],
                    )

        # Delete the old board index
        src_piece.has_moved = undo["src_piece_moved"]

    def move(self, move: dict, board: Board, other_player):
        self.do_move(move["move"], board, other_player)
