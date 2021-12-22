#!/usr/bin/env python3.10

from prompt import read_move
from components import (
    Color,
    Column,
    Board,
    Player,
    Rook,
    Bishop,
    Knight,
    King,
    Queen,
    Pawn,
)

DEFAULT_WHITE = [
    Rook(Column.A, 1, Color.WHITE),
    Knight(Column.B, 1, Color.WHITE),
    Bishop(Column.C, 1, Color.WHITE),
    Queen(Column.D, 1, Color.WHITE),
    King(Column.E, 1, Color.WHITE),
    Bishop(Column.F, 1, Color.WHITE),
    Knight(Column.G, 1, Color.WHITE),
    Rook(Column.H, 1, Color.WHITE),
    Pawn(Column.A, 2, Color.WHITE),
    Pawn(Column.B, 2, Color.WHITE),
    Pawn(Column.C, 2, Color.WHITE),
    Pawn(Column.D, 2, Color.WHITE),
    Pawn(Column.E, 2, Color.WHITE),
    Pawn(Column.F, 2, Color.WHITE),
    Pawn(Column.G, 2, Color.WHITE),
    Pawn(Column.H, 2, Color.WHITE),
]

DEFAULT_BLACK = [
    Rook(Column.A, 8, Color.BLACK),
    Knight(Column.B, 8, Color.BLACK),
    Bishop(Column.C, 8, Color.BLACK),
    Queen(Column.D, 8, Color.BLACK),
    King(Column.E, 8, Color.BLACK),
    Bishop(Column.F, 8, Color.BLACK),
    Knight(Column.G, 8, Color.BLACK),
    Rook(Column.H, 8, Color.BLACK),
    Pawn(Column.A, 7, Color.BLACK),
    Pawn(Column.B, 7, Color.BLACK),
    Pawn(Column.C, 7, Color.BLACK),
    Pawn(Column.D, 7, Color.BLACK),
    Pawn(Column.E, 7, Color.BLACK),
    Pawn(Column.F, 7, Color.BLACK),
    Pawn(Column.G, 7, Color.BLACK),
    Pawn(Column.H, 7, Color.BLACK),
]


class Chess:
    def __init__(
        self,
        get_white_move,
        get_black_move,
        white_position=DEFAULT_WHITE,
        black_position=DEFAULT_BLACK,
        color=None,
    ):
        """Chess game. Has a game loop for two players. Alternatively may be
        used as a chess engine to play against

        param get_white_move: callback function that retrieves white player
            move, if None, pychess will return best move it calculates
        param get_black_move: callback function that retrieves black player
            move, if None, pychess will return best move it calculates
        param white_position: white player starting position
        param black_position: white player starting position
        """
        board = black_position + white_position
        self.board: Board = Board(board)
        self.white: Player = Player(Color.WHITE, white_position)
        self.black: Player = Player(Color.BLACK, black_position)
        self.black_input = get_black_move
        self.white_input = get_white_move
        self.color = color
        print("init")

    def loop(self):
        """Game loop"""
        print("init")
        try:
            turn = Color.WHITE
            err_msg = ""
            while True:
                try:
                    print(
                        "{}'s Turn\tMaterial: {}/{}".format(
                            "White" if turn == Color.WHITE else "Black",
                            self.white.get_material(self.board),
                            self.black.get_material(self.board),
                        )
                    )
                    print(self.board.prettify())
                    print(err_msg)
                    err_msg = ""

                    if turn == Color.WHITE:
                        if self.white_input:
                            user_in = self.white_input()
                            self.white.move(user_in, self.board, self.black)
                        else:
                            best_move = self.white.get_best_move()
                            self.white.move(best_move, self.board, self.black)
                    elif turn == Color.BLACK:
                        user_in = self.black_input()
                        self.black.move(user_in, self.board, self.white)

                    # Switch turns
                    turn = Color.BLACK if turn == Color.WHITE else Color.WHITE
                except ValueError as e:
                    err_msg = e
        except KeyboardInterrupt:
            print()

    def get_best_move(self, opponent_move: dict) -> dict:
        # Update state with opponent's move
        if self.color == Color.WHITE:
            self.black.move(opponent_move, self.board, self.black)
            return self.black.get_best_move()
        elif self.color == Color.BLACK:
            self.white.move(opponent_move, self.board, self.white)
            return self.white.get_best_move()


if __name__ == "__main__":
    chess = Chess(read_move, read_move)
    chess.loop()
