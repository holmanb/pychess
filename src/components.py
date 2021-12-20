from enum import Enum, IntEnum
from typing import Union, List, Any
from collections import namedtuple

Index = namedtuple("Index", ("x", "y"))
Position = namedtuple("Position", ("x", "y"))


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


class IndexType(IntEnum):
    # King may not move into defended Indexes
    # one piece may defend another of the same color
    DEFENDED = 1

    # Possible moves for a piece
    ATTACKED = 2

    # Will use?
    OPEN = 3


class Color(Enum):
    BLACK = 1
    WHITE = 2


def index_to_position(index: Index) -> Position:
    return Position(Column(index.x), index.y + 1)


def position_to_index(position: Position) -> Index:
    return Index(int(position.x), position.y - 1)


def is_index_valid(index: Index) -> bool:
    return index.x >= 0 and index.x < 8 and index.y >= 0 and index.y < 8


def is_position_valid(position: Position) -> bool:
    return is_index_valid(position_to_index(position))


def index_valid_or_raise(index: Index):
    if not is_index_valid(index):
        raise ValueError(f"invalid index {index}")


def position_valid_or_raise(position: Position):
    index_valid_or_raise(position_to_index(position))


def get_index(b, index: Index):
    return b.board[index.x][index.y]


def get_position(b, position: Position):
    return get_index(b, position_to_index(position))


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
        self.index = Index(x, y - 1)
        index_valid_or_raise(self.index)
        self.color = color

    def get_position(self):
        return index_to_position(self.index)

    def get_possible_moves_index(self, _b) -> List[Index]:
        """Get list of available moves by this piece"""
        raise NotImplementedError()

    def get_attacking_moves_index(self, _b) -> List[Index]:
        """Get list of attacking moves by this piece"""
        raise NotImplementedError()

    def get_defended_moves_index(self, b, *_args) -> List[Index]:
        """Indices that the king may not move into"""
        raise NotImplementedError()

    def get_defended_moves_position(self, b, *_args) -> List[Index]:
        return list(
            map(partial(index_to_position, b), self.get_defended_moves_index)
        )

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

    def move_to_relative_index(self, x: int, y: int) -> None:
        self.move_to_index(Index(self.index.x + x, self.index.y + y))

    def move_to_position(self, pos: Position) -> None:
        """Move to board position using standard chess naming: A1-H8"""
        position_valid_or_raise(pos)
        self.move_to_index(position_to_index(pos))

    def get_relative_index(self, b, x: int, y: int):
        return get_index(b, Index(self.index.x + x, self.index.y + y))

    def get_relative_index_color(self, b, x: int, y: int):
        """Get color of piece"""
        piece = self.get_relative_index(b, x, y)
        if piece:
            return piece.color

    def get_possible_moves_position(self, b, *args) -> List[Index]:
        return [
            Index(Column(x), y + 1)
            for x, y in self.get_possible_moves_index(b, *args)
        ]

    def get_attacking_moves_position(self, b, *args) -> List[Index]:
        return [
            Index(Column(x), y + 1)
            for x, y in self.get_attacking_moves_index(b, *args)
        ]


# TODO: en passante, promotion
class Pawn(Piece):
    def __str__(self) -> str:
        return "P"

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
        # defend
        if self.is_relative_index_valid(-1, y_direction):
            moves.append(Index(self.index.x - 1, self.index.y + y_direction))
        # defend
        if self.is_relative_index_valid(1, y_direction):
            moves.append(Index(self.index.x + 1, self.index.y + y_direction))
        return moves

    def get_possible_moves_index(self, b) -> List[Index]:
        moves = []
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

        moves.extend(self.get_attacking_moves_index(b))
        return moves

    def promote(self):
        # phoenix time
        pass


class Knight(Piece):
    def __str__(self) -> str:
        return "R"

    def get_potentials(self) -> List[Index]:
        return [
            Index(self.index.x + 1, self.index.y + 2),
            Index(self.index.x - 1, self.index.y + 2),
            Index(self.index.x - 1, self.index.y - 2),
            Index(self.index.x + 1, self.index.y - 2),
            Index(self.index.x + 2, self.index.y + 1),
            Index(self.index.x - 2, self.index.y + 1),
            Index(self.index.x - 2, self.index.y - 1),
            Index(self.index.x + 2, self.index.y - 1),
        ]

    def get_possible_moves_index(self, b) -> List[Index]:
        out = []
        for index in self.get_potentials():
            if is_index_valid(index):
                value = get_index(b, index)
                if self.color != value.color:
                    out.append(index)
        return out

    def get_defended_moves_index(self, b, *_args) -> List[Index]:
        out = []
        for index in self.get_potentials():
            if is_index_valid(index):
                out.append(index)
        return out


def get_indices_in_line(
    b,
    index: Index,
    color: Color,
    x_mult: int = 0,
    y_mult: int = 0,
    max_depth: int = 8,
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
    o = []
    for i in range(1, max_depth):
        index_x = index.x + i * x_mult
        index_y = index.y + i * y_mult
        derived_index = Index(index_x, index_y)
        if is_index_valid(derived_index):
            piece = get_index(b, derived_index)
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
    max_depth: int = 8,
    index_type: IndexType = IndexType.ATTACKED,
) -> List[Index]:
    out = []

    # up right
    out.extend(
        get_indices_in_line(
            b,
            index,
            color,
            x_mult=1,
            y_mult=1,
            max_depth=max_depth,
            index_type=index_type,
        )
    )

    # down right
    out.extend(
        get_indices_in_line(
            b,
            index,
            color,
            x_mult=1,
            y_mult=-1,
            max_depth=max_depth,
            index_type=index_type,
        )
    )

    # down left
    out.extend(
        get_indices_in_line(
            b,
            index,
            color,
            x_mult=-1,
            y_mult=-1,
            max_depth=max_depth,
            index_type=index_type,
        )
    )

    # up left
    out.extend(
        get_indices_in_line(
            b,
            index,
            color,
            x_mult=-1,
            y_mult=1,
            max_depth=max_depth,
            index_type=index_type,
        )
    )
    return out


def perpendicular(
    b,
    index: Index,
    color: Color,
    max_depth: int = 8,
    index_type: IndexType = IndexType.ATTACKED,
) -> List[Index]:

    out = []

    # up
    out.extend(
        get_indices_in_line(
            b,
            index,
            color,
            y_mult=1,
            max_depth=max_depth,
            index_type=index_type,
        )
    )

    # down
    out.extend(
        get_indices_in_line(
            b,
            index,
            color,
            y_mult=-1,
            max_depth=max_depth,
            index_type=index_type,
        )
    )

    # left
    out.extend(
        get_indices_in_line(
            b,
            index,
            color,
            x_mult=-1,
            max_depth=max_depth,
            index_type=index_type,
        )
    )

    # right
    out.extend(
        get_indices_in_line(
            b,
            index,
            color,
            x_mult=1,
            max_depth=max_depth,
            index_type=index_type,
        )
    )
    return out


class Bishop(Piece):
    def __str__(self) -> str:
        return "B"

    def get_possible_moves_index(self, b) -> List[Index]:
        return diagonal(b, self.index, self.color)

    def get_defended_moves_index(self, b, *args) -> List[Index]:
        return diagonal(
            b, self.index, self.color, index_type=IndexType.DEFENDED, *args
        )


class Rook(Piece):
    def __str__(self) -> str:
        return "C"

    def get_possible_moves_index(self, b) -> List[Index]:
        return perpendicular(b, self.index, self.color)

    def get_defended_moves_index(self, b, *args) -> List[Index]:
        return perpendicular(
            b, self.index, self.color, *args, index_type=IndexType.DEFENDED
        )


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
        return p.is_defending_index(b, self.index)

    def get_possible_moves_index(self, board, player) -> List[Index]:
        """Getting possible moves for the king requires checking which indices
        the other player is attacking.
        """
        if player.color == self.color:
            raise ValueError("Need opposite player to verify checkness")
        out = perpendicular(board, self.index, self.color, max_depth=2)
        out.extend(diagonal(board, self.index, self.color, max_depth=2))
        return list(set(out) - set(player.get_defended_indices(board)))

    def get_defended_moves_index(self, board, player) -> List[Index]:
        if player.color == self.color:
            raise ValueError("Need opposite player to verify checkness")
        out = perpendicular(
            board,
            self.index,
            self.color,
            max_depth=2,
            index_type=IndexType.DEFENDED,
        )
        out.extend(
            diagonal(
                board,
                self.index,
                self.color,
                max_depth=2,
                index_type=IndexType.DEFENDED,
            )
        )
        return out


class Queen(Piece):
    def __str__(self) -> str:
        return "Q"

    def get_possible_moves_index(self, b) -> List[Index]:
        out = perpendicular(b, self.index, self.color)
        out.extend(diagonal(b, self.index, self.color))
        return out

    def get_defended_moves_index(self, b, *_args) -> List[Index]:
        out = perpendicular(
            b, self.index, self.color, index_type=IndexType.DEFENDED
        )
        out.extend(
            diagonal(b, self.index, self.color, index_type=IndexType.DEFENDED)
        )
        return out


# For type hints
AllPieces = Union[King, Queen, Rook, Rook, Bishop, Pawn, Piece]


class Board:
    def __init__(self, pieces: List):
        self.board: List[List]
        self.board = [[None for _ in range(8)] for _ in range(8)]
        for piece in pieces:
            self.init_piece(piece, piece.index)

    def init_piece(self, piece, index: Index):
        index_valid_or_raise(index)
        self.board[piece.index.x][piece.index.y] = piece

    def validate_pieces(self, pieces: List):
        if not isinstance(pieces, List):
            raise TypeError("Invalid type: {}".format(type(pieces)))

        for piece in pieces:
            if not isinstance(pieces, Piece):
                raise TypeError("Invalid type: {}".format(type(pieces)))

    def is_index_under_attack(self, player, index: Index):
        """Attacking indexes are ones which a king may not move into"""
        player.is_attacking_index(player, self, index)

    def is_defending_index(self, player, index: Index):
        """Defended indexes are ones which a king may not move into"""
        player.is_defending_index(player, self, index)

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
            ]:
                row.append(color(self.board[r][c]))
            rows.append(" ".join(row))
        return "\n".join(rows)

    def __str__(self) -> str:
        return self.to_string()


class Player:
    """Represents one side, used to track the location of pieces for iterating
    over, rather than iterating over the entire board
    """

    def __init__(self, color: Color, pieces: List):
        self.index_list: List[Index] = []
        self.color: Color = color
        for piece in pieces:
            if piece.color is not self.color:
                raise ValueError("Invalid piece color added to player")
            self.set_piece_index(piece.index)

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

    def get_defended_indices(self, b: Board) -> List[Index]:
        out = []
        for piece_index in self.index_list:
            piece_obj: Piece
            piece_obj = b.board[piece_index.x][piece_index.y]
            for move in piece_obj.get_defended_moves_index(b, self):
                out.append(move)
        return list(set(out))

    def get_defended_positions(self, b: Board) -> List[Position]:
        return [
            Position(Column(x), y + 1) for x, y in self.get_defended_indices(b)
        ]

    def print_defended_positions(self, b: Board) -> None:
        print("Defended Positions:")
        print("===================")
        pieces = []
        for piece in self.get_defended_positions(b):
            pieces.append(Piece(piece.x, piece.y, Color.BLACK))
        print(Board(pieces).prettify())

    def is_defending_index(self, b: Board, index: Index) -> bool:
        print(self.get_defended_indices(b))
        return index in self.get_defended_indices(b)

    def is_attacking_position(self, b: Board, x: Column, y: int) -> bool:
        return self.is_attacking_index(b, Index(int(x), y - 1))

    def is_defending_position(self, b: Board, x: Column, y: int) -> bool:
        print("checking for position [{}, {}]".format(x, y))
        return self.is_defending_index(b, Index(int(x), y - 1))

    def set_piece_index(self, index: Index):
        """TODO: ordering? LRU vs MRU"""
        self.index_list.append(index)

    def remove_piece_index(self, index: Index):
        """Remove index from list"""
        self.index_list.remove(index)

    def update_piece_index(self, piece: Piece, new_index: Index):
        self.remove_piece_index(piece.index)
        self.set_piece_index(new_index)
