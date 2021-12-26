import copy
import random
from enum import Enum, IntEnum
from typing import Union, List, Any, Tuple
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


def get_index_distance(i1: Index, i2: Index) -> Index:
    return Index(abs(i1.x - i2.x), abs(i1.y - i2.y))


def get_position_distance(i1: Position, i2: Position) -> Position:
    return Position(abs(i1.x - i2.x), abs(i1.y - i2.y))


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

    param index: coordinates in array
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

    value = None

    def __init__(self, x: Column, y: int, color: Color):
        self.index = position_to_index(Position(x, y))
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

    def get_position(self):
        return index_to_position(self.index)

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

    def get_possible_moves_position(
        self, b, player=None, other_player=None
    ) -> List[Position]:
        return [
            index_to_position(index)
            for index in self.get_possible_moves_index(
                b, player=player, other_player=other_player
            )
        ]

    def get_attacking_moves_position(self, b, *args) -> List[Position]:
        return [
            index_to_position(index)
            for index in self.get_attacking_moves_index(b, *args)
        ]


# TODO: en passante, promotion
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
        # defend
        if self.is_relative_index_valid(-1, y_direction):
            moves.append(Index(self.index.x - 1, self.index.y + y_direction))
        # defend
        if self.is_relative_index_valid(1, y_direction):
            moves.append(Index(self.index.x + 1, self.index.y + y_direction))
        return moves

    def get_possible_moves_index(
        self, b, player=None, other_player=None
    ) -> List[Index]:
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
    value = 3

    def __str__(self) -> str:
        return "♘" if self.color == Color.WHITE else "♞"

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

    def get_possible_moves_index(
        self, b, player=None, other_player=None
    ) -> List[Index]:
        out = []
        for index in self.get_potentials():
            if is_index_valid(index):
                value = get_index(b, index)
                if not value or self.color != value.color:
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
    value = 3

    def __str__(self) -> str:
        return "♗" if self.color == Color.WHITE else "♝"

    def get_possible_moves_index(
        self, b, player=None, other_player=None
    ) -> List[Index]:
        return diagonal(b, self.index, self.color)

    def get_defended_moves_index(self, b, *args) -> List[Index]:
        return diagonal(
            b, self.index, self.color, index_type=IndexType.DEFENDED
        )


class Rook(Piece):
    value = 5

    def __str__(self) -> str:
        return "♖" if self.color == Color.WHITE else "♜"

    def get_possible_moves_index(
        self, b, player=None, other_player=None
    ) -> List[Index]:
        return perpendicular(b, self.index, self.color)

    def get_defended_moves_index(self, b, *args) -> List[Index]:
        return perpendicular(
            b, self.index, self.color, index_type=IndexType.DEFENDED
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
        # TODO: implement this by checking player index rather than returning
        # objects?
        if other_player.color == self.color:
            raise ValueError("Need opposite player to verify checkness")
        out = perpendicular(board, self.index, self.color, max_depth=2)
        out.extend(diagonal(board, self.index, self.color, max_depth=2))
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
        out = perpendicular(board, self.index, self.color, max_depth=2)
        out.extend(diagonal(board, self.index, self.color, max_depth=2))

        # castle
        if not self.has_moved and not self.in_check(
            board, player, other_player
        ):
            if Color.WHITE == self.color:
                # KCastle
                k_rook = get_position(board, Position(Column.H, 1))

                # Check that kingside rook hasn't moved and squares are open
                # and not under attack
                positions = [Position(Column.F, 1), Position(Column.G, 1)]
                if k_rook and not k_rook.has_moved:
                    legal = True
                    for position in positions:
                        if get_position(
                            board, position
                        ) or other_player.is_attacking_position(
                            board, position, player
                        ):
                            legal = False
                            break

                    if not isinstance(k_rook, Rook):
                        raise ValueError("This shouldn't be possible")
                    if legal:
                        out.append(position_to_index(Position(Column.G, 1)))

                # QCastle
                q_rook = get_position(board, Position(Column.A, 1))

                positions = [Position(Column.C, 1), Position(Column.D, 1)]
                if q_rook and not q_rook.has_moved:
                    legal = True
                    for position in positions:
                        if get_position(
                            board, position
                        ) or other_player.is_attacking_position(
                            board, position, player
                        ):
                            legal = False
                            break

                    if not isinstance(q_rook, Rook):
                        raise ValueError("This shouldn't be possible")
                    if legal:
                        out.append(position_to_index(Position(Column.C, 1)))

            elif Color.BLACK == self.color:
                # KCastle
                k_rook = get_position(board, Position(Column.H, 8))
                q_rook = get_position(board, Position(Column.A, 8))

                # Check that kingside rook hasn't moved and squares are open
                # and not under attack
                positions = [Position(Column.F, 8), Position(Column.G, 8)]
                if k_rook and not k_rook.has_moved:
                    legal = True
                    for position in positions:
                        if get_position(
                            board, position
                        ) or other_player.is_attacking_position(
                            board, position, player
                        ):
                            legal = False
                            break

                    if not isinstance(k_rook, Rook):
                        raise ValueError("This shouldn't be possible")
                    if legal:
                        out.append(position_to_index(Position(Column.G, 8)))

                # QCastle
                positions = [Position(Column.C, 8), Position(Column.D, 8)]
                if q_rook and not q_rook.has_moved:
                    legal = True
                    for position in positions:
                        if get_position(
                            board, position
                        ) or other_player.is_attacking_position(
                            board, position, player
                        ):
                            legal = False
                            break

                    if not isinstance(q_rook, Rook):
                        raise ValueError("This shouldn't be possible")
                    if legal:
                        out.append(position_to_index(Position(Column.C, 8)))
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
    value = 9

    def __str__(self) -> str:
        return "♕" if self.color == Color.WHITE else "♛"

    def get_possible_moves_index(
        self, b, player=None, other_player=None
    ) -> List[Index]:
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
AllPieces = Union[King, Queen, Rook, Bishop, Pawn, Piece]


class Board:
    def __init__(self, pieces: List):

        self.board: List[List]
        self.board = [[None for _ in range(8)] for _ in range(8)]
        for piece in copy.deepcopy(pieces):
            self.init_piece(piece, piece.index)

    def init_piece(self, piece, index: Index):
        index_valid_or_raise(index)
        self.board[piece.index.x][piece.index.y] = piece

    def is_index_under_attack(self, player, index: Index, other_player):
        """Attacking indexes are ones which a king may not move into"""
        player.is_attacking_index(player, self, index, other_player)

    def is_defending_index(self, player, index: Index, other_player):
        """Defended indexes are ones which a king may not move into"""
        player.is_defending_index(self, index, other_player)

    def set_index(self, index: Index, piece: Piece) -> None:
        self.board[index.x][index.y] = piece

    def set_position(self, position: Position, piece: Piece) -> None:
        self.set_index(position_to_index(position), piece)

    def clear_index(self, index: Index) -> None:
        self.board[index.x][index.y] = None

    def clear_position(self, position: Position) -> None:
        self.clear_index(position_to_index(position))

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


piece_notation_to_class = {
    "K": King,
    "Q": Queen,
    "N": Knight,
    "B": Bishop,
    "R": Rook,
    "P": Pawn,
}

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


def positions_to_cmd(src_pos: Position, dst_pos: Position):
    return {
        "start": {
            "file": piece_column_to_str[src_pos.x],
            "rank": str(src_pos.y),
        },
        "end": {
            "file": piece_column_to_str[dst_pos.x],
            "rank": str(dst_pos.y),
        },
    }


def positions_to_uci_str(src_pos: Position, dst_pos: Position) -> str:
    return "{}{}{}{}".format(
        piece_column_to_str[src_pos.x],
        str(src_pos.y),
        piece_column_to_str[dst_pos.x],
        str(dst_pos.y),
    )


def cmd_to_position(cmd: dict):
    """Map command notation to position"""
    file = piece_str_to_column[cmd["file"]]
    return Position(file, int(cmd["rank"]))


class Player:
    """Represents one side, used to track the location of pieces for iterating
    over, rather than iterating over the entire board
    """

    def __init__(self, color: Color, pieces: List):
        # Seed randomness for move selection
        random.seed()
        self.index_list: List[Index] = []
        self.color: Color = color
        self.KCastle = True
        self.QCastle = True
        for piece in pieces:
            if piece.color is not self.color:
                raise ValueError("Invalid piece color added to player")
            self.set_piece_index(piece.index)
            # Save king coordinate
            if isinstance(piece, King):
                self.king_index = piece.index

    def get_best_move(self, board: Board, other_player) -> str:
        """Current strategy: random"""
        possible_moves = self.get_possible_moves_position(board, other_player)
        select = random.randrange(len(possible_moves))
        moves = possible_moves[select]
        return positions_to_uci_str(moves[0], moves[1])

    def get_possible_moves_index(
        self, b, other_player=None
    ) -> List[Tuple[Index, Index]]:
        """Iterate over all pieces and get a list of Tuples with (src, dst)
        positions
        """
        moves: List[Tuple[Index, Index]] = []

        for index in self.index_list:
            piece = b.board[index.x][index.y]
            piece_moves = piece.get_possible_moves_index(
                b, player=self, other_player=other_player
            )
            for piece in piece_moves:
                moves.append((index, piece))
        if not moves:
            raise ValueError("This means stalemate, but for now we raise")
        return moves

    def get_possible_moves_position(
        self, b, other_player=None
    ) -> List[Tuple[Position, Position]]:
        """Iterate over all pieces and get a list of Tuples with (src, dst)
        positions
        """
        positions = []
        for (start, end) in self.get_possible_moves_index(
            b, other_player=other_player
        ):
            positions.append(
                (index_to_position(start), index_to_position(end))
            )
        return positions

    def get_material(self, board: Board) -> int:
        score = 0
        for index in self.index_list:
            piece = get_index(board, index)
            if not piece:
                raise ValueError(
                    "Accounting error, no piece at position: {}".format(
                        index_to_position(index)
                    )
                )

            if piece.value:
                score += piece.value
        return score

    def get_score(self, board: Board) -> int:
        """Intended for player strategy"""
        return self.get_material(board)

    def is_attacking_index(self, b: Board, index: Index, other_player):
        for index in self.index_list:
            piece = b.board[index.x][index.y]
            for move in piece.get_attacking_moves_index(b, self, other_player):
                if index in move:
                    return True
        return False

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

    def get_defended_positions(self, b: Board, other_player) -> List[Position]:
        return [
            index_to_position(index)
            for index in self.get_defended_indices(b, other_player)
        ]

    def print_defended_positions(self, b: Board, other_player) -> None:
        print("Defended Positions:")
        print("===================")
        pieces = []
        for piece in self.get_defended_positions(b, other_player):
            pieces.append(Piece(piece.x, piece.y, Color.BLACK))
        print(Board(pieces).prettify())

    def is_defending_index(self, b: Board, index: Index, other_player) -> bool:
        if other_player.color == self.color:
            raise ValueError("Need opposite player to verify checkness")
        return index in self.get_defended_indices(b, other_player)

    def is_attacking_position(
        self, b: Board, position: Position, other_player
    ) -> bool:
        return self.is_attacking_index(
            b, position_to_index(position), other_player
        )

    def is_defending_position(
        self, b: Board, position: Position, other_player
    ) -> bool:
        return self.is_defending_index(
            b, position_to_index(position), other_player
        )

    def set_piece_index(self, index: Index):
        """TODO: ordering? LRU vs MRU"""
        self.index_list.append(index)

    def remove_piece_index(self, index: Index):
        """Remove index from list"""
        self.index_list.remove(index)

    def update_piece_index(self, piece: Piece, new_index: Index):
        self.remove_piece_index(piece.index)
        self.set_piece_index(new_index)

    def update_piece_position(self, piece: Piece, new_position: Position):
        return self.update_piece_index(piece, position_to_index(new_position))

    def _verify_do_move(
        self,
        move: dict,
        board: Board,
        other_player,
        dst_pos: Position,
        src_piece: Piece,
        dst_piece: Piece,
    ):
        start = move["start"]
        # Check that source piece exists
        if not src_piece:
            raise ValueError(
                "No piece at {}{}\n{}".format(
                    start["file"], start["rank"], board.prettify()
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
            raise ValueError(
                "Piece at {}{} is not {}".format(
                    start["file"], start["rank"], self.color
                )
            )

        # Get all moves the source piece can do
        moves = src_piece.get_possible_moves_position(
            board, player=self, other_player=other_player
        )

        # Check that requested destination is legal
        if dst_pos not in moves:
            raise ValueError(
                f"Requested move {dst_pos} for piece {src_piece} "
                f"is not in legal movelist: {moves}"
            )

        # Check that not moving to same color
        elif dst_piece is not None:
            if dst_piece.color is self.color:
                raise ValueError(
                    "Piece {} at {} is same color({}),"
                    " can't move there!".format(
                        dst_piece, dst_pos, dst_piece.color
                    )
                )

    def do_castle(
        self, board: Board, other_player, dst_pos: Position, rank: int
    ):
        """king move done, need to move the rook
        position rules are identical besides rank

        Mock user input and call do_move() without verification
        """
        if dst_pos == Position(Column.G, rank):
            self.do_move(
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
        elif dst_pos == Position(Column.C, rank):
            self.do_move(
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
            raise ValueError(f"Invalid castling destination: {dst_pos}")

    def do_move(self, move: dict, board: Board, other_player, verify=True):
        """Move piece and update accounting in board, players, and piece"""
        start = move["start"]
        end = move["end"]

        # Source position
        src_pos = cmd_to_position(start)

        # Destination position
        dst_pos = cmd_to_position(end)

        # Get piece at source position
        src_piece = get_position(board, src_pos)

        # Get piece at destination position
        dst_piece = get_position(board, dst_pos)

        # Skip move verification for castling - we already did that
        if verify:
            # Check for errors
            self._verify_do_move(
                move, board, other_player, dst_pos, src_piece, dst_piece
            )

        # Handle taking opponent's piece
        if dst_piece is not None:

            # Remove piece from other player's index
            other_player.remove_piece_index(position_to_index(dst_pos))

        # Pawn promotion
        if move["promote"]:
            old_src = src_piece
            src_piece = piece_notation_to_class[move["promote"].upper()](
                src_pos.x, src_pos.y, old_src.color
            )

            # Replace old piece
            board.set_position(src_pos, src_piece)

        # Update this player's accounting
        self.update_piece_position(src_piece, dst_pos)

        # Update piece accounting
        src_piece.move_to_position(dst_pos)

        # Set piece to new position
        board.set_position(dst_pos, src_piece)

        # Save king coordinate
        if isinstance(src_piece, King):
            self.king_index = position_to_index(dst_pos)
            distance = get_position_distance(src_pos, dst_pos)

            # Castling, do rook move too, legality checked already
            if distance.x > 1:
                if Color.WHITE == self.color:
                    self.do_castle(board, other_player, dst_pos, 1)
                elif Color.BLACK == self.color:
                    self.do_castle(board, other_player, dst_pos, 8)

        # Delete the old board position
        board.clear_position(src_pos)

    def move(self, move: dict, board: Board, other_player):
        self.do_move(move["move"], board, other_player)
